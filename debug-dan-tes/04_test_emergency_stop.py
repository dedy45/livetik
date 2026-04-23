#!/usr/bin/env python3
"""Test emergency stop latency - must be <500ms."""
import asyncio
import json
import time
from pathlib import Path

import websockets


async def test_emergency_stop(
    ws_url: str = "ws://localhost:8765",
    iterations: int = 10,
) -> None:
    """Test emergency stop latency multiple times."""
    print(f"\n{'='*60}")
    print(f"🚨 EMERGENCY STOP LATENCY TEST")
    print(f"{'='*60}\n")
    print(f"Testing {iterations} iterations...\n")
    
    latencies = []
    
    for i in range(iterations):
        print(f"[{i+1}/{iterations}] Testing emergency stop...")
        
        async with websockets.connect(ws_url) as ws:
            # Start live session
            start_cmd = {"type": "live.start"}
            await ws.send(json.dumps(start_cmd))
            
            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"  ▶️ Live started: {data.get('type')}")
            
            # Wait for audio to start playing
            await asyncio.sleep(2)
            
            # Trigger emergency stop and measure latency
            stop_start = time.time()
            stop_cmd = {"type": "live.emergency_stop", "operator_id": "latency_test"}
            await ws.send(json.dumps(stop_cmd))
            
            # Wait for emergency stop confirmation
            while True:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(response)
                if data.get("type") == "director.emergency_stopped":
                    stop_end = time.time()
                    latency_ms = (stop_end - stop_start) * 1000
                    latencies.append(latency_ms)
                    
                    status = "✅ PASS" if latency_ms < 500 else "❌ FAIL"
                    print(f"  🚨 Emergency stop latency: {latency_ms:.1f}ms {status}")
                    break
            
            # Wait before next iteration
            await asyncio.sleep(1)
    
    # Calculate statistics
    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    pass_count = sum(1 for l in latencies if l < 500)
    pass_rate = (pass_count / len(latencies)) * 100
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTS")
    print(f"{'='*60}\n")
    print(f"Iterations: {len(latencies)}")
    print(f"Average latency: {avg_latency:.1f}ms")
    print(f"Min latency: {min_latency:.1f}ms")
    print(f"Max latency: {max_latency:.1f}ms")
    print(f"Pass rate: {pass_rate:.1f}% ({pass_count}/{len(latencies)})")
    
    if pass_rate == 100:
        print(f"\n✅ ALL TESTS PASSED - Emergency stop <500ms requirement met!")
    elif pass_rate >= 80:
        print(f"\n⚠️ MOSTLY PASSING - {pass_rate:.0f}% tests passed")
    else:
        print(f"\n❌ TESTS FAILED - Only {pass_rate:.0f}% tests passed")
    
    print(f"\nLatency distribution:")
    for i, lat in enumerate(latencies, 1):
        status = "✅" if lat < 500 else "❌"
        print(f"  {status} Test {i}: {lat:.1f}ms")
    
    # Save results
    report_file = Path(__file__).parent / "emergency_stop_latency_report.json"
    with report_file.open("w", encoding="utf-8") as f:
        json.dump({
            "iterations": len(latencies),
            "latencies_ms": latencies,
            "avg_latency_ms": avg_latency,
            "min_latency_ms": min_latency,
            "max_latency_ms": max_latency,
            "pass_count": pass_count,
            "pass_rate_pct": pass_rate,
        }, f, indent=2)
    print(f"\n📄 Report saved to: {report_file}")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test emergency stop latency")
    parser.add_argument("--url", default="ws://localhost:8765", help="WebSocket URL")
    parser.add_argument("--iterations", type=int, default=10, help="Number of test iterations")
    
    args = parser.parse_args()
    
    await test_emergency_stop(args.url, args.iterations)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
