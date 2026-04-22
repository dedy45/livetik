"""Persona loader — reads config/persona.md once at startup."""
from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)

DEFAULT_PERSONA = (
    "Kamu adalah Bang Hack, asisten virtual TikTok Live @interiorhack.id. "
    "Jawab dalam bahasa Indonesia santai maksimal 2 kalimat pendek. "
    "Fokus interior, furniture, rangka baja. Jangan sebut harga pasti atau kontak."
)


def load_persona(path: str | Path = "config/persona.md") -> str:
    p = Path(path)
    if p.exists():
        content = p.read_text(encoding="utf-8").strip()
        if content:
            log.info("persona loaded from %s (%d chars)", p, len(content))
            return content
    log.warning("persona file %s not found → using DEFAULT_PERSONA", p)
    return DEFAULT_PERSONA
