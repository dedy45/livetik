#!/usr/bin/env python3
"""Rebuild index.json from existing audio files in audio_library folders.

This script scans all .wav files in audio_library subfolders and rebuilds
the index.json file with proper metadata.
"""
import json
import wave
from pathlib import Path


def get_wav_duration_ms(wav_path: Path) -> int:
    """Get duration of WAV file in milliseconds."""
    try:
        with wave.open(str(wav_path), 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration_s = frames / float(rate)
            return int(duration_s * 1000)
    except Exception:
        return 15000  # Default 15s if can't read


def extract_metadata_from_filename(wav_path: Path) -> dict:
    """Extract metadata from filename and folder structure."""
    # Path structure: audio_library/CATEGORY/filename.wav
    category = wav_path.parent.name
    clip_id = wav_path.stem
    
    # Extract tags from category
    tags = []
    if category.startswith("C_"):
        tags.append("paloma")
    elif category.startswith("D_"):
        tags.append("cctv")
    elif category.startswith("E_"):
        tags.append("senter")
    elif category.startswith("F_"):
        tags.append("tracker")
    
    # Generic script based on category
    script_map = {
        "A_opening": "Pembukaan live - sapa viewer dan intro tema",
        "B_reset": "Hook - problem statement dan curiosity",
        "C_paloma": "Demo produk Paloma Smart Lock",
        "D_cctv": "Demo produk CCTV Security",
        "E_senter": "Demo produk Senter Multifungsi",
        "F_tracker": "Demo produk GPS Tracker",
        "G_question_hooks": "Question hooks untuk engagement",
        "H_price_safe": "Penjelasan harga dan value",
        "I_trust_safety": "Trust building dan safety",
        "J_idle_filler": "Idle filler saat menunggu",
        "R_reaction_kit": "Reaction kit untuk interaksi",
        "T_bridge": "Bridge transition antar segment",
        "Z_closing_staged": "Closing - thank you dan next schedule",
    }
    
    script = script_map.get(category, f"Audio clip {clip_id}")
    
    return {
        "id": clip_id,
        "category": category,
        "tags": tags,
        "duration_ms": get_wav_duration_ms(wav_path),
        "script": script,
        "scene_hint": "",
    }


def main():
    # Path to audio library (relative to workspace root)
    audio_lib_dir = Path("livetik/apps/worker/static/audio_library")
    index_path = audio_lib_dir / "index.json"
    
    if not audio_lib_dir.exists():
        print(f"ERROR: {audio_lib_dir} not found!")
        return 1
    
    print("Scanning audio library...")
    print(f"Directory: {audio_lib_dir.absolute()}")
    print()
    
    # Find all .wav files
    wav_files = sorted(audio_lib_dir.glob("*/*.wav"))
    
    if not wav_files:
        print("ERROR: No .wav files found in subfolders!")
        return 1
    
    print(f"Found {len(wav_files)} audio files")
    print()
    
    # Build index entries
    index_entries = []
    for wav_path in wav_files:
        metadata = extract_metadata_from_filename(wav_path)
        index_entries.append(metadata)
        print(f"  [{metadata['category']}] {metadata['id']} ({metadata['duration_ms']}ms)")
    
    # Write index.json
    index_data = {
        "version": "1.0",
        "clips": index_entries,
    }
    
    index_path.write_text(
        json.dumps(index_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    print()
    print("=" * 60)
    print(f"✓ Index rebuilt successfully!")
    print(f"  Total clips: {len(index_entries)}")
    print(f"  Index file: {index_path.absolute()}")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart worker: cd apps/worker && uv run python -m banghack")
    print("2. Refresh dashboard: http://localhost:5173/library")
    print()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
