"""Tests for ReplyCache — P2 acceptance."""
from __future__ import annotations

import time

from banghack.core.orchestrator.reply_cache import ReplyCache


def test_hit_similar() -> None:
    """Exact match returns cached replies."""
    cache = ReplyCache(ttl_s=300, similarity_threshold=0.9)
    replies = ["Reply A", "Reply B", "Reply C"]
    cache.put("berapa harga paloma", "price_question", replies)
    result = cache.lookup("berapa harga paloma", "price_question")
    assert result == replies


def test_miss_different_intent() -> None:
    """Same text but different intent returns None."""
    cache = ReplyCache(ttl_s=300, similarity_threshold=0.9)
    replies = ["Reply A", "Reply B", "Reply C"]
    cache.put("halo semua", "greeting", replies)
    result = cache.lookup("halo semua", "price_question")
    assert result is None


def test_ttl() -> None:
    """Entries expire after TTL."""
    cache = ReplyCache(ttl_s=1, similarity_threshold=0.9)
    replies = ["Reply A", "Reply B", "Reply C"]
    cache.put("halo", "greeting", replies)
    assert cache.lookup("halo", "greeting") == replies
    time.sleep(1.1)
    assert cache.lookup("halo", "greeting") is None


def test_hit_rate() -> None:
    """hit_rate property returns correct ratio."""
    cache = ReplyCache(ttl_s=300, similarity_threshold=0.9)
    replies = ["A", "B", "C"]
    cache.put("test text", "greeting", replies)
    cache.lookup("test text", "greeting")  # hit
    cache.lookup("completely different xyz", "greeting")  # miss
    assert cache.hit_rate == 0.5


def test_clear() -> None:
    """clear() removes all entries."""
    cache = ReplyCache(ttl_s=300, similarity_threshold=0.9)
    cache.put("halo", "greeting", ["A", "B", "C"])
    cache.clear()
    assert cache.size == 0
    assert cache.lookup("halo", "greeting") is None
