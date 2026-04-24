#!/usr/bin/env python3
"""Test audio routing to verify OBS integration.

Usage:
    python scripts/test_audio_routing.py
    
This script:
1. Checks if VB-CABLE is installed
2. Verifies .env configuration
3. Plays a test tone to configured device
4. Provides troubleshooting guidance
"""
import os
import sys
from pathlib import Path

# Add worker to path
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "worker" / "src"))

import sounddevice as sd
import numpy as np
from dotenv import load_dotenv

# Load .env from repo root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded .env from {env_path}")
else:
    print(f"⚠ No .env found at {env_path}")

print("\n" + "=" * 70)
print("AUDIO ROUTING TEST")
print("=" * 70)

# Check VB-CABLE installation
print("\n1. Checking VB-CABLE installation...")
devices = sd.query_devices()
cable_devices = [d for d in devices if "cable" in d.get("name", "").lower()]

if cable_devices:
    print(f"✓ Found {len(cable_devices)} VB-CABLE device(s):")
    for d in cable_devices:
        print(f"  - {d.get('name')}")
else:
    print("✗ VB-CABLE not found!")
    print("  Install from: https://vb-audio.com/Cable/")
    sys.exit(1)

# Check .env configuration
print("\n2. Checking .env configuration...")
device_name = os.getenv("AUDIO_OUTPUT_DEVICE", "").strip()
device_index = os.getenv("AUDIO_OUTPUT_DEVICE_INDEX", "").strip()

if device_index.isdigit():
    print(f"✓ AUDIO_OUTPUT_DEVICE_INDEX={device_index}")
    target_device = int(device_index)
elif device_name:
    print(f"✓ AUDIO_OUTPUT_DEVICE={device_name}")
    # Find matching device
    target_device = None
    for i, d in enumerate(devices):
        if d.get("max_output_channels", 0) > 0:
            if device_name.lower() in d.get("name", "").lower():
                target_device = i
                print(f"  Matched device [{i}]: {d.get('name')}")
                break
    if target_device is None:
        print(f"✗ Device '{device_name}' not found!")
        print("  Run: python scripts/list_audio_devices.py")
        sys.exit(1)
else:
    print("⚠ No AUDIO_OUTPUT_DEVICE configured")
    print("  Will use system default (NOT recommended for OBS)")
    target_device = None

# Play test tone
print("\n3. Playing test tone (440 Hz, 2 seconds)...")
print("   Check OBS audio meter for activity!")

duration = 2.0
sample_rate = 44100
frequency = 440.0

# Generate sine wave
t = np.linspace(0, duration, int(sample_rate * duration), False)
tone = 0.3 * np.sin(2 * np.pi * frequency * t)

try:
    sd.play(tone, sample_rate, device=target_device)
    sd.wait()
    print("✓ Test tone played successfully")
except Exception as e:
    print(f"✗ Playback failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("VERIFICATION CHECKLIST")
print("=" * 70)
print("[ ] OBS audio meter showed activity during test tone")
print("[ ] Audio did NOT play through laptop speakers")
print("[ ] OBS Audio Input Capture source = 'CABLE Output'")
print("[ ] OBS Advanced Audio Properties → Monitor = 'Monitor and Output'")
print("\nIf all checked → READY FOR LIVE")
print("If any failed → Check SOP document for troubleshooting")
print("=" * 70)
