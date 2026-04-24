#!/usr/bin/env python3
"""Quick verification script for v0.4 MASTER FIX PATCH implementation."""
import sys
from pathlib import Path

def check_file(path: str, description: str) -> bool:
    """Check if file exists."""
    p = Path(path)
    exists = p.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def main() -> int:
    """Run verification checks."""
    print("🔍 Verifying v0.4 MASTER FIX PATCH Implementation\n")
    
    checks = [
        # Frontend stores
        ("apps/controller/src/lib/stores/ws.svelte.ts", "WebSocket store"),
        ("apps/controller/src/lib/stores/audio_library.svelte.ts", "Audio library store"),
        
        # Frontend components
        ("apps/controller/src/lib/components/AudioLibraryGrid.svelte", "Audio library grid"),
        ("apps/controller/src/lib/components/DecisionStream.svelte", "Decision stream"),
        ("apps/controller/src/lib/components/ReplySuggestions.svelte", "Reply suggestions"),
        ("apps/controller/src/lib/components/TwoHourTimer.svelte", "Two hour timer"),
        ("apps/controller/src/lib/components/EmergencyStop.svelte", "Emergency stop"),
        
        # Frontend routes
        ("apps/controller/src/routes/+page.svelte", "Dashboard route"),
        ("apps/controller/src/routes/library/+page.svelte", "Library route"),
        ("apps/controller/src/routes/live/+page.svelte", "Live route"),
        
        # Backend
        ("apps/worker/src/banghack/main.py", "Worker main.py"),
        ("apps/worker/src/banghack/core/orchestrator/suggester.py", "Suggester"),
        ("apps/worker/src/banghack/core/orchestrator/director.py", "Live director"),
        ("apps/worker/src/banghack/core/audio_library/manager.py", "Audio library manager"),
    ]
    
    results = [check_file(path, desc) for path, desc in checks]
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} files found")
    
    if all(results):
        print("\n✅ All files present! Ready to test.")
        print("\nNext steps:")
        print("1. cd apps/worker && uv sync")
        print("2. cd apps/controller && pnpm install")
        print("3. Terminal 1: cd apps/worker && uv run python -m banghack.main")
        print("4. Terminal 2: cd apps/controller && pnpm dev")
        print("5. Open http://127.0.0.1:5173")
        return 0
    else:
        print("\n❌ Some files missing. Check implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
