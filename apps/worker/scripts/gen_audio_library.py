#!/usr/bin/env python3
"""Generate audio library clips via Cartesia TTS.

Usage:
    uv run python scripts/gen_audio_library.py
    uv run python scripts/gen_audio_library.py --category A_opening --limit 10
    uv run python scripts/gen_audio_library.py --dry-run
    uv run python scripts/gen_audio_library.py --force

NOTE: To verify generated clips, run manually:
    uv run python scripts/gen_audio_library.py --category A_opening --limit 10
    Then check static/audio_library/ for .wav files and index.json for updated entries.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# ---------------------------------------------------------------------------
# Config from env
# ---------------------------------------------------------------------------
CLIPS_SCRIPT_YAML = os.getenv("CLIPS_SCRIPT_YAML", "config/clips_script.yaml")
AUDIO_LIBRARY_DIR = os.getenv("AUDIO_LIBRARY_DIR", "static/audio_library")
CARTESIA_API_KEYS = os.getenv("CARTESIA_API_KEYS", "")
CARTESIA_VOICE_ID = os.getenv("CARTESIA_VOICE_ID", "")
CARTESIA_MODEL = os.getenv("CARTESIA_MODEL", "sonic-3")

OUTPUT_FORMAT = {
    "container": "wav",
    "encoding": "pcm_f32le",
    "sample_rate": 44100,
}

# Duration: len(audio_bytes) / (sample_rate * bytes_per_sample)
# pcm_f32le = 4 bytes per sample, mono
BYTES_PER_SAMPLE = 4
SAMPLE_RATE = 44100


def calc_duration_ms(audio_bytes: bytes) -> int:
    """Calculate duration in milliseconds from raw PCM bytes."""
    seconds = len(audio_bytes) / (SAMPLE_RATE * BYTES_PER_SAMPLE)
    return int(seconds * 1000)


# ---------------------------------------------------------------------------
# Round-robin key pool (sync, no asyncio.Lock needed for single-threaded async)
# ---------------------------------------------------------------------------
class SimpleKeyPool:
    def __init__(self, keys: list[str]) -> None:
        if not keys:
            raise RuntimeError("CARTESIA_API_KEYS is empty — add comma-separated keys")
        self.keys = keys
        self._idx = 0

    def next_key(self) -> str:
        key = self.keys[self._idx]
        self._idx = (self._idx + 1) % len(self.keys)
        return key


# ---------------------------------------------------------------------------
# Core generation logic
# ---------------------------------------------------------------------------
async def generate_clip(
    clip: dict,
    pool: SimpleKeyPool,
    output_dir: Path,
    dry_run: bool = False,
) -> dict | None:
    """Generate a single clip. Returns index entry dict or None on failure."""
    clip_id: str = clip["id"]
    text: str = clip["text"]
    category: str = clip["category"]
    tags: list[str] = clip.get("tags", [])
    emotion: str = clip.get("emotion", "neutral")

    wav_path = output_dir / f"{clip_id}.wav"

    if dry_run:
        print(f"  [DRY-RUN] Would generate: {clip_id} ({len(text)} chars)")
        return {
            "id": clip_id,
            "category": category,
            "tags": tags,
            "duration_ms": 0,
            "voice_id": CARTESIA_VOICE_ID,
            "script": text,
            "scene_hint": category,
            "file_path": f"static/audio_library/{clip_id}.wav",
        }

    from cartesia import AsyncCartesia  # noqa: PLC0415

    key = pool.next_key()
    audio_bytes = b""

    try:
        async with AsyncCartesia(api_key=key) as client:
            async for chunk in client.tts.bytes(
                model_id=CARTESIA_MODEL,
                transcript=text,
                voice={
                    "mode": "id",
                    "id": CARTESIA_VOICE_ID,
                    "experimental_controls": {"emotions": [emotion]},
                },
                language="id",
                output_format=OUTPUT_FORMAT,
            ):
                audio_bytes += chunk
    except Exception as exc:
        log.warning("  [WARN] Failed to generate %s: %s", clip_id, exc)
        return None

    wav_path.write_bytes(audio_bytes)
    duration_ms = calc_duration_ms(audio_bytes)

    return {
        "id": clip_id,
        "category": category,
        "tags": tags,
        "duration_ms": duration_ms,
        "voice_id": CARTESIA_VOICE_ID,
        "script": text,
        "scene_hint": category,
        "file_path": f"static/audio_library/{clip_id}.wav",
    }


def load_existing_index(index_path: Path) -> dict[str, dict]:
    """Load existing index.json, return dict keyed by clip id."""
    if not index_path.exists():
        return {}
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        return {c["id"]: c for c in data.get("clips", [])}
    except Exception as exc:
        log.warning("Could not read existing index.json: %s", exc)
        return {}


def save_index(index_path: Path, clips_by_id: dict[str, dict]) -> None:
    """Write index.json sorted by clip id."""
    clips_list = sorted(clips_by_id.values(), key=lambda c: c["id"])
    data = {"version": "1.0", "clips": clips_list}
    index_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main(args: argparse.Namespace) -> int:
    yaml_path = Path(CLIPS_SCRIPT_YAML)
    if not yaml_path.exists():
        log.error("clips_script.yaml not found at: %s", yaml_path)
        return 1

    output_dir = Path(AUDIO_LIBRARY_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.json"

    # Load yaml
    with yaml_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    all_clips: list[dict] = data.get("clips", [])

    # Filter by category
    if args.category:
        all_clips = [c for c in all_clips if c.get("category") == args.category]
        if not all_clips:
            log.error("No clips found for category: %s", args.category)
            return 1

    # Filter out already-generated (unless --force)
    if not args.force:
        pending = [c for c in all_clips if not (output_dir / f"{c['id']}.wav").exists()]
    else:
        pending = all_clips

    # Apply --limit
    if args.limit is not None:
        pending = pending[: args.limit]

    total = len(pending)
    if total == 0:
        print("Nothing to generate — all clips already exist. Use --force to regenerate.")
        return 0

    # Setup key pool (skip for dry-run)
    pool: SimpleKeyPool | None = None
    if not args.dry_run:
        keys = [k.strip() for k in CARTESIA_API_KEYS.split(",") if k.strip()]
        if not keys:
            log.error("CARTESIA_API_KEYS is not set in .env")
            return 1
        if not CARTESIA_VOICE_ID:
            log.error("CARTESIA_VOICE_ID is not set in .env")
            return 1
        pool = SimpleKeyPool(keys)

    # Load existing index entries
    existing_index = load_existing_index(index_path)

    # Generate
    generated = 0
    for i, clip in enumerate(pending, start=1):
        clip_id = clip["id"]
        print(f"[{i}/{total}] Generating {clip_id}...")

        entry = await generate_clip(clip, pool, output_dir, dry_run=args.dry_run)  # type: ignore[arg-type]
        if entry is not None:
            existing_index[clip_id] = entry
            generated += 1

    # Also index any .wav files already on disk that aren't in index yet
    for wav_file in sorted(output_dir.glob("*.wav")):
        cid = wav_file.stem
        if cid not in existing_index:
            # Find clip metadata from yaml
            yaml_clip = next((c for c in data.get("clips", []) if c["id"] == cid), None)
            if yaml_clip:
                audio_bytes = wav_file.read_bytes()
                existing_index[cid] = {
                    "id": cid,
                    "category": yaml_clip.get("category", ""),
                    "tags": yaml_clip.get("tags", []),
                    "duration_ms": calc_duration_ms(audio_bytes),
                    "voice_id": CARTESIA_VOICE_ID,
                    "script": yaml_clip.get("text", ""),
                    "scene_hint": yaml_clip.get("category", ""),
                    "file_path": f"static/audio_library/{cid}.wav",
                }

    # Save updated index
    save_index(index_path, existing_index)

    skipped = total - generated
    print(
        f"\nDone. Generated: {generated}, Skipped/Failed: {skipped}. "
        f"Index updated: {index_path} ({len(existing_index)} total clips)"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate audio library clips via Cartesia TTS"
    )
    parser.add_argument("--category", metavar="CATEGORY", help="Filter by category")
    parser.add_argument("--dry-run", action="store_true", help="Don't call API, just print")
    parser.add_argument("--limit", type=int, metavar="N", help="Max clips to generate")
    parser.add_argument("--force", action="store_true", help="Regenerate even if .wav exists")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(asyncio.run(main(args)))
