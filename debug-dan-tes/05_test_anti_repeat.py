#!/usr/bin/env python3
"""Test anti-repeat 20-minute window - clips should not repeat within 1200s."""
import asyncio
import json
import time
from pathlib import Path
from collections import defaultdict

import websockets


async def test_anti_repeat(
    ws_url: str = "ws://localhost:8765",
    duration_s: int = 1800,  # 30 minutes
    window_s: int = 1200,  # 20 minutes
) -> None:
    """Test that clips don't repeat within 20-minute window."""
    print(f"\n{'='*60}")
    print(f"🔁 ANTI-REPEAT TEST (20-minute window)")
    print(f"{'='*60}\n")
    print(f"Testing for {duration_s}s ({duration_s//60} minutes)")
    print(f"Anti-repeat window: {window_s}s ({window_s//60} minutes)\n")
    
    clip_history = []  # List of (clip_id, timestamp)
    violations = []  # List of violations
    
    async with websockets.connect(ws_url) as ws:
        # Start live session
        print("▶️ Starting live session...")
        start_cmd = {"type": "live.start"}
        await ws.send(json.dumps(start_cmd))
        
        # Wait for start confirmation
        response = await asyncio.wait_for(ws.recv(), timeout=5.0)
        print(f"✅ Live started!\n")
        
        test_start = time.time()
        last_progress = 0
        
        # Listen for audio.now events
        while time.time() - test_start < duration_s:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                data = json.loads(msg)
                
                if data.get("type") == "audio.now":
                    clip_id = data.get("clip_id", "")
                    current_time = time.time()
                    
                    # Check if this clip was played within the window
                    for prev_clip_id, prev_time in clip_history:
                        if prev_clip_id == clip_id:
                            time_since = current_time - prev_time
                            if time_since < window_s:
                                violations.append({
                                    "clip_id": clip_id,
                                    "time_since_s": time_since,
                                    "timestamp": current_time,
                                })
                                print(f"❌ VIOLATION: {clip_id} repeated after {time_since:.0f}s (< {window_s}s)")
                    
                    # Add to history
                    clip_history.append((clip_id, current_time))
                    print(f"🔊 Clip played: {clip_id} (total: {len(clip_history)})")
                
                # Progress update every 60s
                elapsed = time.time() - test_start
                if int(elapsed) // 60 > last_progress:
                    last_progress = int(elapsed) // 60
                    print(f"⏱️ [{last_progress}m] Progress: {len(clip_history)} clips, {len(violations)} violations")
            
            except asyncio.TimeoutError:
                pass
        
        # Stop live session
        print("\n⏹️ Stopping live session...")
        stop_cmd = {"type": "live.stop"}
        await ws.send(json.dumps(stop_cmd))
    
    # Analyze results
    print(f"\n{'='*60}")
    print(f"📊 RESULTS")
    print(f"{'='*60}\n")
    
    total_clips = len(clip_history)
    unique_clips = len(set(c[0] for c in clip_history))
    violation_count = len(violations)
    
    print(f"Total clips played: {total_clips}")
    print(f"Unique clips: {unique_clips}")
    print(f"Violations: {violation_count}")
    
    if violation_count == 0:
        print(f"\n✅ ALL TESTS PASSED - No clips repeated within {window_s}s window!")
    else:
        print(f"\n❌ TESTS FAILED - {violation_count} violations found")
        print(f"\nViolation details:")
        for v in violations:
            print(f"  - {v['clip_id']}: repeated after {v['time_since_s']:.0f}s")
    
    # Clip frequency analysis
    clip_counts = defaultdict(int)
    for clip_id, _ in clip_history:
        clip_counts[clip_id] += 1
    
    print(f"\nClip frequency distribution:")
    for clip_id, count in sorted(clip_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {clip_id}: {count} times")
    
    # Time-based analysis
    if total_clips > 1:
        avg_interval = (clip_history[-1][1] - clip_history[0][1]) / (total_clips - 1)
        print(f"\nAverage interval between clips: {avg_interval:.1f}s")
    
    # Save report
    report_file = Path(__file__).parent / "anti_repeat_report.json"
    with report_file.open("w", encoding="utf-8") as f:
        json.dump({
            "duration_s": duration_s,
            "window_s": window_s,
            "total_clips": total_clips,
            "unique_clips": unique_clips,
            "violation_count": violation_count,
            "violations": violations,
            "clip_counts": dict(clip_counts),
        }, f, indent=2, default=str)
    print(f"\n📄 Report saved to: {report_file}")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test anti-repeat window")
    parser.add_argument("--url", default="ws://localhost:8765", help="WebSocket URL")
    parser.add_argument("--duration", type=int, default=1800, help="Test duration in seconds (default: 1800 = 30 min)")
    parser.add_argument("--window", type=int, default=1200, help="Anti-repeat window in seconds (default: 1200 = 20 min)")
    
    args = parser.parse_args()
    
    await test_anti_repeat(args.url, args.duration, args.window)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
