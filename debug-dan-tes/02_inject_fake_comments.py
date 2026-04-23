#!/usr/bin/env python3
"""Inject fake TikTok comments for testing classifier + suggester."""
import asyncio
import json
import random
import time
from pathlib import Path

import websockets

# Test comments covering all intents
TEST_COMMENTS = [
    # Greeting
    ("halo bang", "greeting", "TestUser1"),
    ("hai kak", "greeting", "TestUser2"),
    ("assalamualaikum", "greeting", "TestUser3"),
    
    # Price question
    ("berapa harganya?", "price_question", "TestUser4"),
    ("harga paloma berapa?", "price_question", "TestUser5"),
    ("mahal nggak?", "price_question", "TestUser6"),
    
    # Stock question
    ("masih ada stok?", "stock_question", "TestUser7"),
    ("ready kah?", "stock_question", "TestUser8"),
    ("stok pintu lipat ada?", "stock_question", "TestUser9"),
    
    # Buying intent
    ("mau beli yang paloma", "buying_intent", "TestUser10"),
    ("gimana cara order?", "buying_intent", "TestUser11"),
    ("mau pesan 2", "buying_intent", "TestUser12"),
    
    # Compatibility
    ("bisa buat pintu kayu?", "compatibility", "TestUser13"),
    ("cocok untuk kontrakan?", "compatibility", "TestUser14"),
    ("support pintu aluminium?", "compatibility", "TestUser15"),
    
    # How to use
    ("cara pasangnya gimana?", "how_to_use", "TestUser16"),
    ("tutorial install dong", "how_to_use", "TestUser17"),
    ("cara pakai blendernya?", "how_to_use", "TestUser18"),
    
    # Objection
    ("kemahalan", "objection", "TestUser19"),
    ("kualitas bagus nggak?", "objection", "TestUser20"),
    ("worth it nggak sih?", "objection", "TestUser21"),
    
    # Forbidden contact
    ("wa dong 08123456789", "forbidden_contact", "SpamUser1"),
    ("chat ig aja", "forbidden_contact", "SpamUser2"),
    
    # Forbidden link
    ("cek https://bit.ly/promo", "forbidden_link", "SpamUser3"),
    
    # Spam
    ("follow back dong", "spam", "SpamUser4"),
    ("sub4sub", "spam", "SpamUser5"),
    
    # Empty
    ("", "empty", "TestUser22"),
    
    # Other (no clear intent)
    ("warna apa aja?", "other", "TestUser23"),
    ("garansi berapa lama?", "other", "TestUser24"),
]


async def inject_comments(
    ws_url: str = "ws://localhost:8765",
    interval_s: float = 5.0,
    count: int = 50,
    random_order: bool = True,
) -> None:
    """Inject fake comments via WebSocket."""
    print(f"🔌 Connecting to {ws_url}...")
    
    async with websockets.connect(ws_url) as ws:
        print(f"✅ Connected! Injecting {count} comments (interval={interval_s}s)")
        
        comments = TEST_COMMENTS.copy()
        if random_order:
            random.shuffle(comments)
        
        for i in range(count):
            text, expected_intent, user = comments[i % len(comments)]
            
            # Send fake comment event
            event = {
                "type": "tiktok_event",
                "ts": time.time(),
                "event_type": "comment",
                "user": user,
                "text": text,
                "count": 1,
            }
            
            await ws.send(json.dumps(event))
            print(f"[{i+1}/{count}] 💬 {user}: {text[:50]} (expect: {expected_intent})")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(response)
                if data.get("type") == "comment.classified":
                    actual_intent = data.get("intent", "unknown")
                    confidence = data.get("confidence", 0.0)
                    method = data.get("method", "unknown")
                    match = "✅" if actual_intent == expected_intent else "❌"
                    print(f"    {match} Classified: {actual_intent} ({confidence:.2f}, {method})")
            except asyncio.TimeoutError:
                print("    ⚠️ No response (timeout)")
            
            await asyncio.sleep(interval_s)
        
        print(f"\n✅ Injected {count} comments successfully!")


async def inject_burst(
    ws_url: str = "ws://localhost:8765",
    burst_size: int = 10,
) -> None:
    """Inject burst of comments to test rate limiting."""
    print(f"🔌 Connecting to {ws_url}...")
    
    async with websockets.connect(ws_url) as ws:
        print(f"💥 Injecting burst of {burst_size} comments...")
        
        for i in range(burst_size):
            text, _, user = random.choice(TEST_COMMENTS)
            event = {
                "type": "tiktok_event",
                "ts": time.time(),
                "event_type": "comment",
                "user": f"BurstUser{i}",
                "text": text,
                "count": 1,
            }
            await ws.send(json.dumps(event))
            print(f"[{i+1}/{burst_size}] 💬 {text[:50]}")
        
        print(f"\n✅ Burst complete! Check guardrail rate limiting.")


async def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Inject fake TikTok comments")
    parser.add_argument("--url", default="ws://localhost:8765", help="WebSocket URL")
    parser.add_argument("--count", type=int, default=50, help="Number of comments")
    parser.add_argument("--interval", type=float, default=5.0, help="Interval between comments (seconds)")
    parser.add_argument("--burst", type=int, help="Inject burst of N comments")
    parser.add_argument("--no-random", action="store_true", help="Don't randomize order")
    
    args = parser.parse_args()
    
    if args.burst:
        await inject_burst(args.url, args.burst)
    else:
        await inject_comments(
            args.url,
            args.interval,
            args.count,
            not args.no_random,
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
