#!/usr/bin/env python3
"""Quick health check for worker"""
import asyncio
import httpx

async def check_health():
    """Check worker health endpoint"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:8766/health")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Worker is HEALTHY")
                print(f"\nHealth Status:")
                print(f"  TTS Ready: {data.get('tts_ready', False)}")
                print(f"  Cartesia Pool: {data.get('cartesia_pool_size', 0)} keys")
                print(f"  Audio Library: {data.get('audio_library_ready', False)}")
                print(f"  Classifier Ready: {data.get('classifier_ready', False)}")
                print(f"  Director Ready: {data.get('director_ready', False)}")
                print(f"  Budget Remaining: Rp {data.get('budget_remaining_idr', 0):.0f}")
                
                if 'llm_tiers' in data:
                    print(f"\nLLM Tiers:")
                    for tier in data['llm_tiers']:
                        print(f"  {tier['tier']}: {tier['model']}")
                
                return True
            else:
                print(f"❌ Worker returned status {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("❌ Worker is NOT RUNNING")
        print("Start worker with: cd apps/worker && uv run python -m banghack.main")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(check_health())
