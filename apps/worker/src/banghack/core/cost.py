"""Cost tracker — per-tier IDR estimation + daily budget cap."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime

log = logging.getLogger(__name__)

# Konversi kasar Apr 2026 (update kalau rate berubah signifikan)
USD_TO_IDR = 16_200

# Cost per 1K tokens (input + output averaged) per tier, in USD
LLM_COST_PER_1K_USD = {
    "ninerouter": 0.0,          # subscription via 9router
    "deepseek": 0.00028,        # Rp ~4.5 per 1K tokens
    "claude_haiku": 0.0008,     # Rp ~13 per 1K tokens
    "error": 0.0,
}

# Cost per char for TTS, USD
TTS_COST_PER_CHAR_USD = {
    "cartesia": 0.000030,       # Sonic-2 ~$30 per 1M char
    "edge_tts": 0.0,
    "error": 0.0,
}


@dataclass
class CostDay:
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    total_idr: float = 0.0
    llm_calls: int = 0
    tts_calls: int = 0
    by_tier: dict[str, float] = field(default_factory=dict)


class CostTracker:
    def __init__(self) -> None:
        self.budget_idr_daily = float(os.getenv("BUDGET_IDR_DAILY", "5000"))
        self.day = CostDay()

    def _roll_day(self) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.day.date:
            log.info("cost: new day, resetting (was Rp %.0f)", self.day.total_idr)
            self.day = CostDay(date=today)

    def record_llm(self, tier: str, prompt_tokens: int, completion_tokens: int) -> float:
        self._roll_day()
        per_1k = LLM_COST_PER_1K_USD.get(tier, 0.0)
        tokens = prompt_tokens + completion_tokens
        idr = (tokens / 1000) * per_1k * USD_TO_IDR
        self.day.total_idr += idr
        self.day.llm_calls += 1
        self.day.by_tier[f"llm_{tier}"] = self.day.by_tier.get(f"llm_{tier}", 0) + idr
        return idr

    def record_tts(self, engine: str, char_count: int) -> float:
        self._roll_day()
        per_char = TTS_COST_PER_CHAR_USD.get(engine, 0.0)
        idr = char_count * per_char * USD_TO_IDR
        self.day.total_idr += idr
        self.day.tts_calls += 1
        self.day.by_tier[f"tts_{engine}"] = self.day.by_tier.get(f"tts_{engine}", 0) + idr
        return idr

    def is_over_budget(self) -> bool:
        self._roll_day()
        return self.day.total_idr >= self.budget_idr_daily

    def snapshot(self) -> dict:
        self._roll_day()
        return {
            "date": self.day.date,
            "total_idr": round(self.day.total_idr, 2),
            "budget_idr": self.budget_idr_daily,
            "budget_pct": round(
                (self.day.total_idr / self.budget_idr_daily * 100) if self.budget_idr_daily else 0,
                1,
            ),
            "llm_calls": self.day.llm_calls,
            "tts_calls": self.day.tts_calls,
            "by_tier": {k: round(v, 2) for k, v in self.day.by_tier.items()},
            "over_budget": self.is_over_budget(),
        }
