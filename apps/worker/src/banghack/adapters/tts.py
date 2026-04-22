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
from cartesia import AsyncCartesia

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
        self.model_id = os.getenv("CARTESIA_MODEL", "sonic-2")
        self.edge_voice = os.getenv("EDGE_TTS_VOICE", "id-ID-ArdiNeural")
        self._play_lock = asyncio.Lock()
        if not self.voice_id:
            log.warning("CARTESIA_VOICE_ID not set — Cartesia will fail, will fall back to edge-tts")

    async def speak(self, text: str) -> TTSResult:
        """Synthesize then play (sequential, lock-protected)."""
        text = text.strip()
        if not text:
            return TTSResult(engine="error", duration_s=0, char_count=0)
        async with self._play_lock:
            # Try Cartesia first
            try:
                return await self._cartesia_speak(text)
            except Exception as e:
                log.warning("Cartesia failed (%s) → falling back to edge-tts", e)
            # Fallback: edge-tts
            try:
                return await self._edge_speak(text)
            except Exception as e:
                log.error("edge-tts also failed: %s", e)
                return TTSResult(engine="error", duration_s=0, char_count=len(text))

    async def _cartesia_speak(self, text: str) -> TTSResult:
        import time
        if not self.voice_id:
            raise RuntimeError("CARTESIA_VOICE_ID not set")
        slot: KeySlot = await self.pool.acquire()
        t0 = time.monotonic()
        try:
            async with AsyncCartesia(api_key=slot.key) as client:
                audio_bytes = b""
                async for chunk in client.tts.bytes(
                    model_id=self.model_id,
                    transcript=text,
                    voice={"mode": "id", "id": self.voice_id},
                    language="id",
                    output_format={
                        "container": "wav",
                        "encoding": "pcm_s16le",
                        "sample_rate": 22050,
                    },
                ):
                    audio_bytes += chunk
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
