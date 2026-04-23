"""Tests for AudioLibraryManager — P0 acceptance."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from banghack.core.audio_library.manager import AudioLibraryManager, ClipMeta


@pytest.fixture
def tmp_audio_dir(tmp_path: Path) -> Path:
    """Create a temp dir with a minimal index.json and dummy .wav files."""
    index = {
        "version": "1.0",
        "clips": [
            {
                "id": "A_opening_001",
                "category": "A_opening",
                "tags": ["opening", "greeting"],
                "duration_ms": 3000,
                "voice_id": "test-voice",
                "script": "Halo semuanya selamat datang",
                "scene_hint": "A_opening",
            },
            {
                "id": "B_paloma_demo_001",
                "category": "B_paloma_demo",
                "tags": ["paloma", "demo"],
                "duration_ms": 5000,
                "voice_id": "test-voice",
                "script": "PALOMA Smart Lock demo",
                "scene_hint": "B_paloma_demo",
            },
            {
                "id": "Z_closing_001",
                "category": "Z_closing",
                "tags": ["closing", "goodbye"],
                "duration_ms": 2000,
                "voice_id": "test-voice",
                "script": "Makasih sudah nonton",
                "scene_hint": "Z_closing",
            },
        ],
    }
    # Write index.json
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(index), encoding="utf-8")
    # Create dummy .wav files (empty bytes — just need to exist)
    for clip in index["clips"]:
        (tmp_path / f"{clip['id']}.wav").write_bytes(b"RIFF")
    return tmp_path


@pytest.mark.asyncio
async def test_load_empty(tmp_path: Path) -> None:
    """Manager loads empty index without error."""
    index_path = tmp_path / "index.json"
    index_path.write_text('{"version": "1.0", "clips": []}', encoding="utf-8")
    mgr = AudioLibraryManager(index_path)
    await mgr.load()
    assert mgr.is_ready
    assert mgr.clip_count == 0


@pytest.mark.asyncio
async def test_load_index(tmp_audio_dir: Path) -> None:
    """Manager loads 3 clips from index.json."""
    mgr = AudioLibraryManager(tmp_audio_dir / "index.json")
    await mgr.load()
    assert mgr.is_ready
    assert mgr.clip_count == 3


@pytest.mark.asyncio
async def test_anti_repeat(tmp_audio_dir: Path) -> None:
    """mark_played + not_played_since filters correctly."""
    mgr = AudioLibraryManager(tmp_audio_dir / "index.json")
    await mgr.load()
    # Initially all clips not played
    assert len(mgr.not_played_since(window_s=1200)) == 3
    # Mark one as played
    mgr.mark_played("A_opening_001")
    # With window_s=0, recently played clips are excluded
    not_played = mgr.not_played_since(window_s=0)
    ids = [c.id for c in not_played]
    assert "A_opening_001" not in ids
    assert "B_paloma_demo_001" in ids


@pytest.mark.asyncio
async def test_by_category(tmp_audio_dir: Path) -> None:
    """by_category returns only clips in that category."""
    mgr = AudioLibraryManager(tmp_audio_dir / "index.json")
    await mgr.load()
    opening = mgr.by_category("A_opening")
    assert len(opening) == 1
    assert opening[0].id == "A_opening_001"
    closing = mgr.by_category("Z_closing")
    assert len(closing) == 1
    assert closing[0].id == "Z_closing_001"
    empty = mgr.by_category("nonexistent")
    assert empty == []


@pytest.mark.asyncio
async def test_by_product(tmp_audio_dir: Path) -> None:
    """by_product returns clips matching product name in category or tags."""
    mgr = AudioLibraryManager(tmp_audio_dir / "index.json")
    await mgr.load()
    paloma = mgr.by_product("paloma")
    assert len(paloma) >= 1
    assert any(c.id == "B_paloma_demo_001" for c in paloma)
