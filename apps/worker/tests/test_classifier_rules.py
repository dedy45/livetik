"""Tests for rules classifier — P1 acceptance."""
from __future__ import annotations

import pytest
from banghack.core.classifier.rules import classify, IntentResult


@pytest.mark.parametrize("text,expected_intent", [
    ("halo", "greeting"),
    ("hai semua", "greeting"),
    ("selamat malam", "greeting"),
    ("berapa harganya?", "price_question"),
    ("harga paloma berapa", "price_question"),
    ("masih ada stok?", "stock_question"),
    ("ready stok nggak", "stock_question"),
    ("mau beli yang paloma", "buying_intent"),
    ("cara order gimana", "buying_intent"),
    ("bisa buat pintu kontrakan?", "compatibility"),
    ("cocok untuk pintu kayu?", "compatibility"),
    ("cara pasang gimana", "how_to_use"),
    ("tutorial pakai dong", "how_to_use"),
    ("terlalu mahal", "objection"),
    ("kualitas gimana", "objection"),
    ("wa dong", "forbidden_contact"),
    ("hubungi wa aja", "forbidden_contact"),
    ("cek https://bit.ly/x", "forbidden_link"),
    ("", "empty"),
])
def test_classify_intent(text: str, expected_intent: str) -> None:
    result = classify(text)
    assert result.name == expected_intent, (
        f"text={text!r}: expected {expected_intent!r}, got {result.name!r} "
        f"(confidence={result.confidence}, reason={result.reason})"
    )


def test_confidence_bounds() -> None:
    """Confidence must always be 0.0–1.0."""
    for text in ["halo", "berapa harga", "wa dong", "", "random text xyz"]:
        result = classify(text)
        assert 0.0 <= result.confidence <= 1.0, f"confidence out of bounds for {text!r}: {result.confidence}"


def test_forbidden_safe_to_skip() -> None:
    """Forbidden intents must have safe_to_skip=True and needs_llm=False."""
    for text in ["wa dong", "cek https://bit.ly/x", "hubungi wa"]:
        result = classify(text)
        assert result.safe_to_skip, f"expected safe_to_skip for {text!r}"
        assert not result.needs_llm, f"expected needs_llm=False for {text!r}"


def test_high_confidence_no_llm() -> None:
    """High confidence results should not need LLM."""
    result = classify("halo")
    assert result.confidence >= 0.8
    assert not result.needs_llm
