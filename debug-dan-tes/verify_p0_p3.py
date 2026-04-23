#!/usr/bin/env python3
"""Verification script for P0-P3.7 implementation."""
import json
import sys
from pathlib import Path

import yaml

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_file_exists(path: Path, description: str) -> bool:
    """Check if a file exists."""
    exists = path.exists()
    status = f"{GREEN}✅{RESET}" if exists else f"{RED}❌{RESET}"
    print(f"{status} {description}: {path}")
    return exists


def check_dir_exists(path: Path, description: str) -> bool:
    """Check if a directory exists."""
    exists = path.is_dir()
    status = f"{GREEN}✅{RESET}" if exists else f"{RED}❌{RESET}"
    print(f"{status} {description}: {path}")
    return exists


def count_yaml_entries(yaml_path: Path, key: str) -> int:
    """Count entries in a YAML file."""
    try:
        with yaml_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return len(data.get(key, []))
    except Exception as e:
        print(f"{RED}❌{RESET} Error reading {yaml_path}: {e}")
        return 0


def main() -> int:
    """Run verification checks."""
    root = Path(__file__).parent
    worker = root / "apps" / "worker"
    controller = root / "apps" / "controller"
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}P0-P3.7 Verification Checklist{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    total_checks = 0
    passed_checks = 0
    
    # P0.1 - Setup deps + env vars
    print(f"\n{BLUE}=== P0.1 - Setup deps + env vars [CC-LIVE-CLIP-001] ==={RESET}\n")
    
    # Check pyproject.toml dependencies
    pyproject = worker / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        deps = ["pyyaml>=6.0.1", "rapidfuzz>=3.9.0", "aiofiles>=24.1.0"]
        for dep in deps:
            total_checks += 1
            if dep in content:
                print(f"{GREEN}✅{RESET} Dependency found: {dep}")
                passed_checks += 1
            else:
                print(f"{RED}❌{RESET} Dependency missing: {dep}")
    
    # Check .env.example
    env_example = root / ".env.example"
    if env_example.exists():
        content = env_example.read_text(encoding="utf-8")
        env_vars = [
            "AUDIO_LIBRARY_DIR",
            "CLIPS_SCRIPT_YAML",
            "PRODUCTS_YAML",
            "REPLY_TEMPLATES_YAML",
            "LIVE_MAX_DURATION_S=7200",
            "REPLY_CACHE_TTL_S=300",
            "REPLY_CACHE_SIMILARITY=0.90",
            "CLASSIFIER_LLM_THRESHOLD=0.80",
        ]
        for var in env_vars:
            total_checks += 1
            if var in content:
                print(f"{GREEN}✅{RESET} Env var found: {var}")
                passed_checks += 1
            else:
                print(f"{RED}❌{RESET} Env var missing: {var}")
    
    # Check __init__.py files
    init_files = [
        worker / "src" / "banghack" / "core" / "audio_library" / "__init__.py",
        worker / "src" / "banghack" / "core" / "classifier" / "__init__.py",
        worker / "src" / "banghack" / "core" / "orchestrator" / "__init__.py",
    ]
    for init_file in init_files:
        total_checks += 1
        if check_file_exists(init_file, "__init__.py"):
            passed_checks += 1
    
    # P0.2 - Audio Library Manager + Adapter
    print(f"\n{BLUE}=== P0.2 - Audio Library Manager + Adapter [CC-LIVE-CLIP-002] ==={RESET}\n")
    
    clips_yaml = worker / "config" / "clips_script.yaml"
    total_checks += 1
    if clips_yaml.exists():
        clip_count = count_yaml_entries(clips_yaml, "clips")
        if clip_count >= 160:
            print(f"{GREEN}✅{RESET} clips_script.yaml has {clip_count} entries (≥160 required)")
            passed_checks += 1
        else:
            print(f"{YELLOW}⚠️{RESET} clips_script.yaml has {clip_count} entries (<160 required)")
    else:
        print(f"{RED}❌{RESET} clips_script.yaml not found")
    
    files_p02 = [
        (worker / "src" / "banghack" / "core" / "audio_library" / "manager.py", "AudioLibraryManager"),
        (worker / "static" / "audio_library" / "index.json", "index.json"),
        (worker / "src" / "banghack" / "adapters" / "audio_library.py", "AudioLibraryAdapter"),
    ]
    for file_path, desc in files_p02:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P0.3 - Generator script + bat
    print(f"\n{BLUE}=== P0.3 - Generator script + bat [CC-LIVE-CLIP-003] ==={RESET}\n")
    
    files_p03 = [
        (worker / "scripts" / "gen_audio_library.py", "gen_audio_library.py"),
        (worker / "scripts" / "gen_audio_library.bat", "gen_audio_library.bat"),
    ]
    for file_path, desc in files_p03:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # Check for generated audio files
    audio_lib_dir = worker / "static" / "audio_library"
    total_checks += 1
    if audio_lib_dir.exists():
        wav_files = list(audio_lib_dir.glob("*.wav"))
        if len(wav_files) >= 10:
            print(f"{GREEN}✅{RESET} Generated audio files: {len(wav_files)} .wav files (≥10 required)")
            passed_checks += 1
        else:
            print(f"{YELLOW}⚠️{RESET} Generated audio files: {len(wav_files)} .wav files (<10 required)")
    else:
        print(f"{RED}❌{RESET} audio_library directory not found")
    
    # P0.4 - WS commands + Svelte AudioLibraryGrid
    print(f"\n{BLUE}=== P0.4 - WS commands + Svelte AudioLibraryGrid [CC-LIVE-CLIP-004] ==={RESET}\n")
    
    main_py = worker / "src" / "banghack" / "main.py"
    total_checks += 1
    if main_py.exists():
        content = main_py.read_text(encoding="utf-8")
        ws_commands = ["audio.list", "audio.play", "audio.stop"]
        found_commands = sum(1 for cmd in ws_commands if cmd in content)
        if found_commands == len(ws_commands):
            print(f"{GREEN}✅{RESET} WS commands in main.py: {found_commands}/{len(ws_commands)}")
            passed_checks += 1
        else:
            print(f"{YELLOW}⚠️{RESET} WS commands in main.py: {found_commands}/{len(ws_commands)}")
    
    files_p04 = [
        (controller / "src" / "lib" / "stores" / "audio_library.ts", "audio_library.ts"),
        (controller / "src" / "lib" / "components" / "AudioLibraryGrid.svelte", "AudioLibraryGrid.svelte"),
    ]
    for file_path, desc in files_p04:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P0.5 - Tests
    print(f"\n{BLUE}=== P0.5 - Tests [CC-LIVE-CLIP-005] ==={RESET}\n")
    
    test_files = [
        (worker / "tests" / "test_audio_library.py", "test_audio_library.py"),
    ]
    for file_path, desc in test_files:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P1.1 - Rules classifier + config
    print(f"\n{BLUE}=== P1.1 - Rules classifier + config [CC-LIVE-CLASSIFIER-001] ==={RESET}\n")
    
    reply_templates = worker / "config" / "reply_templates.yaml"
    total_checks += 1
    if reply_templates.exists():
        content = reply_templates.read_text(encoding="utf-8")
        intents = ["price_question", "stock_question", "greeting", "buying_intent", "compatibility", "how_to_use", "objection"]
        found_intents = sum(1 for intent in intents if intent in content)
        if found_intents >= 7:
            print(f"{GREEN}✅{RESET} reply_templates.yaml has {found_intents}/7+ intents")
            passed_checks += 1
        else:
            print(f"{YELLOW}⚠️{RESET} reply_templates.yaml has {found_intents}/7+ intents")
    
    files_p11 = [
        (worker / "src" / "banghack" / "core" / "classifier" / "rules.py", "rules.py"),
        (worker / "tests" / "test_classifier_rules.py", "test_classifier_rules.py"),
    ]
    for file_path, desc in files_p11:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P1.2 - LLM fallback + integration
    print(f"\n{BLUE}=== P1.2 - LLM fallback + integration [CC-LIVE-CLASSIFIER-002] ==={RESET}\n")
    
    files_p12 = [
        (worker / "src" / "banghack" / "core" / "classifier" / "llm_fallback.py", "llm_fallback.py"),
    ]
    for file_path, desc in files_p12:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P1.3 - DecisionStream Svelte
    print(f"\n{BLUE}=== P1.3 - DecisionStream Svelte [CC-LIVE-CLASSIFIER-003] ==={RESET}\n")
    
    files_p13 = [
        (controller / "src" / "lib" / "components" / "DecisionStream.svelte", "DecisionStream.svelte"),
    ]
    for file_path, desc in files_p13:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P2.1 - Budget Guard
    print(f"\n{BLUE}=== P2.1 - Budget Guard [CC-LIVE-ORCH-001] ==={RESET}\n")
    
    files_p21 = [
        (worker / "src" / "banghack" / "core" / "orchestrator" / "budget_guard.py", "budget_guard.py"),
    ]
    for file_path, desc in files_p21:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P2.2 - Reply Cache + test
    print(f"\n{BLUE}=== P2.2 - Reply Cache + test [CC-LIVE-ORCH-002] ==={RESET}\n")
    
    files_p22 = [
        (worker / "src" / "banghack" / "core" / "orchestrator" / "reply_cache.py", "reply_cache.py"),
        (worker / "tests" / "test_reply_cache.py", "test_reply_cache.py"),
    ]
    for file_path, desc in files_p22:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P2.3 - Suggester + reply_templates
    print(f"\n{BLUE}=== P2.3 - Suggester + reply_templates [CC-LIVE-ORCH-003] ==={RESET}\n")
    
    files_p23 = [
        (worker / "src" / "banghack" / "core" / "orchestrator" / "suggester.py", "suggester.py"),
    ]
    for file_path, desc in files_p23:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P2.4 - WS reply.* + ReplySuggestions
    print(f"\n{BLUE}=== P2.4 - WS reply.* + ReplySuggestions [CC-LIVE-ORCH-004] ==={RESET}\n")
    
    total_checks += 1
    if main_py.exists():
        content = main_py.read_text(encoding="utf-8")
        ws_commands = ["reply.approve", "reply.reject", "reply.regen", "budget.get"]
        found_commands = sum(1 for cmd in ws_commands if cmd in content)
        if found_commands >= 3:  # At least 3 out of 4
            print(f"{GREEN}✅{RESET} WS reply commands in main.py: {found_commands}/{len(ws_commands)}")
            passed_checks += 1
        else:
            print(f"{YELLOW}⚠️{RESET} WS reply commands in main.py: {found_commands}/{len(ws_commands)}")
    
    files_p24 = [
        (controller / "src" / "lib" / "components" / "ReplySuggestions.svelte", "ReplySuggestions.svelte"),
    ]
    for file_path, desc in files_p24:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P2.5 - Output guardrail + test
    print(f"\n{BLUE}=== P2.5 - Output guardrail + test [CC-LIVE-ORCH-005] ==={RESET}\n")
    
    files_p25 = [
        (worker / "tests" / "test_suggester.py", "test_suggester.py"),
    ]
    for file_path, desc in files_p25:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P3.1 - products.yaml + Director state machine
    print(f"\n{BLUE}=== P3.1 - products.yaml + Director state machine [CC-LIVE-DIRECTOR-001] ==={RESET}\n")
    
    files_p31 = [
        (worker / "config" / "products.yaml", "products.yaml"),
        (worker / "src" / "banghack" / "core" / "orchestrator" / "director.py", "director.py"),
    ]
    for file_path, desc in files_p31:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P3.2 - Runsheet loop + anti-repeat
    print(f"\n{BLUE}=== P3.2 - Runsheet loop + anti-repeat [CC-LIVE-DIRECTOR-002] ==={RESET}\n")
    
    director_py = worker / "src" / "banghack" / "core" / "orchestrator" / "director.py"
    total_checks += 1
    if director_py.exists():
        content = director_py.read_text(encoding="utf-8")
        required_methods = ["_run_loop", "live.state", "live.tick"]
        found_methods = sum(1 for method in required_methods if method in content)
        if found_methods == len(required_methods):
            print(f"{GREEN}✅{RESET} Director methods: {found_methods}/{len(required_methods)}")
            passed_checks += 1
        else:
            print(f"{YELLOW}⚠️{RESET} Director methods: {found_methods}/{len(required_methods)}")
    
    # P3.3 - WS live.* + live_state store
    print(f"\n{BLUE}=== P3.3 - WS live.* + live_state store [CC-LIVE-DIRECTOR-003] ==={RESET}\n")
    
    total_checks += 1
    if main_py.exists():
        content = main_py.read_text(encoding="utf-8")
        ws_commands = ["live.start", "live.pause", "live.resume", "live.stop", "live.emergency_stop"]
        found_commands = sum(1 for cmd in ws_commands if cmd in content)
        if found_commands >= 4:  # At least 4 out of 5
            print(f"{GREEN}✅{RESET} WS live commands in main.py: {found_commands}/{len(ws_commands)}")
            passed_checks += 1
        else:
            print(f"{YELLOW}⚠️{RESET} WS live commands in main.py: {found_commands}/{len(ws_commands)}")
    
    files_p33 = [
        (controller / "src" / "lib" / "stores" / "live_state.ts", "live_state.ts"),
    ]
    for file_path, desc in files_p33:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P3.4 - TwoHourTimer + EmergencyStop
    print(f"\n{BLUE}=== P3.4 - TwoHourTimer + EmergencyStop [CC-LIVE-DIRECTOR-004] ==={RESET}\n")
    
    files_p34 = [
        (controller / "src" / "lib" / "components" / "TwoHourTimer.svelte", "TwoHourTimer.svelte"),
        (controller / "src" / "lib" / "components" / "EmergencyStop.svelte", "EmergencyStop.svelte"),
    ]
    for file_path, desc in files_p34:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P3.5 - Tests + P3 acceptance
    print(f"\n{BLUE}=== P3.5 - Tests + P3 acceptance [CC-LIVE-DIRECTOR-005] ==={RESET}\n")
    
    files_p35 = [
        (worker / "tests" / "test_director_state.py", "test_director_state.py"),
    ]
    for file_path, desc in files_p35:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # P3.6 - Health Check Extension
    print(f"\n{BLUE}=== P3.6 - Health Check Extension [Task 19] ==={RESET}\n")
    
    http_server = worker / "src" / "banghack" / "ipc" / "http_server.py"
    total_checks += 1
    if http_server.exists():
        content = http_server.read_text(encoding="utf-8")
        health_checks = ["audio_library_ready", "classifier_ready", "director_ready", "budget_remaining_idr"]
        found_checks = sum(1 for check in health_checks if check in content)
        if found_checks >= 3:  # At least 3 out of 4
            print(f"{GREEN}✅{RESET} Health check fields: {found_checks}/{len(health_checks)}")
            passed_checks += 1
        else:
            print(f"{YELLOW}⚠️{RESET} Health check fields: {found_checks}/{len(health_checks)}")
    
    # P3.7 - Documentation Updates
    print(f"\n{BLUE}=== P3.7 - Documentation Updates [Task 19] ==={RESET}\n")
    
    files_p37 = [
        (root / "docs" / "CHANGELOG.md", "CHANGELOG.md"),
        (root / "docs" / "ARCHITECTURE.md", "ARCHITECTURE.md"),
    ]
    for file_path, desc in files_p37:
        total_checks += 1
        if check_file_exists(file_path, desc):
            passed_checks += 1
    
    # Summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Summary{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    print(f"Total checks: {total_checks}")
    print(f"Passed: {GREEN}{passed_checks}{RESET}")
    print(f"Failed: {RED}{total_checks - passed_checks}{RESET}")
    print(f"Success rate: {GREEN if percentage >= 90 else YELLOW if percentage >= 70 else RED}{percentage:.1f}%{RESET}\n")
    
    if percentage >= 90:
        print(f"{GREEN}✅ P0-P3.7 implementation is COMPLETE!{RESET}\n")
        return 0
    elif percentage >= 70:
        print(f"{YELLOW}⚠️ P0-P3.7 implementation is MOSTLY COMPLETE, but some items need attention.{RESET}\n")
        return 1
    else:
        print(f"{RED}❌ P0-P3.7 implementation is INCOMPLETE. Please review failed checks.{RESET}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
