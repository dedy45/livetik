"""Audio device helper — list output devices via sounddevice."""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def list_devices() -> list[dict]:  # type: ignore[type-arg]
    """Return list of output audio devices.

    Returns:
        List of dicts: [{index, name, max_output_channels, is_default}, ...]
        Returns [{"error": "..."}] if sounddevice not installed.
    """
    try:
        import sounddevice as sd  # type: ignore[import-not-found]
    except ImportError:
        return [{"error": "sounddevice not installed — add sounddevice>=0.4.6 to pyproject.toml"}]
    try:
        devices = sd.query_devices()
        default_out = sd.default.device[1] if sd.default.device else -1
        out: list[dict] = []  # type: ignore[type-arg]
        for i, d in enumerate(devices):
            if d.get("max_output_channels", 0) > 0:
                out.append({
                    "index": i,
                    "name": d.get("name", ""),
                    "max_output_channels": d.get("max_output_channels", 0),
                    "is_default": i == default_out,
                })
        return out
    except Exception as e:
        log.error("list_devices failed: %s", e)
        return [{"error": str(e)[:200]}]
