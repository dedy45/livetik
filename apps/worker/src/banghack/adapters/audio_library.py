"""Audio Library Adapter -- playback via sounddevice to virtual cable."""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Awaitable

if TYPE_CHECKING:
    from banghack.core.audio_library.manager import AudioLibraryManager

log = logging.getLogger(__name__)


def _resolve_output_device() -> int | None:
    """Resolve audio output device from env vars.
    
    Returns device index or None for system default.
    Priority: AUDIO_OUTPUT_DEVICE_INDEX > AUDIO_OUTPUT_DEVICE (name match) > None
    """
    import sounddevice as sd  # type: ignore
    
    # Try explicit index first
    idx_env = os.getenv("AUDIO_OUTPUT_DEVICE_INDEX", "").strip()
    if idx_env.isdigit():
        idx = int(idx_env)
        log.info("audio_library: using device index %d from AUDIO_OUTPUT_DEVICE_INDEX", idx)
        return idx
    
    # Try name match
    name_env = os.getenv("AUDIO_OUTPUT_DEVICE", "").strip()
    if not name_env:
        log.info("audio_library: no AUDIO_OUTPUT_DEVICE set, using system default")
        return None
    
    # Search for device by name (case-insensitive substring match)
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d.get("max_output_channels", 0) > 0:
            device_name = d.get("name", "").lower()
            if name_env.lower() in device_name:
                log.info("audio_library: matched device %d: %s", i, d.get("name"))
                return i
    
    log.warning("audio_library: device '%s' not found, using system default", name_env)
    return None


class AudioLibraryAdapter:
    def __init__(
        self,
        manager: "AudioLibraryManager",
        ws_broadcast: Callable[[dict], Awaitable[None]],
    ) -> None:
        self._manager = manager
        self._broadcast = ws_broadcast
        self._playing = False
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._current_clip_id: str | None = None
        self._stop_event = asyncio.Event()

    async def play(self, clip_id: str) -> None:
        """Queue a clip for playback."""
        await self._queue.put(clip_id)
        if not self._playing:
            asyncio.create_task(self._process_queue())

    async def stop(self) -> None:
        """Stop current playback immediately."""
        import sounddevice as sd  # type: ignore
        self._stop_event.set()
        sd.stop()  # Force stop current playback immediately

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def current_clip_id(self) -> str | None:
        return self._current_clip_id

    async def _process_queue(self) -> None:
        """Drain queue, play each clip via sounddevice."""
        self._playing = True
        try:
            while not self._queue.empty():
                if self._stop_event.is_set():
                    self._stop_event.clear()
                    # Drain remaining queue
                    while not self._queue.empty():
                        try:
                            self._queue.get_nowait()
                        except asyncio.QueueEmpty:
                            break
                    break
                clip_id = await self._queue.get()
                await self._play_clip(clip_id)
        finally:
            self._playing = False
            self._current_clip_id = None

    async def _play_clip(self, clip_id: str) -> None:
        """Load and play a clip via sounddevice."""
        import sounddevice as sd  # type: ignore
        import soundfile as sf  # type: ignore

        clip = self._manager.get(clip_id)
        if clip is None:
            log.warning("clip not found: %s", clip_id)
            await self._broadcast({"type": "error.audio_playback", "clip_id": clip_id, "detail": f"clip not found: {clip_id}"})
            return

        self._current_clip_id = clip_id
        try:
            data, samplerate = sf.read(clip.file_path, dtype="float32")
            await self._broadcast({
                "type": "audio.now",
                "clip_id": clip_id,
                "script_preview": clip.script[:80],
                "duration_ms": clip.duration_ms,
            })
            # Resolve output device from env
            device = _resolve_output_device()
            sd.play(data, samplerate, device=device)
            # Run blocking wait in executor with 30s timeout
            loop = asyncio.get_event_loop()
            try:
                await asyncio.wait_for(
                    loop.run_in_executor(None, sd.wait),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                log.error("audio playback timeout for %s (>30s)", clip_id)
                sd.stop()
                await self._broadcast({
                    "type": "error.audio_playback",
                    "clip_id": clip_id,
                    "detail": "playback timeout (>30s)",
                })
                return
            self._manager.mark_played(clip_id)
            await self._broadcast({"type": "audio.done", "clip_id": clip_id})
        except Exception as exc:
            log.error("audio playback error for %s: %s", clip_id, exc)
            await self._broadcast({
                "type": "error.audio_playback",
                "clip_id": clip_id,
                "detail": str(exc),
            })
        finally:
            self._current_clip_id = None
