"""LLM fallback classifier — called only when rules confidence < 0.8."""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from .rules import IntentResult

if TYPE_CHECKING:
    from banghack.adapters.llm import LLMAdapter

log = logging.getLogger(__name__)

VALID_INTENTS = frozenset({
    "price_question", "stock_question", "greeting", "buying_intent",
    "compatibility", "how_to_use", "objection", "spam", "other",
})

_CACHE_TTL_S = 300  # 5 minutes
_cache: dict[str, tuple[IntentResult, float]] = {}  # key -> (result, ts)


async def classify_with_llm(text: str, llm: "LLMAdapter") -> IntentResult:
    """Classify text via LLM with 5-minute cache.

    Returns IntentResult. Falls back to "other" on timeout or error.
    """
    cache_key = text[:50].lower().strip()

    # Check cache
    if cache_key in _cache:
        result, ts = _cache[cache_key]
        if time.time() - ts < _CACHE_TTL_S:
            log.debug("llm_fallback cache hit for: %s", cache_key)
            return result
        else:
            del _cache[cache_key]

    prompt = (
        "Klasifikasikan komentar TikTok Live berikut ke salah satu kategori:\n"
        "price_question, stock_question, greeting, buying_intent, compatibility, "
        "how_to_use, objection, spam, other\n"
        "Jawab HANYA dengan nama kategori, tanpa penjelasan.\n"
        f'Komentar: "{text}"'
    )

    try:
        llm_result = await llm.reply("", prompt, max_tokens=20)
        if llm_result.tier == "error" or not llm_result.text:
            raise RuntimeError("LLM returned error")

        intent_name = llm_result.text.strip().lower().split()[0]
        intent_name = intent_name.strip(".,!?\"'")

        if intent_name not in VALID_INTENTS:
            log.warning("LLM returned unknown intent %r, defaulting to 'other'", intent_name)
            intent_name = "other"

        result = IntentResult(
            name=intent_name,
            confidence=0.75,
            reason=f"llm:{llm_result.tier}",
            needs_llm=False,
            safe_to_skip=False,
        )
    except Exception as exc:
        log.warning("LLM fallback failed: %s — defaulting to 'other'", exc)
        result = IntentResult(
            name="other",
            confidence=0.5,
            reason=f"llm_error:{type(exc).__name__}",
            needs_llm=False,
            safe_to_skip=False,
        )

    # Cache result
    _cache[cache_key] = (result, time.time())

    # Evict old entries
    if len(_cache) > 500:
        cutoff = time.time() - _CACHE_TTL_S
        expired = [k for k, (_, ts) in _cache.items() if ts < cutoff]
        for k in expired:
            del _cache[k]

    return result
