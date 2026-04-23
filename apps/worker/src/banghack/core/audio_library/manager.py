"""Audio Library Manager -- load index.json, fuzzy search, hot-reload."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass
class ClipMeta:
    id: str
    category: str
    tags: list[str]
    duration_ms: int
    voice_id: str
    script: str
    scene_hint: str
    file_path: str


class AudioLibraryManager:
    def __init__(self, index_path: Path) -> None:
        self._index_path = index_path
        self._clips: dict[str, ClipMeta] = {}
        self._last_mtime: float = 0.0
        self._played: dict[str, float] = {}
        self._ready = False

    async def load(self) -> None:
        try:
            raw = json.loads(self._index_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            log.warning("index.json not found at %s", self._index_path)
            self._ready = True
            return
        except json.JSONDecodeError as exc:
            log.error("index.json parse error: %s", exc)
            return

        clips_raw: list[dict] = raw.get("clips", [])
        loaded: dict[str, ClipMeta] = {}
        base_dir = self._index_path.parent

        for clip in clips_raw:
            clip_id = clip.get("id", "")
            if not clip_id:
                log.warning("clip missing id, skipping: %s", clip)
                continue

            if clip.get("file_path"):
                fp = Path(clip["file_path"])
                if not fp.is_absolute():
                    fp = base_dir / fp
            else:
                fp = base_dir / f"{clip_id}.wav"

            if not fp.exists():
                log.debug("clip file missing, skipping: %s", clip_id)
                continue

            loaded[clip_id] = ClipMeta(
                id=clip_id,
                category=clip.get("category", ""),
                tags=clip.get("tags", []),
                duration_ms=int(clip.get("duration_ms", 0)),
                voice_id=clip.get("voice_id", ""),
                script=clip.get("script", clip.get("text", "")),
                scene_hint=clip.get("scene_hint", clip.get("category", "")),
                file_path=str(fp),
            )

        self._clips = loaded
        self._last_mtime = self._index_path.stat().st_mtime if self._index_path.exists() else 0.0
        self._ready = True
        log.info("audio_library loaded: %d clips from %s", len(self._clips), self._index_path)

    def by_category(self, category: str) -> list[ClipMeta]:
        return [c for c in self._clips.values() if c.category == category]

    def by_product(self, product: str) -> list[ClipMeta]:
        product_lower = product.lower()
        return [
            c for c in self._clips.values()
            if product_lower in c.category.lower() or product_lower in " ".join(c.tags).lower()
        ]

    def mark_played(self, clip_id: str) -> None:
        self._played[clip_id] = time.time()

    def not_played_since(self, window_s: int = 1200) -> list[ClipMeta]:
        cutoff = time.time() - window_s
        return [c for c in self._clips.values() if self._played.get(c.id, 0) < cutoff]

    def search(self, tag: str) -> list[ClipMeta]:
        tag_lower = tag.lower()
        return [
            c for c in self._clips.values()
            if any(tag_lower in t.lower() for t in c.tags)
            or tag_lower in c.script.lower()
            or tag_lower in c.category.lower()
        ]

    def get(self, clip_id: str) -> ClipMeta | None:
        return self._clips.get(clip_id)

    def start_hot_reload(self) -> None:
        asyncio.create_task(self._hot_reload_loop())

    async def _hot_reload_loop(self) -> None:
        while True:
            await asyncio.sleep(5)
            try:
                mtime = self._index_path.stat().st_mtime
                if mtime != self._last_mtime:
                    old_count = len(self._clips)
                    await self.load()
                    log.info("audio_library hot-reload: %d -> %d clips", old_count, len(self._clips))
            except Exception as e:
                log.warning("hot-reload error: %s", e)

    @property
    def clip_count(self) -> int:
        return len(self._clips)

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def all_clips(self) -> list[ClipMeta]:
        return list(self._clips.values())
