"""Suggester — generate 3 reply options from templates or LLM."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from .budget_guard import BudgetGuard
from .reply_cache import ReplyCache

if TYPE_CHECKING:
    from banghack.adapters.llm import LLMAdapter

log = logging.getLogger(__name__)

# Intents that use templates (no LLM needed)
TEMPLATE_INTENTS = frozenset({"greeting", "price_question", "stock_question", "buying_intent"})

# Regex patterns for output safety filter
_UNSAFE_PATTERNS = [
    re.compile(r"https?://\S+"),
    re.compile(r"wa\.me/\S+"),
    re.compile(r"\b\d{10,}\b"),
    re.compile(r"\bRp\s*\d[\d.,]+\b"),
]


def _safe(reply: str) -> str:
    """Strip unsafe content from reply text."""
    for pat in _UNSAFE_PATTERNS:
        reply = pat.sub("[...]", reply)
    return reply.strip()


class Suggester:
    """Generate 3 reply options for a comment."""

    def __init__(
        self,
        cache: ReplyCache,
        budget_guard: BudgetGuard,
        llm: "LLMAdapter",
        templates_path: Path,
    ) -> None:
        self._cache = cache
        self._guard = budget_guard
        self._llm = llm
        self._templates: dict[str, dict[str, str]] = {}
        self._load_templates(templates_path)

    def _load_templates(self, path: Path) -> None:
        try:
            with path.open(encoding="utf-8") as f:
                self._templates = yaml.safe_load(f) or {}
            log.info("reply_templates loaded: %d intents", len(self._templates))
        except Exception as exc:
            log.warning("Failed to load reply_templates.yaml: %s", exc)
            self._templates = {}

    async def handle(self, text: str, intent: str, product: str = "", user: str = "") -> dict:  # type: ignore[type-arg]
        """Generate 3 reply suggestions.

        Returns dict with keys: replies (list[str]), source (template|llm|cache), cached (bool)
        """
        # Fallback for empty product/user
        product = product or "produk ini"
        user = user or "kak"
        
        cached = self._cache.lookup(text, intent)
        if cached:
            self._guard.record_cache_hit()
            return {"replies": cached, "source": "cache", "cached": True}

        replies: list[str]
        source: str

        if intent in TEMPLATE_INTENTS and intent in self._templates:
            tmpl = self._templates[intent]
            replies = [
                _safe(tmpl.get("formal", "").format(product=product, user=user)),
                _safe(tmpl.get("casual", "").format(product=product, user=user)),
                _safe(tmpl.get("enthusiastic", "").format(product=product, user=user)),
            ]
            replies = [r for r in replies if r] or [f"Terima kasih kak {user}!"] * 3
            source = "template"
        elif self._guard.can_call():
            prompt = (
                f"Buat 3 variasi reply untuk komentar TikTok Live tentang produk {product or 'kami'}.\n"
                f'Komentar: "{text}"\n'
                'Format: JSON array ["formal", "casual", "enthusiastic"]\n'
                "Max 30 kata per reply. Bahasa Indonesia. Jangan sertakan link atau nomor telepon."
            )
            try:
                result = await self._llm.reply("", prompt, max_tokens=200)
                if result.tier != "error" and result.text:
                    text_clean = result.text.strip()
                    start = text_clean.find("[")
                    end = text_clean.rfind("]") + 1
                    if start >= 0 and end > start:
                        parsed = json.loads(text_clean[start:end])
                        replies = [_safe(str(r)) for r in parsed[:3]]
                    else:
                        replies = [_safe(result.text[:100])] * 3
                    while len(replies) < 3:
                        replies.append(replies[0] if replies else "Terima kasih kak!")
                    self._guard.record_call(
                        result.prompt_tokens + result.completion_tokens,
                        0.0,
                    )
                    source = "llm"
                else:
                    raise RuntimeError("LLM error")
            except Exception as exc:
                log.warning("Suggester LLM failed: %s — using template fallback", exc)
                replies = self._template_fallback(intent, product, user)
                source = "template_fallback"
        else:
            await self._guard.emit_blocked("budget_exceeded_suggester")
            replies = self._template_fallback(intent, product, user)
            source = "template_fallback"

        self._cache.put(text, intent, replies)
        return {"replies": replies, "source": source, "cached": False}

    def _template_fallback(self, intent: str, product: str, user: str) -> list[str]:
        if intent in self._templates:
            tmpl = self._templates[intent]
            replies = [
                _safe(tmpl.get("formal", "").format(product=product, user=user)),
                _safe(tmpl.get("casual", "").format(product=product, user=user)),
                _safe(tmpl.get("enthusiastic", "").format(product=product, user=user)),
            ]
            return [r for r in replies if r] or ["Terima kasih kak!"] * 3
        return [
            f"Terima kasih kak {user}! Silakan cek info lebih lanjut di bio kami.",
            f"Makasih kak {user}! Ada yang bisa kami bantu?",
            f"Halo kak {user}! Yuk cek produk kami!",
        ]
