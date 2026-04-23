"""Reply Cache — cosine similarity cache for generated replies."""
from __future__ import annotations

import logging
import time
from collections import Counter

log = logging.getLogger(__name__)


def _tokenize(text: str) -> list[str]:
    """Simple whitespace tokenizer, lowercase."""
    return text.lower().split()


def _cosine_similarity(a: str, b: str) -> float:
    """Compute cosine similarity between two texts using TF bag-of-words."""
    tokens_a = _tokenize(a)
    tokens_b = _tokenize(b)
    if not tokens_a or not tokens_b:
        return 0.0

    count_a = Counter(tokens_a)
    count_b = Counter(tokens_b)

    dot = sum(count_a[t] * count_b[t] for t in count_a if t in count_b)
    mag_a = sum(v * v for v in count_a.values()) ** 0.5
    mag_b = sum(v * v for v in count_b.values()) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)


class ReplyCache:
    """Cache for generated replies, keyed by (text, intent) with cosine similarity lookup."""

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
            sim = _cosine_similarity(text, cached_text)
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
