"""Budget Guard — wraps CostTracker to gate LLM calls and track cache hits."""
from __future__ import annotations

import logging
import time
from typing import Callable, Awaitable

log = logging.getLogger(__name__)


class BudgetGuard:
    """Thin wrapper around CostTracker that gates LLM calls.

    Usage:
        guard = BudgetGuard(cost_tracker, ws_broadcast)
        if guard.can_call():
            result = await llm.reply(...)
            guard.record_call(tokens, idr)
        else:
            # use template fallback
    """

    def __init__(
        self,
        cost_tracker: "CostTracker",  # type: ignore[name-defined]
        ws_broadcast: Callable[[dict], Awaitable[None]] | None = None,
    ) -> None:
        self._cost = cost_tracker
        self._broadcast = ws_broadcast
        self._total_calls = 0
        self._total_idr = 0.0
        self._cache_hits = 0

    def can_call(self) -> bool:
        """Return True if budget allows an LLM call."""
        return not self._cost.is_over_budget()

    def record_call(self, tokens: int, idr: float) -> None:
        """Record a completed LLM call."""
        self._total_calls += 1
        self._total_idr += idr

    def record_cache_hit(self) -> None:
        """Record a cache hit (no LLM call made)."""
        self._cache_hits += 1

    def snapshot(self) -> dict:  # type: ignore[type-arg]
        """Return current budget snapshot."""
        cost_snap = self._cost.snapshot()
        return {
            "total_calls": self._total_calls,
            "total_idr": round(self._total_idr, 2),
            "budget_idr": cost_snap["budget_idr"],
            "remaining_idr": round(cost_snap["budget_idr"] - cost_snap["total_idr"], 2),
            "cache_hits": self._cache_hits,
            "over_budget": cost_snap["over_budget"],
        }

    async def emit_blocked(self, reason: str = "budget_exceeded") -> None:
        """Emit guardrail.blocked event via WS."""
        if self._broadcast:
            await self._broadcast({
                "type": "guardrail.blocked",
                "ts": time.time(),
                "reason": reason,
                "snapshot": self.snapshot(),
            })
            log.warning("guardrail.blocked: %s", reason)
