"""Rule-first comment classifier — 7+ intents, regex + keyword dict, Bahasa Indonesia."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class IntentResult:
    name: str          # intent name
    confidence: float  # 0.0–1.0
    reason: str        # human-readable reason
    needs_llm: bool    # True if confidence < threshold
    safe_to_skip: bool # True for spam/forbidden — don't send to LLM


# Intent definitions: (name, keywords, patterns, weight, safe_to_skip)
_INTENTS = [
    # Forbidden — must be detected first, safe_to_skip=True
    (
        "forbidden_contact",
        ["wa", "whatsapp", "telegram", "ig", "instagram", "line", "dm", "pm"],
        [r"wa\.me", r"t\.me", r"wa\s*:\s*\d", r"hubungi\s+wa", r"chat\s+wa"],
        1.0, True,
    ),
    (
        "forbidden_link",
        [],
        [r"https?://", r"bit\.ly", r"tinyurl", r"linktr\.ee", r"linktree"],
        1.0, True,
    ),
    (
        "spam",
        ["follow", "subscribe", "sub4sub", "f4f", "like4like"],
        [r"\d{10,}", r"@\w{5,}"],
        0.9, True,
    ),
    # Normal intents
    (
        "greeting",
        ["halo", "hai", "hi", "hey", "selamat", "mampir", "hadir", "join", "masuk", "assalamualaikum", "permisi"],
        [r"^halo\b", r"^hai\b", r"^hi\b", r"^hey\b", r"selamat\s+(pagi|siang|sore|malam)"],
        1.0, False,
    ),
    (
        "price_question",
        ["harga", "berapa", "murah", "mahal", "diskon", "promo", "harganya", "cost", "price"],
        [r"harga\s*\?", r"berapa\s+harga", r"berapa\s+nih", r"harganya\s+berapa"],
        1.0, False,
    ),
    (
        "stock_question",
        ["stok", "stock", "ready", "ada", "tersedia", "habis", "kosong", "masih"],
        [r"masih\s+ada", r"ready\s+stok", r"stok\s+ada", r"ada\s+stok", r"masih\s+ready"],
        1.0, False,
    ),
    (
        "buying_intent",
        ["beli", "order", "pesan", "mau", "minta", "checkout", "bayar", r"bisa\s+beli"],
        [r"mau\s+beli", r"mau\s+order", r"cara\s+beli", r"cara\s+order", r"gimana\s+beli"],
        1.0, False,
    ),
    (
        "compatibility",
        ["bisa", "cocok", "kompatibel", "sesuai", "pas", "fit", "support"],
        [r"bisa\s+buat", r"bisa\s+untuk", r"cocok\s+untuk", r"bisa\s+dipasang", r"kompatibel\s+dengan"],
        0.9, False,
    ),
    (
        "how_to_use",
        ["cara", "pasang", "install", "pakai", "gunakan", "tutorial", "panduan", "langkah"],
        [r"cara\s+pasang", r"cara\s+pakai", r"cara\s+install", r"gimana\s+cara", r"bagaimana\s+cara"],
        0.9, False,
    ),
    (
        "objection",
        ["mahal", "kemahalan", "kualitas", "jelek", "bagus", "worth", "worth it", "rugi", "kecewa"],
        [r"terlalu\s+mahal", r"kualitas\s+gimana", r"worth\s+it\s+nggak", r"bagus\s+nggak"],
        0.9, False,
    ),
    (
        "empty",
        [],
        [],
        1.0, True,
    ),
]

_THRESHOLD = 0.8


def classify(text: str) -> IntentResult:
    """Classify a comment text into an intent.

    Returns IntentResult with confidence 0.0–1.0.
    needs_llm=True if confidence < _THRESHOLD and not safe_to_skip.
    """
    text = text.strip()

    # Empty check
    if not text:
        return IntentResult(name="empty", confidence=1.0, reason="empty text", needs_llm=False, safe_to_skip=True)

    text_lower = text.lower()

    best_name = "other"
    best_score = 0.0
    best_reason = "no match"
    best_safe = False

    for name, keywords, patterns, weight, safe_to_skip in _INTENTS:
        if name == "empty":
            continue
        score = 0.0
        reasons = []

        # Keyword matching: +0.3 per hit, max 0.9
        kw_hits = sum(1 for kw in keywords if kw in text_lower)
        if kw_hits > 0:
            kw_score = min(kw_hits * 0.3, 0.9)
            score += kw_score
            reasons.append(f"kw:{kw_hits}")

        # Pattern matching: +0.5 per hit
        for pat in patterns:
            if re.search(pat, text_lower):
                score += 0.5
                reasons.append(f"pat:{pat[:20]}")
                break  # one pattern match is enough

        score = min(score * weight, 1.0)

        if score > best_score:
            best_score = score
            best_name = name
            best_reason = ", ".join(reasons) if reasons else "no match"
            best_safe = safe_to_skip

    # If no match found, return "other" with low confidence
    if best_score < 0.1:
        return IntentResult(
            name="other",
            confidence=0.3,
            reason="no pattern match",
            needs_llm=True,
            safe_to_skip=False,
        )

    needs_llm = best_score < _THRESHOLD and not best_safe
    return IntentResult(
        name=best_name,
        confidence=round(best_score, 3),
        reason=best_reason,
        needs_llm=needs_llm,
        safe_to_skip=best_safe,
    )
