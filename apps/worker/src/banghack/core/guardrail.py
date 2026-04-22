"""Guardrail — filter forbidden content + per-user rate limit + dedup."""
from __future__ import annotations

import logging
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass

log = logging.getLogger(__name__)

# Patterns that should never be replied to (likely spam, phishing, sensitive)
FORBIDDEN_PATTERNS = [
    re.compile(r"https?://\S+", re.I),          # any URL
    re.compile(r"(\d[\s-]?){8,}"),                # phone / credit card
    re.compile(r"\b(wa|whatsapp|telegram|tele)\b", re.I),
    re.compile(r"\b(bokep|porn|xxx|sex|sange|ngewe)\b", re.I),
    re.compile(r"\b(fuck|shit|bangsat|anjing\s+lu|goblok\s+lu)\b", re.I),
    re.compile(r"\b(sara|agama\s+lu|kafir)\b", re.I),
    re.compile(r"^[^a-zA-Z0-9]{0,3}$"),          # emoji/punct only
]

MIN_WORDS = 2       # skip "hi", "a"
MAX_CHARS = 300
RATE_LIMIT_WINDOW_S = 60
RATE_LIMIT_MAX = 3  # max 3 replies per user per 60s
DEDUP_WINDOW_S = 60


@dataclass(slots=True)
class GuardrailResult:
    accepted: bool
    reason: str = ""  # forbidden | too_short | too_long | rate_limit | dedup


class Guardrail:
    def __init__(self) -> None:
        self._user_history: dict[str, deque[float]] = defaultdict(deque)
        self._recent_hashes: deque[tuple[float, str]] = deque()

    def check(self, user: str, text: str) -> GuardrailResult:
        text = (text or "").strip()
        # Length check
        if len(text) > MAX_CHARS:
            return GuardrailResult(accepted=False, reason="too_long")
        word_count = len(re.findall(r"\w+", text))
        if word_count < MIN_WORDS:
            return GuardrailResult(accepted=False, reason="too_short")
        # Forbidden patterns
        for pat in FORBIDDEN_PATTERNS:
            if pat.search(text):
                log.info("guardrail REJECT (forbidden) user=%s text=%r", user, text[:50])
                return GuardrailResult(accepted=False, reason="forbidden")
        # Rate limit per user
        now = time.time()
        hist = self._user_history[user]
        while hist and hist[0] < now - RATE_LIMIT_WINDOW_S:
            hist.popleft()
        if len(hist) >= RATE_LIMIT_MAX:
            return GuardrailResult(accepted=False, reason="rate_limit")
        # Dedup (same user + text within DEDUP_WINDOW_S)
        key = f"{user}::{text[:50].lower()}"
        while self._recent_hashes and self._recent_hashes[0][0] < now - DEDUP_WINDOW_S:
            self._recent_hashes.popleft()
        if any(h == key for _, h in self._recent_hashes):
            return GuardrailResult(accepted=False, reason="dedup")
        # Accept — record
        hist.append(now)
        self._recent_hashes.append((now, key))
        return GuardrailResult(accepted=True)
