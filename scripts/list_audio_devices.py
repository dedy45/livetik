#!/usr/bin/env python3
"""List available audio devices for AUDIO_OUTPUT_DEVICE configuration.

Usage:
    python scripts/list_audio_devices.py
    
Output shows device index and name for .env configuration.
"""
import sounddevice as sd

print("=" * 70)
print("AUDIO OUTPUT DEVICES (untuk .env AUDIO_OUTPUT_DEVICE)")
print("=" * 70)

devices = sd.query_devices()
for i, device in enumerate(devices):
    # Only show output devices
    if device.get("max_output_channels", 0) > 0:
        name = device.get("name", "Unknown")
        channels = device.get("max_output_channels", 0)
        sample_rate = device.get("default_samplerate", 0)
        
        # Highlight VB-CABLE devices
        marker = " ← VB-CABLE" if "cable" in name.lower() else ""
        
        print(f"\n[{i}] {name}{marker}")
        print(f"    Channels: {channels}, Sample Rate: {sample_rate} Hz")

print("\n" + "=" * 70)
print("CARA PAKAI:")
print("=" * 70)
print("1. Pilih device yang mau dipakai (biasanya 'CABLE Input')")
print("2. Tambahkan ke .env:")
print("   AUDIO_OUTPUT_DEVICE=CABLE Input")
print("   atau")
print("   AUDIO_OUTPUT_DEVICE_INDEX=<nomor index>")
print("\n3. Restart worker")
print("=" * 70)
