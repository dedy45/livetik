"""Generate audio library from clips_script.yaml using Cartesia TTS API.

This script reads clips_script.yaml, generates .wav files via Cartesia TTS,
and populates index.json for the AudioLibraryManager.

Usage:
    python scripts/gen_audio_library.py
    
Or on Windows:
    scripts\\gen_audio_library.bat
"""
import asyncio
import json
import os
import sys
from pathlib import Path

import httpx
import yaml
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "worker" / "src"))

load_dotenv()

CLIPS_YAML = PROJECT_ROOT / "apps/worker/config/clips_script.yaml"
OUT_DIR = PROJECT_ROOT / "apps/worker/static/audio_library"
INDEX_JSON = OUT_DIR / "index.json"

# Get API keys from environment
API_KEYS_STR = os.environ.get("CARTESIA_API_KEYS", "")
if not API_KEYS_STR:
    print("ERROR: CARTESIA_API_KEYS not found in environment")
    sys.exit(1)

API_KEYS = [k.strip() for k in API_KEYS_STR.split(",") if k.strip()]
VOICE_ID = os.environ.get("CARTESIA_VOICE_ID", "a167e0f3-df7e-4d52-a9c3-f949145efdab")
MODEL = os.environ.get("CARTESIA_MODEL", "sonic-3")

print(f"Using {len(API_KEYS)} Cartesia API key(s)")
print(f"Voice ID: {VOICE_ID}")
print(f"Model: {MODEL}")


async def gen_one(client: httpx.AsyncClient, clip: dict, api_key: str) -> dict:  # type: ignore[type-arg]
    """Generate one audio clip via Cartesia TTS API."""
    clip_id = clip["id"]
    out_path = OUT_DIR / f"{clip_id}.wav"
    
    # Skip if already exists
    if out_path.exists():
        # Read existing file to get duration
        size = out_path.stat().st_size
        # Rough estimate: 44100 Hz * 4 bytes (f32le) = 176400 bytes/sec
        duration_ms = int((size / 176400) * 1000)
        return {
            "id": clip_id,
            "category": clip["category"],
            "tags": clip.get("tags", []),
            "duration_ms": duration_ms,
            "voice_id": VOICE_ID,
            "script": clip["text"],
            "scene_hint": clip["category"],
            "file_path": f"{clip_id}.wav",
            "skipped": True,
        }
    
    # Generate new audio
    try:
        r = await client.post(
            "https://api.cartesia.ai/tts/bytes",
            headers={
                "Cartesia-Version": "2024-06-10",
                "X-API-Key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "model_id": MODEL,
                "transcript": clip["text"],
                "voice": {"mode": "id", "id": VOICE_ID},
                "language": "id",
                "output_format": {
                    "container": "wav",
                    "encoding": "pcm_f32le",
                    "sample_rate": 44100,
                },
                "experimental_controls": {
                    "emotions": [clip.get("emotion", "neutral")]
                },
            },
            timeout=30.0,
        )
        r.raise_for_status()
        
        # Write audio file
        out_path.write_bytes(r.content)
        size = len(r.content)
        duration_ms = int((size / 176400) * 1000)
        
        return {
            "id": clip_id,
            "category": clip["category"],
            "tags": clip.get("tags", []),
            "duration_ms": duration_ms,
            "voice_id": VOICE_ID,
            "script": clip["text"],
            "scene_hint": clip["category"],
            "file_path": f"{clip_id}.wav",
        }
    except Exception as e:
        print(f"  ERROR: {e}")
        raise


async def main() -> None:
    """Main generation loop."""
    # Create output directory
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load clips
    if not CLIPS_YAML.exists():
        print(f"ERROR: {CLIPS_YAML} not found")
        sys.exit(1)
    
    data = yaml.safe_load(CLIPS_YAML.read_text(encoding="utf-8"))
    clips = data.get("clips", [])
    
    if not clips:
        print("ERROR: No clips found in clips_script.yaml")
        sys.exit(1)
    
    print(f"\nGenerating {len(clips)} clips...")
    print(f"Output directory: {OUT_DIR}")
    print("-" * 60)
    
    # Round-robin API keys
    key_idx = 0
    index_entries = []
    skipped_count = 0
    generated_count = 0
    failed_count = 0
    
    async with httpx.AsyncClient(timeout=30) as client:
        for i, clip in enumerate(clips):
            clip_id = clip["id"]
            api_key = API_KEYS[key_idx % len(API_KEYS)]
            key_idx += 1
            
            try:
                entry = await gen_one(client, clip, api_key)
                
                if entry.get("skipped"):
                    skipped_count += 1
                    print(f"[{i+1}/{len(clips)}] {clip_id} SKIPPED (exists)")
                    # Remove skipped flag before adding to index
                    del entry["skipped"]
                else:
                    generated_count += 1
                    print(f"[{i+1}/{len(clips)}] {clip_id} ({entry['duration_ms']}ms) ✓")
                
                index_entries.append(entry)
                
                # Rate limit: 0.5s between requests
                await asyncio.sleep(0.5)
                
            except Exception as e:
                failed_count += 1
                print(f"[{i+1}/{len(clips)}] {clip_id} FAILED: {e}")
    
    # Write index.json
    index_data = {
        "version": "1.0",
        "clips": index_entries,
    }
    INDEX_JSON.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print("-" * 60)
    print(f"\n✓ Generation complete!")
    print(f"  Generated: {generated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total in index: {len(index_entries)}")
    print(f"\nIndex written to: {INDEX_JSON}")
    
    if failed_count > 0:
        print(f"\n⚠ WARNING: {failed_count} clips failed to generate")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
