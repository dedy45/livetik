"""Live Director — state machine for 2-hour TikTok Live sessions."""
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Awaitable, TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from banghack.core.audio_library.manager import AudioLibraryManager
    from banghack.adapters.audio_library import AudioLibraryAdapter

log = logging.getLogger(__name__)


class LiveMode(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


@dataclass
class RunsheetPhase:
    phase: str
    duration_s: int
    product: str | None
    clip_category: str
    obs_scene: str


@dataclass
class DirectorState:
    mode: LiveMode = LiveMode.IDLE
    phase_idx: int = 0
    phase_start_ts: float = 0.0
    session_start_ts: float = 0.0
    total_decisions: int = 0
    current_product: str = ""
    current_phase: str = ""


class LiveDirector:
    """State machine orchestrating 2-hour live sessions."""

    def __init__(
        self,
        products_yaml: Path,
        audio_manager: "AudioLibraryManager",
        audio_adapter: "AudioLibraryAdapter",
        ws_broadcast: Callable[[dict], Awaitable[None]],
        max_duration_s: int = 7200,
    ) -> None:
        self._products_yaml = products_yaml
        self._audio_manager = audio_manager
        self._audio_adapter = audio_adapter
        self._broadcast = ws_broadcast
        self._max_duration_s = max_duration_s
        self._state = DirectorState()
        self._runsheet: list[RunsheetPhase] = []
        self._run_task: asyncio.Task | None = None  # type: ignore[type-arg]
        self._tick_task: asyncio.Task | None = None  # type: ignore[type-arg]
        self._load_config()

    def _load_config(self) -> None:
        try:
            with self._products_yaml.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self._runsheet = [
                RunsheetPhase(
                    phase=p["phase"],
                    duration_s=int(p["duration_s"]),
                    product=p.get("product"),
                    clip_category=p["clip_category"],
                    obs_scene=p.get("obs_scene", ""),
                )
                for p in data.get("runsheet", [])
            ]
            log.info("director: loaded %d runsheet phases", len(self._runsheet))
        except Exception as exc:
            log.error("director: failed to load products.yaml: %s", exc)
            self._runsheet = []

    async def start(self) -> None:
        if self._state.mode == LiveMode.RUNNING:
            log.warning("director: already running")
            return
        self._state = DirectorState(
            mode=LiveMode.RUNNING,
            phase_idx=0,
            phase_start_ts=time.time(),
            session_start_ts=time.time(),
        )
        log.info("director: starting session (max %ds)", self._max_duration_s)
        self._run_task = asyncio.create_task(self._run_loop(), name="director_run")
        self._tick_task = asyncio.create_task(self._tick_loop(), name="director_tick")
        await self._broadcast_state("session_started")

    async def stop(self, reason: str = "manual") -> None:
        await self._do_stop(reason)

    async def pause(self) -> None:
        if self._state.mode == LiveMode.RUNNING:
            self._state.mode = LiveMode.PAUSED
            await self._broadcast_state("paused")

    async def resume(self) -> None:
        if self._state.mode == LiveMode.PAUSED:
            self._state.mode = LiveMode.RUNNING
            await self._broadcast_state("resumed")

    async def emergency_stop(self, operator_id: str = "operator") -> None:
        await self._audio_adapter.stop()
        await self._do_stop("emergency_stop")
        await self._broadcast({
            "type": "director.emergency_stopped",
            "ts": time.time(),
            "operator_id": operator_id,
            "elapsed_s": self.elapsed_s,
        })

    async def _do_stop(self, reason: str) -> None:
        self._state.mode = LiveMode.STOPPED
        if self._run_task and not self._run_task.done():
            self._run_task.cancel()
        if self._tick_task and not self._tick_task.done():
            self._tick_task.cancel()
        await self._broadcast({
            "type": "director.stopped",
            "ts": time.time(),
            "reason": reason,
            "elapsed_s": self.elapsed_s,
            "total_decisions": self._state.total_decisions,
        })
        log.info("director: stopped (reason=%s, elapsed=%.0fs)", reason, self.elapsed_s)

    async def _run_loop(self) -> None:
        """Main runsheet loop — iterate phases, play clips, advance."""
        if not self._runsheet:
            log.warning("director: empty runsheet, stopping")
            await self._do_stop("empty_runsheet")
            return

        phase_idx = 0
        while self._state.mode in (LiveMode.RUNNING, LiveMode.PAUSED):
            if self.elapsed_s >= self._max_duration_s:
                log.info("director: hard stop at max_duration_s=%d", self._max_duration_s)
                await self._do_stop("max_duration_reached")
                return

            if self._state.mode == LiveMode.PAUSED:
                await asyncio.sleep(1)
                continue

            phase = self._runsheet[phase_idx % len(self._runsheet)]
            self._state.phase_idx = phase_idx % len(self._runsheet)
            self._state.current_phase = phase.phase
            self._state.current_product = phase.product or ""
            self._state.phase_start_ts = time.time()
            self._state.total_decisions += 1

            await self._broadcast_state(f"phase:{phase.phase}")

            # Play clips continuously during this phase
            elapsed_in_phase = 0
            next_clip_at = 0
            
            while elapsed_in_phase < phase.duration_s:
                if self._state.mode == LiveMode.STOPPED:
                    return
                if self.elapsed_s >= self._max_duration_s:
                    await self._do_stop("max_duration_reached")
                    return
                
                # Play a new clip if it's time and we're running
                if elapsed_in_phase >= next_clip_at and self._state.mode == LiveMode.RUNNING:
                    clips = self._audio_manager.by_category(phase.clip_category)
                    not_played = self._audio_manager.not_played_since(window_s=600)
                    not_played_ids = {c.id for c in not_played}
                    candidates = [c for c in clips if c.id in not_played_ids] or clips
                    
                    if candidates:
                        clip = random.choice(candidates)
                        asyncio.create_task(self._audio_adapter.play(clip.id))
                        # Schedule next clip: clip duration + 5 second gap
                        clip_duration_s = max(15, clip.duration_ms // 1000)
                        next_clip_at = elapsed_in_phase + clip_duration_s + 5
                
                await asyncio.sleep(1)
                if self._state.mode != LiveMode.PAUSED:
                    elapsed_in_phase += 1

            phase_idx += 1

    async def _tick_loop(self) -> None:
        """Emit live.tick every 30 seconds."""
        while self._state.mode in (LiveMode.RUNNING, LiveMode.PAUSED):
            await asyncio.sleep(30)
            if self._state.mode == LiveMode.STOPPED:
                break
            remaining = max(0, self._max_duration_s - self.elapsed_s)
            await self._broadcast({
                "type": "live.tick",
                "ts": time.time(),
                "elapsed_s": round(self.elapsed_s),
                "remaining_s": round(remaining),
                "mode": self._state.mode.value,
                "phase": self._state.current_phase,
                "product": self._state.current_product,
            })
            if remaining <= 600 and remaining > 570:
                await self._broadcast({
                    "type": "director.warning",
                    "ts": time.time(),
                    "remaining_s": round(remaining),
                    "message": "10 menit tersisa!",
                })

    async def _broadcast_state(self, reason: str) -> None:
        remaining = max(0, self._max_duration_s - self.elapsed_s)
        await self._broadcast({
            "type": "live.state",
            "ts": time.time(),
            "mode": self._state.mode.value,
            "phase": self._state.current_phase,
            "phase_idx": self._state.phase_idx,
            "phase_total": len(self._runsheet),
            "product": self._state.current_product,
            "elapsed_s": round(self.elapsed_s),
            "remaining_s": round(remaining),
            "reason": reason,
        })

    def get_state(self) -> dict:  # type: ignore[type-arg]
        remaining = max(0, self._max_duration_s - self.elapsed_s)
        return {
            "mode": self._state.mode.value,
            "phase": self._state.current_phase,
            "phase_idx": self._state.phase_idx,
            "phase_total": len(self._runsheet),
            "product": self._state.current_product,
            "elapsed_s": round(self.elapsed_s),
            "remaining_s": round(remaining),
            "total_decisions": self._state.total_decisions,
        }

    @property
    def elapsed_s(self) -> float:
        if self._state.session_start_ts == 0:
            return 0.0
        return time.time() - self._state.session_start_ts

    @property
    def remaining_s(self) -> float:
        return max(0.0, self._max_duration_s - self.elapsed_s)

    @property
    def current_product(self) -> str:
        return self._state.current_product

    @property
    def is_ready(self) -> bool:
        return len(self._runsheet) > 0

    @property
    def mode(self) -> LiveMode:
        return self._state.mode
