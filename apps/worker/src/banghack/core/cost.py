"""Cost tracker — per-tier IDR estimation + daily budget cap.

P3: mutable tariff + set_budget via UI.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime

log = logging.getLogger(__name__)


@dataclass
class CostDay:
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    total_idr: float = 0.0
    llm_calls: int = 0
    tts_calls: int = 0
    by_tier: dict[str, float] = field(default_factory=dict)


class CostTracker:
    def __init__(self) -> None:
        self.budget_idr = float(os.getenv("BUDGET_IDR_DAILY", "5000"))
        self.usd_to_idr = int(os.getenv("USD_TO_IDR", "16200"))
        # Mutable tariff tables
        self.llm_cost_per_1k: dict[str, float] = {
            "ninerouter": 0.0,          # subscription via 9router
            "deepseek": 0.00028,        # Rp ~4.5 per 1K tokens
            "claude_haiku": 0.0008,     # Rp ~13 per 1K tokens
            "error": 0.0,
        }
        self.tts_cost_per_char: dict[str, float] = {
            "cartesia": 0.000030,       # Sonic-3 ~$30 per 1M char
            "edge_tts": 0.0,
            "error": 0.0,
        }
        self.day = CostDay()

    def set_budget(self, idr: float) -> None:
        """Set daily budget. Raises ValueError if out of range 0..10_000_000."""
        if idr < 0 or idr > 10_000_000:
            raise ValueError(f"budget out of range 0..10_000_000, got {idr}")
        self.budget_idr = float(idr)
        log.info("budget updated → Rp %.0f/day", self.budget_idr)

    def update_tariff(
        self,
        *,
        usd_to_idr: int | None = None,
        llm: dict[str, float] | None = None,
        tts: dict[str, float] | None = None,
    ) -> None:
        """Update tariff tables at runtime."""
        if usd_to_idr is not None:
            if usd_to_idr <= 0:
                raise ValueError("usd_to_idr must be positive")
            self.usd_to_idr = int(usd_to_idr)
        if isinstance(llm, dict):
            self.llm_cost_per_1k.update({k: float(v) for k, v in llm.items()})
        if isinstance(tts, dict):
            self.tts_cost_per_char.update({k: float(v) for k, v in tts.items()})
        log.info("tariff updated: usd_to_idr=%d", self.usd_to_idr)

    def _roll_day(self) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.day.date:
            log.info("cost: new day, resetting (was Rp %.0f)", self.day.total_idr)
            self.day = CostDay(date=today)

    def record_llm(self, tier: str, prompt_tokens: int, completion_tokens: int) -> float:
        self._roll_day()
        per_1k = self.llm_cost_per_1k.get(tier, 0.0)
        tokens = prompt_tokens + completion_tokens
        idr = (tokens / 1000) * per_1k * self.usd_to_idr
        self.day.total_idr += idr
        self.day.llm_calls += 1
        self.day.by_tier[f"llm_{tier}"] = self.day.by_tier.get(f"llm_{tier}", 0) + idr
        return idr

    def record_tts(self, engine: str, char_count: int) -> float:
        self._roll_day()
        per_char = self.tts_cost_per_char.get(engine, 0.0)
        idr = char_count * per_char * self.usd_to_idr
        self.day.total_idr += idr
        self.day.tts_calls += 1
        self.day.by_tier[f"tts_{engine}"] = self.day.by_tier.get(f"tts_{engine}", 0) + idr
        return idr

    def is_over_budget(self) -> bool:
        self._roll_day()
        return self.day.total_idr >= self.budget_idr

    def snapshot(self) -> dict:  # type: ignore[type-arg]
        self._roll_day()
        return {
            "date": self.day.date,
            "total_idr": round(self.day.total_idr, 2),
            "budget_idr": self.budget_idr,
            "budget_pct": round(
                (self.day.total_idr / self.budget_idr * 100) if self.budget_idr else 0,
                1,
            ),
            "llm_calls": self.day.llm_calls,
            "tts_calls": self.day.tts_calls,
            "by_tier": {k: round(v, 2) for k, v in self.day.by_tier.items()},
            "over_budget": self.is_over_budget(),
        }
