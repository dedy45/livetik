"""Config persistence — .env writer (with backup) + .state.json for runtime toggles."""
from __future__ import annotations

import json
import logging
import shutil
import time
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

ENV_PATH = Path(".env")
STATE_PATH = Path(".state.json")

# Keys yang aman di-expose via read_env (tidak secret)
SAFE_KEYS = frozenset({
    "TIKTOK_USERNAME", "CARTESIA_VOICE_ID", "CARTESIA_MODEL",
    "CARTESIA_DEFAULT_EMOTION", "EDGE_TTS_VOICE", "NINEROUTER_BASE_URL",
    "NINEROUTER_MODEL", "BUDGET_IDR_DAILY", "USD_TO_IDR", "HTTP_HOST", "HTTP_PORT",
    "AUDIO_DEVICE_INDEX", "REPLY_ENABLED", "DRY_RUN",
    "GUARDRAIL_MIN_WORDS", "GUARDRAIL_RATE_MAX", "GUARDRAIL_RATE_WINDOW_S", "GUARDRAIL_MAX_CHARS",
})

# Keys yang HARUS di-mask (show first 4 + *** + last 4)
SECRET_KEYS = frozenset({
    "CARTESIA_API_KEYS", "NINEROUTER_API_KEY",
    "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY",
})


def _parse_env(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def read_env(mask_secrets: bool = True) -> dict[str, str]:
    """Read .env and return dict. Masks secret keys when mask_secrets=True."""
    if not ENV_PATH.exists():
        return {}
    data = _parse_env(ENV_PATH.read_text(encoding="utf-8"))
    if mask_secrets:
        for k in list(data.keys()):
            if k in SECRET_KEYS and data[k]:
                v = data[k]
                data[k] = f"{v[:4]}***{v[-4:]}" if len(v) > 8 else "***"
    return data


def write_env(updates: dict[str, str]) -> Path:
    """Atomic update .env with timestamped backup.

    Preserves existing lines (comments, ordering). Keys in updates dict are replaced;
    new keys appended at end. Returns backup path for rollback.

    Raises:
        OSError: kalau filesystem gagal.
    """
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup = ENV_PATH.parent / f".env.bak.{ts}"
    if ENV_PATH.exists():
        shutil.copy2(ENV_PATH, backup)

    existing_lines: list[str] = []
    existing_keys: set[str] = set()
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                existing_lines.append(line)
                continue
            key = stripped.partition("=")[0].strip()
            if key in updates:
                existing_lines.append(f"{key}={updates[key]}")
                existing_keys.add(key)
            else:
                existing_lines.append(line)

    for k, v in updates.items():
        if k not in existing_keys:
            existing_lines.append(f"{k}={v}")

    # Atomic write via temp rename
    tmp = ENV_PATH.parent / ".env.tmp"
    tmp.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")
    tmp.replace(ENV_PATH)
    log.info("wrote .env (%d keys, backup: %s)", len(updates), backup.name)
    return backup


def load_state() -> dict[str, Any]:
    """Load .state.json runtime toggles. Returns empty dict on error."""
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except (OSError, json.JSONDecodeError) as e:
        log.warning("load_state failed: %s", e)
        return {}


def save_state(state: dict[str, Any]) -> None:
    """Atomic save .state.json."""
    tmp = STATE_PATH.parent / ".state.json.tmp"
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(STATE_PATH)
