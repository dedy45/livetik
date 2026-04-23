"""Tests for Suggester output guardrail — P2 acceptance."""
from __future__ import annotations

from banghack.core.orchestrator.suggester import _safe


def test_safe_strips_url() -> None:
    """URLs should be replaced with [...]."""
    reply = "Cek produk di https://bit.ly/paloma123 ya kak!"
    result = _safe(reply)
    assert "https://" not in result
    assert "[...]" in result


def test_safe_strips_phone_number() -> None:
    """Phone numbers (10+ digits) should be replaced with [...]."""
    reply = "Hubungi kami di 08123456789 untuk info lebih lanjut"
    result = _safe(reply)
    assert "08123456789" not in result
    assert "[...]" in result


def test_safe_strips_specific_price() -> None:
    """Specific prices (Rp XXXXX) should be replaced with [...]."""
    reply = "Harga PALOMA Smart Lock Rp 850.000 saja kak!"
    result = _safe(reply)
    assert "Rp 850.000" not in result
    assert "[...]" in result


def test_safe_passes_normal_reply() -> None:
    """Normal reply without unsafe content should pass through unchanged."""
    reply = "Terima kasih kak! Silakan cek keranjang belanja ya."
    result = _safe(reply)
    assert result == reply


def test_safe_strips_whatsapp_link() -> None:
    """WhatsApp links should be replaced with [...]."""
    reply = "Chat kita di wa.me/6281234567890 ya kak"
    result = _safe(reply)
    assert "wa.me" not in result
    assert "[...]" in result
