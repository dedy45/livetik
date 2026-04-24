"""Reply Cache — similarity-based cache for generated replies using rapidfuzz."""
from __future__ import annotations

import logging
import time

from rapidfuzz import fuzz

log = logging.getLogger(__name__)


def _similarity(a: str, b: str) -> float:
    """Compute similarity between two texts using rapidfuzz token_sort_ratio.
    
    Returns float 0.0-1.0 where 1.0 is identical.
    """
    if not a or not b:
        return 0.0
    return fuzz.token_sort_ratio(a.lower(), b.lower()) / 100.0


class ReplyCache:
    """Cache for generated replies, keyed by (text, intent) with similarity lookup."""

    def __init__(self, ttl_s: int = 300, similarity_threshold: float = 0.9) -> None:
        self._ttl_s = ttl_s
        self._threshold = similarity_threshold
        self._entries: list[tuple[str, str, list[str], float]] = []
        self._hits = 0
        self._misses = 0

    def put(self, text: str, intent: str, replies: list[str]) -> None:
        """Store replies for a (text, intent) pair."""
        self._evict_expired()
        self._entries.append((text, intent, replies, time.time()))

    def lookup(self, text: str, intent: str) -> list[str] | None:
        """Return cached replies if a similar (text, intent) exists, else None."""
        self._evict_expired()
        for cached_text, cached_intent, replies, _ in self._entries:
            if cached_intent != intent:
                continue
            sim = _similarity(text, cached_text)
            if sim >= self._threshold:
                self._hits += 1
                log.debug("reply_cache hit (sim=%.3f) for: %s", sim, text[:40])
                return replies
        self._misses += 1
        return None

    def clear(self) -> None:
        """Clear all cache entries."""
        self._entries.clear()
        self._hits = 0
        self._misses = 0

    def _evict_expired(self) -> None:
        cutoff = time.time() - self._ttl_s
        self._entries = [(t, i, r, ts) for t, i, r, ts in self._entries if ts >= cutoff]

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        return len(self._entries)
