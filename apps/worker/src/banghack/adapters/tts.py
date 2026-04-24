"""TTS adapter — Cartesia primary (5-key pool) + edge-tts id-ID fallback.

Output flow: synth bytes → temp file (WAV/MP3) → ffplay subprocess → VB-CABLE.
"""
from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import edge_tts

from .cartesia_pool import CartesiaPool, KeySlot

log = logging.getLogger(__name__)


@dataclass(slots=True)
class TTSResult:
    engine: str  # cartesia | edge_tts | error
    duration_s: float
    char_count: int
    key_preview: str = ""


class TTSAdapter:
    def __init__(self, pool: CartesiaPool) -> None:
        self.pool = pool
        self.voice_id = os.getenv("CARTESIA_VOICE_ID", "")
        self.model_id = os.getenv("CARTESIA_MODEL", "sonic-3")
        self.default_emotion = os.getenv("CARTESIA_DEFAULT_EMOTION", "neutral")
        self.edge_voice = os.getenv("EDGE_TTS_VOICE", "id-ID-ArdiNeural")
        self._play_lock = asyncio.Lock()
        if not self.voice_id:
            log.warning("CARTESIA_VOICE_ID not set — Cartesia will fail, will fall back to edge-tts")

    async def speak(self, text: str, emotion: str | None = None) -> TTSResult:
        """Synthesize then play (sequential, lock-protected).

        Args:
            text: Text to synthesize.
            emotion: Cartesia emotion — neutral | happy | sad | angry | dramatic | comedic.
                     If None, uses self.default_emotion (runtime mutable).
                     Ignored by edge-tts fallback.
        """
        text = text.strip()
        if not text:
            return TTSResult(engine="error", duration_s=0, char_count=0)
        # Kalau emotion None → pakai default_emotion (runtime mutable)
        use_emotion = emotion if emotion else self.default_emotion
        async with self._play_lock:
            # Try Cartesia first
            try:
                return await self._cartesia_speak(text, emotion=use_emotion)
            except Exception as e:
                log.warning("Cartesia failed (%s) → falling back to edge-tts", e)
            # Fallback: edge-tts
            try:
                return await self._edge_speak(text)
            except Exception as e:
                log.error("edge-tts also failed: %s", e)
                return TTSResult(engine="error", duration_s=0, char_count=len(text))

    # Valid Cartesia Sonic-3 emotions
    VALID_EMOTIONS = frozenset({"neutral", "happy", "sad", "angry", "dramatic", "comedic"})

    async def _cartesia_speak(self, text: str, emotion: str = "neutral") -> TTSResult:
        import time
        import httpx
        if not self.voice_id:
            raise RuntimeError("CARTESIA_VOICE_ID not set")
        slot: KeySlot = await self.pool.acquire()
        t0 = time.monotonic()
        # Normalise emotion — fall back to neutral if unknown
        safe_emotion = emotion if emotion in self.VALID_EMOTIONS else "neutral"
        try:
            # Use HTTP API directly (same as scripts/voice/tts_lib.py)
            payload = {
                "model_id": self.model_id,
                "transcript": text,
                "voice": {
                    "mode": "id",
                    "id": self.voice_id
                },
                "output_format": {
                    "container": "wav",
                    "encoding": "pcm_f32le",
                    "sample_rate": 44100
                },
                "language": "id",
                "speed": "normal",
                "generation_config": {
                    "speed": 0.98,
                    "volume": 1.14,
                    "emotion": safe_emotion
                }
            }
            
            headers = {
                "Cartesia-Version": "2026-03-01",
                "X-API-Key": slot.key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.cartesia.ai/tts/bytes",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")
                
                audio_bytes = response.content
        except Exception as e:
            # Distinguish quota/auth from transient errors
            msg = str(e).lower()
            if any(tok in msg for tok in ("429", "quota", "insufficient", "402", "unauthorized", "401")):
                await self.pool.mark_exhausted(slot)
            raise
        # Play
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        try:
            await self._play_file(tmp_path)
        finally:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass
        return TTSResult(
            engine="cartesia",
            duration_s=time.monotonic() - t0,
            char_count=len(text),
            key_preview=slot.preview(),
        )

    async def _edge_speak(self, text: str) -> TTSResult:
        import time
        t0 = time.monotonic()
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name
        try:
            communicate = edge_tts.Communicate(text, self.edge_voice)
            await communicate.save(tmp_path)
            await self._play_file(tmp_path)
        finally:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass
        return TTSResult(
            engine="edge_tts",
            duration_s=time.monotonic() - t0,
            char_count=len(text),
        )

    @staticmethod
    async def _play_file(path: str) -> None:
        """Play audio via ffplay (blocks until done)."""
        proc = await asyncio.create_subprocess_exec(
            "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
