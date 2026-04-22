"""Health check — validate semua komponen sebelum go-live.

Checks:
  1. ffplay (ffmpeg) — TTS audio playback
  2. Port 8765 (WebSocket) — worker running?
  3. 9router — LLM gateway
  4. LLM roundtrip — actual model call
  5. Cartesia keys — TTS primary
  6. Edge-TTS — TTS fallback
  7. Worker WS commands — bidirectional WS
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import socket
import sys
import time
import traceback
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from project root (2 levels up from scripts/)
_env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(_env_path)

NINEROUTER_BASE = os.getenv("NINEROUTER_BASE_URL", "http://localhost:20128/v1")
NINEROUTER_KEY = os.getenv("NINEROUTER_API_KEY", "sk-dummy-9router")
CARTESIA_KEYS_RAW = os.getenv("CARTESIA_API_KEYS", "")
CARTESIA_VOICE_ID = os.getenv("CARTESIA_VOICE_ID", "")
CARTESIA_MODEL = os.getenv("CARTESIA_MODEL", "sonic-3")
EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "id-ID-ArdiNeural")
WS_HOST = os.getenv("WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("WS_PORT", "8765"))


# ── Helpers ──────────────────────────────────────────────────────────────────

def _ok(msg: str) -> None:
    print(f"   ✅ {msg}")

def _warn(msg: str) -> None:
    print(f"   ⚠️  {msg}")

def _fail(msg: str, detail: str = "") -> None:
    print(f"   ❌ {msg}")
    if detail:
        for line in detail.strip().splitlines():
            print(f"      {line}")

def _section(n: int, total: int, title: str) -> None:
    print(f"\n[{n}/{total}] {title}")
    print("   " + "─" * 50)


# ── Check 1: ffplay ───────────────────────────────────────────────────────────

def check_ffplay() -> bool:
    _section(1, 7, "ffplay (ffmpeg) — TTS audio playback")
    path = (
        shutil.which("ffplay")
        or shutil.which(r"C:\ffmpeg\bin\ffplay.exe")
    )
    if not path:
        _fail(
            "ffplay not found in PATH",
            "Install ffmpeg: https://ffmpeg.org/download.html\n"
            "Or add C:\\ffmpeg\\bin to PATH",
        )
        return False
    try:
        import subprocess
        result = subprocess.run(
            [path, "-version"], capture_output=True, text=True, timeout=5
        )
        version_line = (result.stdout or result.stderr or "").splitlines()[0]
        _ok(f"{version_line}")
        _ok(f"Path: {path}")
        return True
    except Exception as e:
        _fail("ffplay found but failed to run", str(e))
        return False


# ── Check 2: Port 8765 (worker running?) ─────────────────────────────────────

def check_worker_port() -> bool:
    _section(2, 7, f"Port {WS_PORT} — Worker WebSocket running?")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((WS_HOST, WS_PORT))
    sock.close()
    if result == 0:
        _ok(f"Port {WS_PORT} is OPEN — worker is running")
        return True
    else:
        _warn(
            f"Port {WS_PORT} is CLOSED — worker not running\n"
            "   Start worker: scripts\\dev.bat  or  cd apps\\worker && uv run python -m banghack"
        )
        return False


# ── Check 3: 9router ─────────────────────────────────────────────────────────

def check_ninerouter() -> bool:
    _section(3, 7, f"9router — LLM gateway ({NINEROUTER_BASE})")
    try:
        r = requests.get(
            f"{NINEROUTER_BASE}/models",
            headers={"Authorization": f"Bearer {NINEROUTER_KEY}"},
            timeout=5,
        )
        if r.status_code == 200:
            models = r.json().get("data", [])
            _ok(f"{len(models)} model tersedia")
            for m in models[:5]:
                print(f"      · {m.get('id')}")
            if len(models) > 5:
                print(f"      · ... dan {len(models) - 5} lainnya")
            return True
        _fail(
            f"HTTP {r.status_code}",
            f"Response: {r.text[:200]}\n"
            "Pastikan 9router berjalan di localhost:20128",
        )
        return False
    except requests.exceptions.ConnectionError as e:
        _fail(
            "Connection refused — 9router tidak berjalan",
            f"Detail: {e}\n"
            "Jalankan 9router terlebih dahulu",
        )
        return False
    except Exception as e:
        _fail("Unexpected error", traceback.format_exc())
        return False


# ── Check 4: LLM roundtrip ───────────────────────────────────────────────────

async def check_llm_roundtrip() -> bool:
    _section(4, 7, "LLM roundtrip — actual model call via LiteLLM")
    try:
        from litellm import acompletion
    except ImportError:
        _fail("litellm not installed", "Run: uv sync")
        return False

    # Try models in order of preference
    candidates = [
        "openai/kc/kilo-auto/free",
        "openai/KIRO",
        "openai/kc/openai/gpt-4.1",
    ]

    for model in candidates:
        try:
            t0 = time.monotonic()
            resp = await acompletion(
                model=model,
                api_base=NINEROUTER_BASE,
                api_key=NINEROUTER_KEY,
                messages=[{"role": "user", "content": "Jawab 1 kata: halo"}],
                max_tokens=10,
                timeout=20,
            )
            latency = int((time.monotonic() - t0) * 1000)
            text = (resp.choices[0].message.content or "").strip()
            _ok(f"model={model}")
            _ok(f"latency={latency}ms  reply={text!r}")
            return True
        except Exception as e:
            err_short = str(e)[:100]
            print(f"      ⚠️  {model}: {err_short}")

    _fail(
        "All candidate models failed",
        "Cek NINEROUTER_BASE_URL dan NINEROUTER_API_KEY di .env\n"
        "Atau jalankan: scripts\\health.bat setelah 9router aktif",
    )
    return False


# ── Check 5: Cartesia keys ───────────────────────────────────────────────────

def check_cartesia_keys() -> tuple[int, int]:
    _section(5, 7, "Cartesia TTS pool — per-key synth test")
    if not CARTESIA_KEYS_RAW or not CARTESIA_VOICE_ID:
        _warn(
            "CARTESIA_API_KEYS atau CARTESIA_VOICE_ID kosong di .env\n"
            "   TTS akan fallback ke edge-tts (Rp 0)"
        )
        return 0, 0

    keys = [k.strip() for k in CARTESIA_KEYS_RAW.split(",") if k.strip()]
    ok = 0
    for i, key in enumerate(keys, 1):
        preview = f"{key[:8]}...{key[-4:]}"
        try:
            r = requests.post(
                "https://api.cartesia.ai/tts/bytes",
                headers={
                    "Cartesia-Version": "2026-03-01",
                    "X-API-Key": key,
                    "Content-Type": "application/json",
                },
                json={
                    "model_id": CARTESIA_MODEL,
                    "transcript": "halo",
                    "voice": {"mode": "id", "id": CARTESIA_VOICE_ID},
                    "language": "id",
                    "output_format": {
                        "container": "wav",
                        "encoding": "pcm_f32le",
                        "sample_rate": 44100,
                    },
                },
                timeout=15,
            )
            if r.status_code == 200:
                size_kb = len(r.content) / 1024
                _ok(f"[{i}] {preview} → {size_kb:.1f} KB audio")
                ok += 1
            else:
                _fail(
                    f"[{i}] {preview} → HTTP {r.status_code}",
                    f"Response: {r.text[:150]}",
                )
        except Exception as e:
            _fail(f"[{i}] {preview}", str(e))
    return ok, len(keys)


# ── Check 6: Edge-TTS ────────────────────────────────────────────────────────

async def check_edge_tts() -> bool:
    _section(6, 7, f"Edge-TTS fallback ({EDGE_TTS_VOICE})")
    try:
        import edge_tts
    except ImportError:
        _fail("edge-tts not installed", "Run: uv sync")
        return False
    try:
        out = Path("scripts/_health_edge.mp3")
        out.parent.mkdir(exist_ok=True)
        communicate = edge_tts.Communicate("Test suara Indonesia", EDGE_TTS_VOICE)
        await communicate.save(str(out))
        size_kb = out.stat().st_size / 1024
        out.unlink(missing_ok=True)
        _ok(f"{size_kb:.1f} KB audio generated")
        return True
    except Exception as e:
        _fail("edge-tts failed", traceback.format_exc())
        return False


# ── Check 7: Worker WS commands ──────────────────────────────────────────────

async def check_worker_commands() -> bool:
    _section(7, 7, "Worker WS commands — bidirectional test")
    try:
        import websockets
    except ImportError:
        _warn("websockets not installed — skipping WS command test")
        return True

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    if sock.connect_ex((WS_HOST, WS_PORT)) != 0:
        sock.close()
        _warn("Worker not running — skipping WS command test")
        return True
    sock.close()

    try:
        async with websockets.connect(
            f"ws://{WS_HOST}:{WS_PORT}", open_timeout=5
        ) as ws:
            hello = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
            commands = hello.get("commands", [])
            _ok(f"{len(commands)} commands registered")

            # Test test_guardrail (fast, no external deps)
            req_id = "health-guardrail-test"
            await ws.send(json.dumps({
                "type": "cmd", "name": "test_guardrail", "req_id": req_id,
                "params": {"user": "TestUser", "text": "halo bang"},
            }))
            # Drain until cmd_result
            for _ in range(30):
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
                if msg.get("type") == "cmd_result" and msg.get("req_id") == req_id:
                    if msg.get("ok"):
                        result = msg.get("result", {})
                        _ok(f"test_guardrail: accepted={result.get('accepted')} reason={result.get('reason')!r}")
                    else:
                        _fail("test_guardrail failed", msg.get("error", ""))
                    break

            # Check key commands present
            required = ["test_llm_custom", "test_cartesia_all", "set_reply_enabled", "set_dry_run"]
            missing = [c for c in required if c not in commands]
            if missing:
                _warn(f"Missing commands: {missing}")
            else:
                _ok("All required commands present")
            return True
    except Exception as e:
        _fail("WS connection failed", traceback.format_exc())
        return False


# ── Main ─────────────────────────────────────────────────────────────────────

async def main() -> int:
    print()
    print("=" * 60)
    print("  BANG HACK — HEALTH CHECK")
    print(f"  .env: {_env_path}")
    print("=" * 60)

    r1 = check_ffplay()
    r2 = check_worker_port()
    r3 = check_ninerouter()
    r4 = await check_llm_roundtrip()
    r5_ok, r5_total = check_cartesia_keys()
    r6 = await check_edge_tts()
    r7 = await check_worker_commands()

    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  ffplay         : {'✅' if r1 else '❌'}")
    print(f"  Worker port    : {'✅ running' if r2 else '⚠️  not running'}")
    print(f"  9router        : {'✅' if r3 else '❌'}")
    print(f"  LLM roundtrip  : {'✅' if r4 else '❌'}")
    if r5_total > 0:
        print(f"  Cartesia pool  : {r5_ok}/{r5_total} key aktif {'✅' if r5_ok > 0 else '❌'}")
    else:
        print(f"  Cartesia pool  : ⚠️  tidak dikonfigurasi (edge-tts fallback)")
    print(f"  Edge-TTS       : {'✅' if r6 else '❌'}")
    print(f"  WS commands    : {'✅' if r7 else '❌'}")
    print("=" * 60)

    # Determine readiness
    tts_ok = r5_ok > 0 or r6
    llm_ok = r3 and r4
    core_ok = r1 and llm_ok and tts_ok

    if core_ok:
        print("  🟢 READY — boleh enable REPLY_ENABLED=true")
        if not r2:
            print("  ℹ️  Start worker dulu: scripts\\dev.bat")
        return 0
    else:
        print("  🔴 NOT READY — fix error di atas dulu")
        if not r1:
            print("  → Install ffmpeg: https://ffmpeg.org/download.html")
        if not r3:
            print("  → Jalankan 9router di localhost:20128")
        if not r4:
            print("  → Cek NINEROUTER_API_KEY di .env")
        if not tts_ok:
            print("  → Set CARTESIA_API_KEYS atau pastikan internet untuk edge-tts")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
