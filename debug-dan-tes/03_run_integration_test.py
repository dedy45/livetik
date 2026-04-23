#!/usr/bin/env python3
"""30-minute integration test runner for P0-P3 acceptance criteria."""
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime

import websockets


class IntegrationTestRunner:
    def __init__(self, ws_url: str = "ws://localhost:8765"):
        self.ws_url = ws_url
        self.ws = None
        self.metrics = {
            "start_time": 0.0,
            "end_time": 0.0,
            "phases_seen": set(),
            "clips_played": [],
            "comments_injected": 0,
            "comments_classified": 0,
            "suggestions_generated": 0,
            "errors": [],
            "emergency_stop_latency_ms": None,
        }
        self.test_comments = [
            ("halo bang", "greeting"),
            ("berapa harganya?", "price_question"),
            ("masih ada stok?", "stock_question"),
            ("mau beli", "buying_intent"),
            ("cara pasangnya gimana?", "how_to_use"),
            ("kemahalan", "objection"),
        ]
    
    async def connect(self):
        """Connect to worker WebSocket."""
        print(f"🔌 Connecting to {self.ws_url}...")
        self.ws = await websockets.connect(self.ws_url)
        print("✅ Connected!")
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        if self.ws:
            await self.ws.close()
            print("🔌 Disconnected")
    
    async def send_command(self, cmd: dict) -> dict:
        """Send command and wait for response."""
        await self.ws.send(json.dumps(cmd))
        response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
        return json.loads(response)
    
    async def listen_events(self):
        """Listen for events and update metrics."""
        try:
            while True:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                data = json.loads(msg)
                event_type = data.get("type", "")
                
                if event_type == "live.state":
                    phase = data.get("phase", "")
                    if phase:
                        self.metrics["phases_seen"].add(phase)
                
                elif event_type == "audio.now":
                    clip_id = data.get("clip_id", "")
                    self.metrics["clips_played"].append({
                        "clip_id": clip_id,
                        "ts": time.time(),
                    })
                
                elif event_type == "comment.classified":
                    self.metrics["comments_classified"] += 1
                
                elif event_type == "reply.suggested":
                    self.metrics["suggestions_generated"] += 1
                
                elif event_type.startswith("error."):
                    self.metrics["errors"].append({
                        "type": event_type,
                        "ts": time.time(),
                        "detail": data.get("detail", ""),
                    })
        
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print(f"⚠️ Event listener error: {e}")
    
    async def inject_comment(self, text: str, user: str):
        """Inject a fake comment."""
        event = {
            "type": "tiktok_event",
            "ts": time.time(),
            "event_type": "comment",
            "user": user,
            "text": text,
            "count": 1,
        }
        await self.ws.send(json.dumps(event))
        self.metrics["comments_injected"] += 1
    
    async def run_test(self, duration_s: int = 1800):
        """Run 30-minute integration test."""
        print(f"\n{'='*60}")
        print(f"🧪 INTEGRATION TEST - {duration_s}s ({duration_s//60} minutes)")
        print(f"{'='*60}\n")
        
        await self.connect()
        
        # Start event listener
        listener_task = asyncio.create_task(self.listen_events())
        
        # Start live session
        print("▶️ Starting live session...")
        self.metrics["start_time"] = time.time()
        start_cmd = {"type": "live.start"}
        await self.send_command(start_cmd)
        print("✅ Live session started!\n")
        
        # Inject comments periodically
        comment_interval = 10  # Every 10 seconds
        next_comment_time = time.time() + comment_interval
        comment_idx = 0
        
        # Run for specified duration
        test_start = time.time()
        while time.time() - test_start < duration_s:
            elapsed = time.time() - test_start
            remaining = duration_s - elapsed
            
            # Progress update every 60s
            if int(elapsed) % 60 == 0 and int(elapsed) > 0:
                print(f"⏱️ [{int(elapsed//60)}m] Progress: {len(self.metrics['clips_played'])} clips, "
                      f"{self.metrics['comments_classified']} classified, "
                      f"{self.metrics['suggestions_generated']} suggestions")
            
            # Inject comment
            if time.time() >= next_comment_time:
                text, intent = self.test_comments[comment_idx % len(self.test_comments)]
                user = f"TestUser{comment_idx}"
                await self.inject_comment(text, user)
                comment_idx += 1
                next_comment_time = time.time() + comment_interval
            
            # Test emergency stop at 15 minutes
            if 890 < elapsed < 910 and self.metrics["emergency_stop_latency_ms"] is None:
                print("\n🚨 Testing emergency stop...")
                stop_start = time.time()
                stop_cmd = {"type": "live.emergency_stop", "operator_id": "test_runner"}
                await self.send_command(stop_cmd)
                stop_latency = (time.time() - stop_start) * 1000
                self.metrics["emergency_stop_latency_ms"] = stop_latency
                print(f"⏱️ Emergency stop latency: {stop_latency:.1f}ms")
                
                # Restart after 5s
                await asyncio.sleep(5)
                print("▶️ Restarting live session...")
                await self.send_command(start_cmd)
            
            await asyncio.sleep(0.5)
        
        # Stop live session
        print("\n⏹️ Stopping live session...")
        stop_cmd = {"type": "live.stop"}
        await self.send_command(stop_cmd)
        self.metrics["end_time"] = time.time()
        
        # Stop listener
        listener_task.cancel()
        
        await self.disconnect()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report."""
        duration = self.metrics["end_time"] - self.metrics["start_time"]
        
        print(f"\n{'='*60}")
        print(f"📊 TEST REPORT")
        print(f"{'='*60}\n")
        
        print(f"⏱️ Duration: {duration:.1f}s ({duration/60:.1f} minutes)")
        print(f"🎬 Phases seen: {len(self.metrics['phases_seen'])} - {sorted(self.metrics['phases_seen'])}")
        print(f"🔊 Clips played: {len(self.metrics['clips_played'])}")
        print(f"💬 Comments injected: {self.metrics['comments_injected']}")
        print(f"🏷️ Comments classified: {self.metrics['comments_classified']}")
        print(f"💡 Suggestions generated: {self.metrics['suggestions_generated']}")
        print(f"❌ Errors: {len(self.metrics['errors'])}")
        
        if self.metrics["emergency_stop_latency_ms"]:
            latency = self.metrics["emergency_stop_latency_ms"]
            status = "✅ PASS" if latency < 500 else "❌ FAIL"
            print(f"🚨 Emergency stop latency: {latency:.1f}ms {status}")
        
        print(f"\n{'='*60}")
        print(f"ACCEPTANCE CRITERIA VERIFICATION")
        print(f"{'='*60}\n")
        
        # P3.1: Timer runs
        timer_ok = duration >= 1700  # At least 28 minutes
        print(f"{'✅' if timer_ok else '❌'} P3.1: Timer runs for full duration")
        
        # P3.2: Opening clip auto-play
        opening_ok = len(self.metrics['clips_played']) > 0
        print(f"{'✅' if opening_ok else '❌'} P3.2: Opening clip auto-played")
        
        # P3.3: Phases auto-advance
        phases_ok = len(self.metrics['phases_seen']) >= 3
        print(f"{'✅' if phases_ok else '❌'} P3.3: Phases auto-advance (saw {len(self.metrics['phases_seen'])} phases)")
        
        # P3.4: OBS scene switch (manual)
        print(f"⚠️ P3.4: OBS scene switch (MANUAL - not automated)")
        
        # P3.5: Anti-repeat 20 min
        print(f"⚠️ P3.5: Anti-repeat 20 min (needs separate test)")
        
        # P3.6: Emergency stop <500ms
        if self.metrics["emergency_stop_latency_ms"]:
            emergency_ok = self.metrics["emergency_stop_latency_ms"] < 500
            print(f"{'✅' if emergency_ok else '❌'} P3.6: Emergency stop <500ms ({self.metrics['emergency_stop_latency_ms']:.1f}ms)")
        else:
            print(f"⚠️ P3.6: Emergency stop not tested")
        
        # P3.7: Hard-stop at max_duration
        print(f"⚠️ P3.7: Hard-stop at max_duration (needs 2-hour test)")
        
        # Error check
        no_errors = len(self.metrics['errors']) == 0
        print(f"{'✅' if no_errors else '❌'} No errors during test")
        
        if self.metrics['errors']:
            print(f"\n⚠️ Errors encountered:")
            for err in self.metrics['errors'][:5]:
                print(f"  - {err['type']}: {err['detail']}")
        
        # Save report to file
        report_file = Path(__file__).parent / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with report_file.open("w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2, default=str)
        print(f"\n📄 Full report saved to: {report_file}")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run integration test")
    parser.add_argument("--url", default="ws://localhost:8765", help="WebSocket URL")
    parser.add_argument("--duration", type=int, default=1800, help="Test duration in seconds (default: 1800 = 30 min)")
    
    args = parser.parse_args()
    
    runner = IntegrationTestRunner(args.url)
    await runner.run_test(args.duration)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
