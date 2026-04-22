"""Cartesia API key pool — sticky-until-error rotation across 5 keys."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass

log = logging.getLogger(__name__)

COOLDOWN_S = 24 * 3600  # 24 hours after quota error


@dataclass
class KeySlot:
    key: str
    exhausted_until: float = 0.0
    total_calls: int = 0
    total_errors: int = 0

    def preview(self) -> str:
        if len(self.key) < 12:
            return "****"
        return f"{self.key[:6]}...{self.key[-4:]}"


class CartesiaPool:
    def __init__(self, slots: list[KeySlot]) -> None:
        if not slots:
            raise RuntimeError("CartesiaPool needs at least 1 key")
        self.slots = slots
        self._active_idx = 0
        self._lock = asyncio.Lock()

    @classmethod
    def from_env(cls, env_var: str = "CARTESIA_API_KEYS") -> CartesiaPool:
        raw = os.getenv(env_var, "").strip()
        keys = [k.strip() for k in raw.split(",") if k.strip()]
        if not keys:
            raise RuntimeError(f"{env_var} is empty in .env — add comma-separated keys")
        log.info("Cartesia pool initialized with %d key(s)", len(keys))
        return cls(slots=[KeySlot(key=k) for k in keys])

    async def acquire(self) -> KeySlot:
        async with self._lock:
            now = time.time()
            for _ in range(len(self.slots)):
                slot = self.slots[self._active_idx]
                if slot.exhausted_until <= now:
                    slot.total_calls += 1
                    return slot
                self._active_idx = (self._active_idx + 1) % len(self.slots)
            soonest = min(self.slots, key=lambda s: s.exhausted_until)
            wait_s = int(max(0, soonest.exhausted_until - now))
            raise RuntimeError(
                f"All {len(self.slots)} Cartesia keys exhausted, next available in {wait_s}s"
            )

    async def mark_exhausted(self, slot: KeySlot) -> None:
        async with self._lock:
            slot.exhausted_until = time.time() + COOLDOWN_S
            slot.total_errors += 1
            self._active_idx = (self._active_idx + 1) % len(self.slots)
            log.warning(
                "Cartesia key %s marked exhausted 24h (errors=%d), rotating",
                slot.preview(), slot.total_errors,
            )

    def stats(self) -> list[dict]:
        now = time.time()
        return [
            {
                "key": s.preview(),
                "calls": s.total_calls,
                "errors": s.total_errors,
                "exhausted": s.exhausted_until > now,
                "cooldown_s": max(0, int(s.exhausted_until - now)),
            }
            for s in self.slots
        ]
