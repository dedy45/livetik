"""Guardrail — filter forbidden content + per-user rate limit + dedup.

P3: fully reconfigurable via update_config() — no restart needed.
"""
from __future__ import annotations

import logging
import os
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass

log = logging.getLogger(__name__)

DEFAULT_FORBIDDEN_PATTERNS = [
    r"https?://\S+",                                    # any URL
    r"(\d[\s-]?){8,}",                                  # phone / credit card
    r"\b(wa|whatsapp|telegram|tele)\b",
    r"\b(bokep|porn|xxx|sex|sange|ngewe)\b",
    r"\b(fuck|shit|bangsat|anjing\s+lu|goblok\s+lu)\b",
    r"\b(sara|agama\s+lu|kafir)\b",
    r"^[^a-zA-Z0-9]{0,3}$",                             # emoji/punct only
]


@dataclass(slots=True)
class GuardrailResult:
    accepted: bool
    reason: str = ""  # forbidden | too_short | too_long | rate_limit | dedup


class Guardrail:
    def __init__(self) -> None:
        self.forbidden: list[re.Pattern[str]] = [
            re.compile(p, re.I) for p in DEFAULT_FORBIDDEN_PATTERNS
        ]
        self.min_words = int(os.getenv("GUARDRAIL_MIN_WORDS", "2"))
        self.rate_max = int(os.getenv("GUARDRAIL_RATE_MAX", "3"))
        self.rate_window_s = int(os.getenv("GUARDRAIL_RATE_WINDOW_S", "60"))
        self.max_chars = int(os.getenv("GUARDRAIL_MAX_CHARS", "300"))
        self._user_history: dict[str, deque[float]] = defaultdict(deque)
        self._recent_hashes: deque[tuple[float, str]] = deque()

    def update_config(
        self,
        *,
        forbidden: list[str] | None = None,
        min_words: int | None = None,
        rate_max: int | None = None,
        rate_window_s: int | None = None,
        max_chars: int | None = None,
    ) -> None:
        """Atomic update — validates ALL regex compile sebelum replace.

        Raises:
            re.error: kalau regex invalid (original config tidak diubah).
        """
        if forbidden is not None:
            compiled = [re.compile(p, re.I) for p in forbidden]  # fail-fast
            self.forbidden = compiled
        if min_words is not None:
            self.min_words = max(1, int(min_words))
        if rate_max is not None:
            self.rate_max = max(1, int(rate_max))
        if rate_window_s is not None:
            self.rate_window_s = max(1, int(rate_window_s))
        if max_chars is not None:
            self.max_chars = max(10, int(max_chars))
        log.info(
            "guardrail config updated: min_words=%d rate=%d/%ds max_chars=%d patterns=%d",
            self.min_words, self.rate_max, self.rate_window_s, self.max_chars, len(self.forbidden),
        )

    def config_snapshot(self) -> dict:  # type: ignore[type-arg]
        return {
            "forbidden_patterns": [p.pattern for p in self.forbidden],
            "min_words": self.min_words,
            "rate_max": self.rate_max,
            "rate_window_s": self.rate_window_s,
            "max_chars": self.max_chars,
        }

    def check(self, user: str, text: str) -> GuardrailResult:
        text = (text or "").strip()
        # Length check
        if len(text) > self.max_chars:
            return GuardrailResult(accepted=False, reason="too_long")
        word_count = len(re.findall(r"\w+", text))
        if word_count < self.min_words:
            return GuardrailResult(accepted=False, reason="too_short")
        # Forbidden patterns
        for pat in self.forbidden:
            if pat.search(text):
                log.info("guardrail REJECT (forbidden) user=%s text=%r", user, text[:50])
                return GuardrailResult(accepted=False, reason="forbidden")
        # Rate limit per user
        now = time.time()
        hist = self._user_history[user]
        while hist and hist[0] < now - self.rate_window_s:
            hist.popleft()
        if len(hist) >= self.rate_max:
            return GuardrailResult(accepted=False, reason="rate_limit")
        # Dedup (same user + text within rate_window_s)
        key = f"{user}::{text[:50].lower()}"
        while self._recent_hashes and self._recent_hashes[0][0] < now - self.rate_window_s:
            self._recent_hashes.popleft()
        if any(h == key for _, h in self._recent_hashes):
            return GuardrailResult(accepted=False, reason="dedup")
        # Accept — record
        hist.append(now)
        self._recent_hashes.append((now, key))
        return GuardrailResult(accepted=True)
