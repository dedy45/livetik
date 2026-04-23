"""Tests for LiveDirector state machine — P3 acceptance."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
import yaml

from banghack.core.orchestrator.director import LiveDirector, LiveMode


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def products_yaml(tmp_path: Path) -> Path:
    """Create a minimal products.yaml for testing."""
    data = {
        "products": [
            {"id": "TEST", "name": "Test Product", "demo_clip_tag": "demo",
             "cta_clip_tag": "cta", "hook_clip_tag": "hook",
             "demo_duration_min": 1, "cta_duration_min": 1}
        ],
        "runsheet": [
            {"phase": "opening", "duration_s": 2, "product": None,
             "clip_category": "A_opening", "obs_scene": "scene_opening"},
            {"phase": "demo", "duration_s": 2, "product": "TEST",
             "clip_category": "demo", "obs_scene": "scene_product"},
        ]
    }
    yaml_path = tmp_path / "products.yaml"
    yaml_path.write_text(yaml.dump(data), encoding="utf-8")
    return yaml_path


class MockAudioManager:
    def by_category(self, cat: str):
        return []

    def not_played_since(self, window_s: int = 1200):
        return []


class MockAudioAdapter:
    async def play(self, clip_id: str) -> None:
        pass

    async def stop(self) -> None:
        pass


async def noop_broadcast(event: dict) -> None:
    pass


# ── Tests ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_start_sets_running(products_yaml: Path) -> None:
    """start() transitions mode to RUNNING."""
    director = LiveDirector(
        products_yaml=products_yaml,
        audio_manager=MockAudioManager(),
        audio_adapter=MockAudioAdapter(),
        ws_broadcast=noop_broadcast,
        max_duration_s=60,
    )
    assert director.mode == LiveMode.IDLE
    await director.start()
    assert director.mode == LiveMode.RUNNING
    await director.stop()


@pytest.mark.asyncio
async def test_pause_resume(products_yaml: Path) -> None:
    """pause() sets PAUSED, resume() sets RUNNING."""
    director = LiveDirector(
        products_yaml=products_yaml,
        audio_manager=MockAudioManager(),
        audio_adapter=MockAudioAdapter(),
        ws_broadcast=noop_broadcast,
        max_duration_s=60,
    )
    await director.start()
    assert director.mode == LiveMode.RUNNING
    await director.pause()
    assert director.mode == LiveMode.PAUSED
    await director.resume()
    assert director.mode == LiveMode.RUNNING
    await director.stop()


@pytest.mark.asyncio
async def test_emergency_stop(products_yaml: Path) -> None:
    """emergency_stop() transitions to STOPPED immediately."""
    director = LiveDirector(
        products_yaml=products_yaml,
        audio_manager=MockAudioManager(),
        audio_adapter=MockAudioAdapter(),
        ws_broadcast=noop_broadcast,
        max_duration_s=60,
    )
    await director.start()
    assert director.mode == LiveMode.RUNNING
    await director.emergency_stop(operator_id="test")
    assert director.mode == LiveMode.STOPPED


@pytest.mark.asyncio
async def test_hard_stop_at_max_duration(products_yaml: Path) -> None:
    """Director auto-stops when max_duration_s is reached."""
    director = LiveDirector(
        products_yaml=products_yaml,
        audio_manager=MockAudioManager(),
        audio_adapter=MockAudioAdapter(),
        ws_broadcast=noop_broadcast,
        max_duration_s=3,  # 3 seconds for fast test
    )
    await director.start()
    # Wait for hard stop
    for _ in range(50):  # max 5 seconds
        await asyncio.sleep(0.1)
        if director.mode == LiveMode.STOPPED:
            break
    assert director.mode == LiveMode.STOPPED


def test_is_ready(products_yaml: Path) -> None:
    """is_ready returns True when runsheet is loaded."""
    director = LiveDirector(
        products_yaml=products_yaml,
        audio_manager=MockAudioManager(),
        audio_adapter=MockAudioAdapter(),
        ws_broadcast=noop_broadcast,
    )
    assert director.is_ready is True


def test_get_state(products_yaml: Path) -> None:
    """get_state() returns dict with expected keys."""
    director = LiveDirector(
        products_yaml=products_yaml,
        audio_manager=MockAudioManager(),
        audio_adapter=MockAudioAdapter(),
        ws_broadcast=noop_broadcast,
    )
    state = director.get_state()
    assert "mode" in state
    assert "phase" in state
    assert "elapsed_s" in state
    assert "remaining_s" in state
    assert state["mode"] == "IDLE"
