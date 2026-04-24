#!/usr/bin/env python3
"""Test WebSocket audio.list command to debug dashboard issue."""
import asyncio
import json
import websockets


async def test_audio_list():
    uri = "ws://127.0.0.1:8765"
    
    print("=" * 60)
    print("TESTING WEBSOCKET audio.list COMMAND")
    print("=" * 60)
    print()
    
    try:
        async with websockets.connect(uri) as ws:
            print("✓ Connected to worker WebSocket")
            
            # Send audio.list command
            req_id = "test-audio-list-123"
            command = {
                "type": "cmd",
                "name": "audio.list",
                "req_id": req_id,
                "params": {}
            }
            
            print(f"\nSending command: {json.dumps(command, indent=2)}")
            await ws.send(json.dumps(command))
            
            # Wait for response
            print("\nWaiting for response...")
            timeout = 5
            try:
                response_raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                response = json.loads(response_raw)
                
                print(f"\n✓ Received response:")
                print(f"  Type: {response.get('type')}")
                print(f"  OK: {response.get('ok')}")
                
                if response.get('type') == 'cmd_result':
                    result = response.get('result', {})
                    clips = result.get('clips', [])
                    
                    print(f"\n  Clips count: {len(clips)}")
                    
                    if len(clips) > 0:
                        print(f"\n  First 3 clips:")
                        for i, clip in enumerate(clips[:3]):
                            print(f"    [{i+1}] {clip.get('id')} - {clip.get('category')}")
                    else:
                        print("\n  ❌ NO CLIPS RETURNED!")
                        print("\n  DIAGNOSIS:")
                        print("  - Worker loaded index.json with 0 clips")
                        print("  - index.json was rebuilt but worker NOT restarted")
                        print("\n  FIX:")
                        print("  1. Stop worker (CTRL+C)")
                        print("  2. Restart: cd apps/worker && uv run python -m banghack")
                        print("  3. Refresh dashboard")
                else:
                    print(f"\n  Unexpected response type: {response.get('type')}")
                    print(f"  Full response: {json.dumps(response, indent=2)}")
                    
            except asyncio.TimeoutError:
                print(f"\n❌ Timeout after {timeout}s - no response from worker")
                
    except ConnectionRefusedError:
        print("❌ Connection refused - worker not running!")
        print("\nStart worker first:")
        print("  cd apps/worker && uv run python -m banghack")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_audio_list())
