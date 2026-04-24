"""Budget Guard — wraps CostTracker to gate LLM calls and track cache hits."""
from __future__ import annotations

import logging
import time
from typing import Callable, Awaitable

log = logging.getLogger(__name__)


class BudgetGuard:
    """Thin wrapper around CostTracker that gates LLM calls with rate limiting.

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
        min_gap_s: float = 10.0,
        max_calls_per_user: int = 3,
        user_window_s: float = 600.0,
    ) -> None:
        self._cost = cost_tracker
        self._broadcast = ws_broadcast
        self._min_gap_s = min_gap_s
        self._max_calls_per_user = max_calls_per_user
        self._user_window_s = user_window_s
        
        self._total_calls = 0
        self._total_idr = 0.0
        self._cache_hits = 0
        self._last_call_ts = 0.0
        self._per_user_calls: dict[str, list[float]] = {}

    def can_call(self, user: str = "") -> bool:
        """Return True if budget and rate limits allow an LLM call."""
        now = time.time()
        
        # Check budget
        if self._cost.is_over_budget():
            return False
        
        # Check global rate limit (min gap between any calls)
        if now - self._last_call_ts < self._min_gap_s:
            return False
        
        # Check per-user rate limit
        if user:
            recent = [t for t in self._per_user_calls.get(user, []) if now - t < self._user_window_s]
            if len(recent) >= self._max_calls_per_user:
                return False
        
        return True

    def record_call(self, tokens: int, idr: float, user: str = "") -> None:
        """Record a completed LLM call."""
        now = time.time()
        self._total_calls += 1
        self._total_idr += idr
        self._last_call_ts = now
        
        # Track per-user calls
        if user:
            if user not in self._per_user_calls:
                self._per_user_calls[user] = []
            self._per_user_calls[user].append(now)
            
            # Cleanup old entries
            cutoff = now - self._user_window_s
            self._per_user_calls[user] = [t for t in self._per_user_calls[user] if t >= cutoff]

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
            "last_call_ts": self._last_call_ts,
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
