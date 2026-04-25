"""Main entry — P3: TikTok read + LLM + TTS reply loop + bidirectional WS commands."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, NoReturn

import httpx
import uvicorn
from dotenv import load_dotenv

from .adapters.audio_library import AudioLibraryAdapter
from .core.classifier.rules import classify as rules_classify
from .core.orchestrator.budget_guard import BudgetGuard
from .core.orchestrator.reply_cache import ReplyCache
from .core.orchestrator.director import LiveDirector
from .core.orchestrator.suggester import Suggester
from .core.classifier.llm_fallback import classify_with_llm
from .adapters.cartesia_pool import CartesiaPool
from .adapters.llm import LLMAdapter
from .adapters.tiktok import TikTokAdapter, TTEvent
from .adapters.tts import TTSAdapter
from .core.audio_library.manager import AudioLibraryManager
from .core.config_store import load_state, save_state, read_env, write_env
from .core.cost import CostDay, CostTracker
from .core.guardrail import Guardrail
from .core.persona import load_persona
from .core.queue import ReplyJob, ReplyQueue
from .core.tiktok_supervisor import TikTokSupervisor
from .ipc.audio import list_devices
from .ipc.http_server import create_app
from .ipc.ws_server import WSServer

# Load .env from repo root (4 levels up from this file)
_env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
load_dotenv(_env_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("banghack")

TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME", "").strip().lstrip("@")
HTTP_HOST = os.getenv("HTTP_HOST", "127.0.0.1")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8766"))
HEARTBEAT_INTERVAL_S = 5

# Mutable runtime flags — toggled via WS commands without restart
_flags: dict[str, bool] = {
    "REPLY_ENABLED": os.getenv("REPLY_ENABLED", "false").lower() == "true",
    "DRY_RUN": os.getenv("DRY_RUN", "false").lower() == "true",
}

# Restore runtime flags dari .state.json
_saved_state = load_state()
_flags["REPLY_ENABLED"] = bool(_saved_state.get("reply_enabled", _flags["REPLY_ENABLED"]))
_flags["DRY_RUN"] = bool(_saved_state.get("dry_run", _flags["DRY_RUN"]))


async def _run_http(llm: LLMAdapter, audio_lib_manager: Any = None, live_director: Any = None, cost: Any = None) -> None:
    """Run FastAPI HTTP server for config/model API."""
    from .core.classifier.rules import _INTENTS
    classifier_rules_count = len([i for i in _INTENTS if i[0] not in ("empty",)])
    app = create_app(
        llm,
        audio_lib_manager=audio_lib_manager,
        classifier_rules_count=classifier_rules_count,
        live_director=live_director,
        cost_tracker=cost,
    )
    config = uvicorn.Config(
        app, host=HTTP_HOST, port=HTTP_PORT,
        log_level="warning", access_log=False,
    )
    server = uvicorn.Server(config)
    await server.serve()


class State:
    def __init__(self) -> None:
        self.status: str = "idle"
        self.start_ts: float = time.time()
        self.comments: int = 0
        self.replies: int = 0
        self.gifts: int = 0
        self.joins: int = 0
        self.viewers: int = 0
        self.latencies_ms: list[int] = []

    def record_latency(self, ms: int) -> None:
        self.latencies_ms.append(ms)
        if len(self.latencies_ms) > 100:
            self.latencies_ms.pop(0)

    def p95_latency(self) -> int:
        if not self.latencies_ms:
            return 0
        arr = sorted(self.latencies_ms)
        return arr[int(len(arr) * 0.95)]


async def main() -> NoReturn:
    log.info("🎙️ Bang Hack Worker v0.3.0-dev (P2-C) starting")
    log.info(
        "REPLY_ENABLED=%s DRY_RUN=%s",
        _flags["REPLY_ENABLED"], _flags["DRY_RUN"],
    )

    ws = WSServer(host="127.0.0.1", port=8765)
    await ws.start()

    def _wrap_cmd(name: str, category: str, handler):  # type: ignore[no-untyped-def]
        """Wrap command: broadcast error_event on exception, then re-raise for cmd_result."""
        async def wrapped(p: dict[str, object]) -> dict[str, object]:
            try:
                return await handler(p)
            except Exception as e:
                await ws.broadcast({
                    "type": "error_event", "ts": time.time(),
                    "category": category, "user": "system",
                    "detail": f"{name}: {type(e).__name__}: {str(e)[:200]}",
                })
                raise
        return wrapped

    def _persist_flags() -> None:
        save_state({"reply_enabled": _flags["REPLY_ENABLED"], "dry_run": _flags["DRY_RUN"]})

    state = State()
    guardrail = Guardrail()
    cost = CostTracker()
    persona_text = load_persona("config/persona.md")
    llm = LLMAdapter()

    tts: TTSAdapter | None = None
    try:
        pool = CartesiaPool.from_env()
        tts = TTSAdapter(pool)
    except Exception as e:
        log.warning("TTS disabled: %s", e)

    queue = ReplyQueue(maxsize=20)

    # ── v0.4 Audio Library ──────────────────────────────────────────────────
    _audio_index_path = Path(os.getenv("AUDIO_LIBRARY_DIR", "static/audio_library")) / "index.json"
    audio_lib_manager = AudioLibraryManager(_audio_index_path)
    await audio_lib_manager.load()
    audio_lib_manager.start_hot_reload()
    audio_lib_adapter = AudioLibraryAdapter(audio_lib_manager, ws.broadcast)
    log.info("audio_library: %d clips loaded", audio_lib_manager.clip_count)

    # ── v0.4 Budget Guard ───────────────────────────────────────────────────
    budget_guard = BudgetGuard(cost, ws.broadcast)

    # ── v0.4 Suggester ──────────────────────────────────────────────────────
    _reply_cache = ReplyCache(
        ttl_s=int(os.getenv("REPLY_CACHE_TTL_S", "300")),
        similarity_threshold=float(os.getenv("REPLY_CACHE_SIMILARITY", "0.90")),
    )
    _templates_path = Path(os.getenv("REPLY_TEMPLATES_YAML", "config/reply_templates.yaml"))
    suggester = Suggester(_reply_cache, budget_guard, llm, _templates_path)

    # ── v0.4 Live Director ──────────────────────────────────────────────────
    _products_yaml = Path(os.getenv("PRODUCTS_YAML", "config/products.yaml"))
    _live_max_duration_s = int(os.getenv("LIVE_MAX_DURATION_S", "7200"))
    live_director = LiveDirector(
        products_yaml=_products_yaml,
        audio_manager=audio_lib_manager,
        audio_adapter=audio_lib_adapter,
        ws_broadcast=ws.broadcast,
        max_duration_s=_live_max_duration_s,
    )
    log.info("live_director: ready=%s, phases=%d", live_director.is_ready, len(live_director._runsheet))

    async def handle_reply(job: ReplyJob) -> None:
        if cost.is_over_budget():
            log.warning("BUDGET EXCEEDED (Rp %.0f) — skipping reply", cost.day.total_idr)
            return
        t0 = time.monotonic()
        prompt = f"{job.user} bertanya: {job.text}"
        tier = "ninerouter"
        prompt_tok = 0
        completion_tok = 0
        if _flags["DRY_RUN"]:
            log.info("[DRY_RUN] Would reply to %s: %r", job.user, job.text)
            reply_text = f"[dry_run] Halo {job.user}, pesanmu: {job.text[:40]}"
        else:
            result = await llm.reply(persona_text, prompt)
            if result.tier == "error" or not result.text:
                log.error("LLM failed for %s — no reply", job.user)
                await ws.broadcast({
                    "type": "error_event", "ts": time.time(),
                    "category": "llm", "user": job.user, "detail": "LLM all tiers failed",
                })
                return
            reply_text = result.text
            tier = result.tier
            prompt_tok = result.prompt_tokens
            completion_tok = result.completion_tokens
            idr = cost.record_llm(tier, prompt_tok, completion_tok)
            log.info("[llm:%s] %s → %r (+Rp %.2f)", tier, job.user, reply_text[:60], idr)

        tts_engine = "skipped"
        if tts and not _flags["DRY_RUN"]:
            try:
                tts_result = await tts.speak(reply_text)
                tts_engine = tts_result.engine
                idr_tts = cost.record_tts(tts_engine, tts_result.char_count)
                log.info("[tts:%s] %d chars (+Rp %.2f)", tts_engine, tts_result.char_count, idr_tts)
            except Exception as e:
                log.error("TTS error: %s", e)
                await ws.broadcast({
                    "type": "error_event", "ts": time.time(),
                    "category": "tts", "user": job.user, "detail": str(e)[:300],
                })

        state.replies += 1
        latency_ms = int((time.monotonic() - t0) * 1000)
        state.record_latency(latency_ms)
        await ws.broadcast({
            "type": "reply_event", "ts": time.time(),
            "user": job.user, "comment": job.text,
            "reply": reply_text, "tier": tier,
            "tts": tts_engine, "latency_ms": latency_ms,
        })

    queue.start_worker(handle_reply)

    # ── P2-C: Register 15 validation commands ──────────────────────────────

    async def cmd_test_ffplay(_p: dict[str, object]) -> dict[str, object]:
        path = shutil.which("ffplay") or shutil.which(r"C:\ffmpeg\bin\ffplay.exe")
        if not path:
            raise RuntimeError("ffplay not in PATH — install ffmpeg")
        proc = await asyncio.create_subprocess_exec(
            path, "-version",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        version = stdout.decode("utf-8", errors="replace").splitlines()[0] if stdout else "unknown"
        return {"path": path, "version": version}

    async def cmd_test_ninerouter(_p: dict[str, object]) -> dict[str, object]:
        base = os.getenv("NINEROUTER_BASE_URL", "http://localhost:20128/v1")
        key = os.getenv("NINEROUTER_API_KEY", "sk-dummy-9router")
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                f"{base}/models", headers={"Authorization": f"Bearer {key}"}
            )
            r.raise_for_status()
            data = r.json()
        models = [m.get("id", "?") for m in data.get("data", [])]
        return {"base": base, "model_count": len(models), "models": models[:10]}

    async def cmd_test_llm(_p: dict[str, object]) -> dict[str, object]:
        result = await llm.reply(persona_text, "Jawab dengan 1 kata: halo", max_tokens=20)
        if result.tier == "error":
            raise RuntimeError("LLM all tiers failed")
        return {
            "tier": result.tier, "model": result.model,
            "text": result.text[:100], "latency_ms": result.latency_ms,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
        }

    async def cmd_test_cartesia_key(p: dict[str, object]) -> dict[str, object]:
        idx = int(p.get("key_index", 0))  # type: ignore[arg-type]
        if not tts or idx >= len(tts.pool.slots):
            raise RuntimeError(
                f"key_index {idx} out of range "
                f"(pool size {len(tts.pool.slots) if tts else 0})"
            )
        slot = tts.pool.slots[idx]
        voice_id = os.getenv("CARTESIA_VOICE_ID", "")
        model = os.getenv("CARTESIA_MODEL", "sonic-3")
        if not voice_id:
            raise RuntimeError("CARTESIA_VOICE_ID not set in .env")
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "https://api.cartesia.ai/tts/bytes",
                headers={
                    "Cartesia-Version": "2026-03-01",
                    "X-API-Key": slot.key,
                    "Content-Type": "application/json",
                },
                json={
                    "model_id": model, "transcript": "halo",
                    "voice": {"mode": "id", "id": voice_id},
                    "language": "id",
                    "output_format": {
                        "container": "wav", "encoding": "pcm_f32le", "sample_rate": 44100,
                    },
                },
            )
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
            size_kb = len(r.content) / 1024
        return {"key": slot.preview(), "audio_kb": round(size_kb, 1), "model": model}

    async def cmd_test_cartesia_all(_p: dict[str, object]) -> dict[str, object]:
        if not tts:
            raise RuntimeError("TTS adapter not initialized")
        results: list[dict[str, object]] = []
        for i in range(len(tts.pool.slots)):
            try:
                r = await cmd_test_cartesia_key({"key_index": i})
                results.append({"index": i, "ok": True, **r})
            except Exception as e:
                results.append({"index": i, "ok": False, "error": str(e)[:200]})
        return {"results": results, "ok_count": sum(1 for r in results if r["ok"])}

    async def cmd_test_edge_tts(_p: dict[str, object]) -> dict[str, object]:
        import edge_tts as _edge_tts  # type: ignore[import-not-found]
        voice = os.getenv("EDGE_TTS_VOICE", "id-ID-ArdiNeural")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp = f.name
        try:
            communicate = _edge_tts.Communicate("Test suara Indonesia", voice)
            await communicate.save(tmp)
            size_kb = Path(tmp).stat().st_size / 1024
            return {"voice": voice, "audio_kb": round(size_kb, 1)}
        finally:
            Path(tmp).unlink(missing_ok=True)

    async def cmd_generate_edge_tts(p: dict[str, object]) -> dict[str, object]:
        """Generate Edge-TTS audio and save to static folder for download/play."""
        import edge_tts as _edge_tts  # type: ignore[import-not-found]
        import time
        
        text = str(p.get("text", "")).strip()
        if not text:
            raise RuntimeError("text required")
        voice = str(p.get("voice", os.getenv("EDGE_TTS_VOICE", "id-ID-ArdiNeural")))
        
        # Save to controller static folder
        static_dir = Path("../controller/static/tts-samples")
        static_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        filename = f"edge-{timestamp}.mp3"
        output_path = static_dir / filename
        
        communicate = _edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
        
        # Get file metadata
        file_size_kb = output_path.stat().st_size / 1024
        
        # Estimate duration (rough: 150 words per minute, average 5 chars per word)
        word_count = len(text.split())
        duration_s = (word_count / 150) * 60
        
        return {
            "file_path": f"/tts-samples/{filename}",
            "duration_s": round(duration_s, 2),
            "file_size_kb": round(file_size_kb, 1),
            "voice": voice
        }

    async def cmd_generate_cartesia_tts(p: dict[str, object]) -> dict[str, object]:
        """Generate Cartesia TTS audio and save to static folder for download/play."""
        import time
        import httpx
        
        if not tts:
            raise RuntimeError("TTS not initialized — check CARTESIA_API_KEYS")
        
        text = str(p.get("text", "")).strip()
        if not text:
            raise RuntimeError("text required")
        emotion = str(p.get("emotion", "neutral"))
        
        # Save to controller static folder
        static_dir = Path("../controller/static/tts-samples")
        static_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        filename = f"cartesia-{timestamp}.wav"
        output_path = static_dir / filename
        
        # Use Cartesia API directly via HTTP (like working scripts)
        if not tts.voice_id:
            raise RuntimeError("CARTESIA_VOICE_ID not set")
        
        slot = await tts.pool.acquire()
        safe_emotion = emotion if emotion in tts.VALID_EMOTIONS else "neutral"
        
        try:
            # Use HTTP API directly (same as scripts/voice/tts_lib.py)
            payload = {
                "model_id": tts.model_id,
                "transcript": text,
                "voice": {
                    "mode": "id",
                    "id": tts.voice_id
                },
                "output_format": {
                    "container": "wav",
                    "encoding": "pcm_f32le",
                    "sample_rate": 44100
                },
                "language": "id",
                "speed": "normal",
                "generation_config": {
                    "speed": 0.98,
                    "volume": 1.14,
                    "emotion": safe_emotion
                }
            }
            
            headers = {
                "Cartesia-Version": "2026-03-01",
                "X-API-Key": slot.key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.cartesia.ai/tts/bytes",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")
                
                audio_bytes = response.content
                
                # Save audio bytes to file
                output_path.write_bytes(audio_bytes)
                
                # Calculate metadata
                file_size_kb = len(audio_bytes) / 1024
                # Estimate duration: 44100 Hz, 32-bit float (4 bytes), mono
                duration_s = len(audio_bytes) / (44100 * 4)
                
                return {
                    "file_path": f"/tts-samples/{filename}",
                    "duration_s": round(duration_s, 2),
                    "file_size_kb": round(file_size_kb, 1),
                    "emotion": safe_emotion,
                    "key_preview": slot.preview(),
                }
        except Exception as e:
            log.error("Cartesia TTS generation failed: %s", e)
            raise RuntimeError(f"Cartesia TTS failed: {e}")


    async def cmd_test_tts_voice_out(p: dict[str, object]) -> dict[str, object]:
        if not tts:
            raise RuntimeError("TTS not initialized — check CARTESIA_API_KEYS")
        text = str(p.get("text", "Halo bos, Bang Hack di sini makasih udah mampir"))
        emotion = str(p.get("emotion", "neutral"))
        result = await tts.speak(text, emotion=emotion)
        if result.engine == "error":
            raise RuntimeError("TTS engine error — check logs")
        return {
            "engine": result.engine, "char_count": result.char_count,
            "duration_s": round(result.duration_s, 2), "key": result.key_preview,
            "emotion": emotion,
        }

    async def cmd_test_tiktok_conn(p: dict[str, object]) -> dict[str, object]:
        from TikTokLive import TikTokLiveClient  # type: ignore[import-not-found]
        from TikTokLive.client.errors import UserOfflineError  # type: ignore[import-not-found]
        uname = (str(p.get("username") or TIKTOK_USERNAME)).lstrip("@")
        if not uname:
            raise RuntimeError("username empty")
        client = TikTokLiveClient(unique_id=f"@{uname}")
        try:
            is_live = await client.is_live()
            return {"username": uname, "is_live": bool(is_live)}
        except UserOfflineError:
            return {"username": uname, "is_live": False, "note": "user offline"}

    async def cmd_reload_persona(_p: dict[str, object]) -> dict[str, object]:
        nonlocal persona_text
        new_text = load_persona("config/persona.md")
        persona_text = new_text
        return {"char_count": len(new_text), "content": new_text, "preview": new_text[:200]}

    async def cmd_save_persona(p: dict[str, object]) -> dict[str, object]:
        """Save persona text to config/persona.md and hot-reload into memory."""
        nonlocal persona_text
        content = str(p.get("content", "")).strip()
        if not content:
            raise RuntimeError("content required — cannot save empty persona")
        persona_path = Path("config/persona.md")
        persona_path.parent.mkdir(parents=True, exist_ok=True)
        persona_path.write_text(content, encoding="utf-8")
        persona_text = content
        log.info("persona saved (%d chars) and hot-reloaded", len(content))
        return {"saved": True, "char_count": len(content), "content": content, "preview": content[:200]}

    async def cmd_test_reply(p: dict[str, object]) -> dict[str, object]:
        user = str(p.get("user", "TestUser"))
        text = str(p.get("text", "halo bang"))
        gr = guardrail.check(user, text)
        if not gr.accepted:
            return {"stage": "guardrail", "accepted": False, "reason": gr.reason}
        llm_res = await llm.reply(persona_text, f"{user} bertanya: {text}")
        if llm_res.tier == "error":
            return {"stage": "llm", "error": "all tiers failed"}
        return {
            "stage": "ok", "accepted": True,
            "reply": llm_res.text, "tier": llm_res.tier,
            "model": llm_res.model, "latency_ms": llm_res.latency_ms,
        }

    async def cmd_test_guardrail(p: dict[str, object]) -> dict[str, object]:
        user = str(p.get("user", "TestUser"))
        text = str(p.get("text", ""))
        gr = guardrail.check(user, text)
        return {"accepted": gr.accepted, "reason": gr.reason}

    async def cmd_reset_cost_today(p: dict[str, object]) -> dict[str, object]:
        if not p.get("confirm"):
            raise RuntimeError("confirm flag required (dev only)")
        cost.day = CostDay()
        return cost.snapshot()

    async def cmd_reload_env(_p: dict[str, object]) -> dict[str, object]:
        load_dotenv(override=True)
        return {"note": "env reloaded — restart worker to re-init adapters"}

    async def cmd_set_reply_enabled(p: dict[str, object]) -> dict[str, object]:
        _flags["REPLY_ENABLED"] = bool(p.get("value", False))
        _persist_flags()
        return {"reply_enabled": _flags["REPLY_ENABLED"], "note": "persisted to .state.json"}

    async def cmd_set_dry_run(p: dict[str, object]) -> dict[str, object]:
        _flags["DRY_RUN"] = bool(p.get("value", False))
        _persist_flags()
        return {"dry_run": _flags["DRY_RUN"], "note": "persisted to .state.json"}

    async def cmd_update_llm_tier(p: dict[str, object]) -> dict[str, object]:
        tier_id = str(p.get("tier_id", ""))
        model = str(p.get("model", ""))
        if not tier_id or not model:
            raise RuntimeError("tier_id and model required")
        llm.update_tier_model(tier_id, model)
        return {"tier_id": tier_id, "model": model, "note": "updated (runtime only)"}

    async def cmd_test_llm_custom(p: dict[str, object]) -> dict[str, object]:
        model = str(p.get("model", "")).strip()
        api_base = str(p.get("api_base", "")).strip()
        api_key = str(p.get("api_key", "")).strip()
        if not model:
            raise RuntimeError("model required — e.g. 'KIRO' atau 'openai/KIRO'")
        # test_with_model now raises RuntimeError with clear message on failure
        result = await llm.test_with_model(model, api_base, api_key)
        return {
            "model": result.model, "text": result.text[:100],
            "latency_ms": result.latency_ms,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
        }

    async def cmd_list_ninerouter_models(_p: dict[str, object]) -> dict[str, object]:
        """Fetch model list from 9router and return with correct LiteLLM format."""
        base = os.getenv("NINEROUTER_BASE_URL", "http://localhost:20128/v1")
        key = os.getenv("NINEROUTER_API_KEY", "sk-dummy-9router")
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                f"{base}/models", headers={"Authorization": f"Bearer {key}"}
            )
            r.raise_for_status()
            data = r.json()
        raw_ids = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
        # Return with litellm_model = openai/<id> format
        models = [
            {"id": mid, "litellm_model": f"openai/{mid}"}
            for mid in raw_ids
        ]
        return {"base": base, "count": len(models), "models": models}

    # ── P3 new command handlers ─────────────────────────────────────────────

    async def cmd_read_env(_p: dict[str, object]) -> dict[str, object]:
        return {"env": read_env(mask_secrets=True)}

    async def cmd_save_env(p: dict[str, object]) -> dict[str, object]:
        updates = p.get("updates")
        if not isinstance(updates, dict) or not updates:
            raise RuntimeError("updates dict required — e.g. {TIKTOK_USERNAME: 'foo'}")
        str_updates = {str(k): str(v) for k, v in updates.items()}
        backup = write_env(str_updates)
        return {"saved": True, "backup": backup.name, "keys": list(str_updates.keys())}

    async def cmd_set_cartesia_config(p: dict[str, object]) -> dict[str, object]:
        if tts is None:
            raise RuntimeError("TTS not initialized — set CARTESIA_API_KEYS dulu")
        voice_id = str(p.get("voice_id", "")).strip()
        model = str(p.get("model", "")).strip()
        default_emotion = str(p.get("default_emotion", "")).strip()
        updates: dict[str, str] = {}
        if voice_id:
            if not re.match(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", voice_id):
                raise RuntimeError("voice_id must be UUID format (8-4-4-4-12 hex)")
            tts.voice_id = voice_id
            updates["CARTESIA_VOICE_ID"] = voice_id
        if model:
            if model not in ("sonic-3", "sonic-2", "sonic-english", "sonic-preview"):
                raise RuntimeError(f"unknown model {model!r}")
            tts.model_id = model
            updates["CARTESIA_MODEL"] = model
        if default_emotion:
            if default_emotion not in tts.VALID_EMOTIONS:
                raise RuntimeError(f"invalid emotion {default_emotion!r} — must be one of {sorted(tts.VALID_EMOTIONS)}")
            tts.default_emotion = default_emotion
            updates["CARTESIA_DEFAULT_EMOTION"] = default_emotion
        if updates:
            write_env(updates)
        return {
            "voice_id": tts.voice_id, "model": tts.model_id,
            "default_emotion": tts.default_emotion,
            "persisted": bool(updates),
        }

    async def cmd_add_cartesia_key(p: dict[str, object]) -> dict[str, object]:
        if tts is None:
            raise RuntimeError("TTS not initialized")
        key = str(p.get("key", "")).strip()
        tts.pool.add_key(key)  # raises kalau invalid
        all_keys = [s.key for s in tts.pool.slots]
        write_env({"CARTESIA_API_KEYS": ",".join(all_keys)})
        return {"added": True, "pool_size": len(tts.pool.slots)}

    async def cmd_remove_cartesia_key(p: dict[str, object]) -> dict[str, object]:
        if tts is None:
            raise RuntimeError("TTS not initialized")
        key_preview = str(p.get("key_preview", "")).strip()
        if not tts.pool.remove_key_by_preview(key_preview):
            raise RuntimeError(f"key not found: {key_preview!r}")
        all_keys = [s.key for s in tts.pool.slots]
        write_env({"CARTESIA_API_KEYS": ",".join(all_keys) if all_keys else ""})
        return {"removed": True, "pool_size": len(tts.pool.slots)}

    async def cmd_update_guardrail(p: dict[str, object]) -> dict[str, object]:
        forbidden = p.get("forbidden_patterns")
        try:
            guardrail.update_config(
                forbidden=forbidden if isinstance(forbidden, list) else None,
                min_words=int(p["min_words"]) if "min_words" in p else None,
                rate_max=int(p["rate_max"]) if "rate_max" in p else None,
                rate_window_s=int(p["rate_window_s"]) if "rate_window_s" in p else None,
                max_chars=int(p["max_chars"]) if "max_chars" in p else None,
            )
        except re.error as e:
            raise RuntimeError(f"invalid regex: {e}") from e
        snap = guardrail.config_snapshot()
        write_env({
            "GUARDRAIL_MIN_WORDS": str(snap["min_words"]),
            "GUARDRAIL_RATE_MAX": str(snap["rate_max"]),
            "GUARDRAIL_RATE_WINDOW_S": str(snap["rate_window_s"]),
            "GUARDRAIL_MAX_CHARS": str(snap["max_chars"]),
        })
        return {"updated": True, **snap}

    async def cmd_set_budget_idr(p: dict[str, object]) -> dict[str, object]:
        value = float(p.get("value", 5000))
        cost.set_budget(value)  # raises ValueError kalau out of range
        write_env({"BUDGET_IDR_DAILY": str(int(value))})
        return {"budget_idr": value}

    async def cmd_connect_tiktok(p: dict[str, object]) -> dict[str, object]:
        username = str(p.get("username", "")).strip().lstrip("@")
        if not username:
            raise RuntimeError("username empty")
        await tt_supervisor.connect(username)
        write_env({"TIKTOK_USERNAME": username})
        return {"connected": True, "username": username}

    async def cmd_disconnect_tiktok(_p: dict[str, object]) -> dict[str, object]:
        await tt_supervisor.disconnect()
        return {"connected": False}

    async def cmd_list_audio_devices(_p: dict[str, object]) -> dict[str, object]:
        return {"devices": list_devices()}

    async def cmd_read_cost_history(p: dict[str, object]) -> dict[str, object]:
        days = int(p.get("days", 7))
        cutoff = time.time() - days * 86400
        rows: list[dict[str, object]] = []
        cost_path = Path("costs.jsonl")
        if cost_path.exists():
            for line in cost_path.read_text(encoding="utf-8").splitlines():
                try:
                    rec = json.loads(line)
                    if rec.get("ts", 0) >= cutoff:
                        rows.append(rec)
                except Exception:
                    continue
        return {"rows": rows, "count": len(rows)}

    # ── v0.4 Audio Library commands ─────────────────────────────────────────

    async def cmd_audio_list(p: dict[str, object]) -> dict[str, object]:
        tag = str(p.get("tag", "")).strip()
        if tag:
            clips = audio_lib_manager.search(tag)
        else:
            clips = audio_lib_manager.all_clips
        payload = [
            {
                "id": c.id,
                "category": c.category,
                "tags": c.tags,
                "duration_ms": c.duration_ms,
                "text": c.script,           # FIX: controller baca field `text`
                "script": c.script,          # keep back-compat
                "scene_hint": c.scene_hint,
                "product": getattr(c, "product", None),
            }
            for c in clips
        ]
        # FIX: broadcast `audio.list.ok` supaya audioClips store di controller ke-isi
        await ws.broadcast({"type": "audio.list.ok", "ts": time.time(), "clips": payload})
        return {"clips": payload, "count": len(payload)}

    async def cmd_audio_play(p: dict[str, object]) -> dict[str, object]:
        clip_id = str(p.get("clip_id", "")).strip()
        if not clip_id:
            raise RuntimeError("clip_id required")
        await audio_lib_adapter.play(clip_id)
        return {"ok": True, "clip_id": clip_id}

    async def cmd_audio_stop(_p: dict[str, object]) -> dict[str, object]:
        await audio_lib_adapter.stop()
        return {"ok": True}

    # ── v0.4 Reply commands ──────────────────────────────────────────────────

    async def cmd_reply_approve(p: dict[str, object]) -> dict[str, object]:
        """Approve a reply suggestion — send to TTS and broadcast reply.sent."""
        suggestion_id = str(p.get("suggestion_id", "")).strip()
        variant = int(p.get("variant", 0))
        
        if not suggestion_id:
            raise RuntimeError("suggestion_id required")
        
        sug = _pending_suggestions.pop(suggestion_id, None)
        if not sug:
            raise RuntimeError(f"suggestion {suggestion_id} not found")
        
        if not (0 <= variant < len(sug["replies"])):
            raise RuntimeError(f"invalid variant {variant}")
        
        reply_text = sug["replies"][variant]
        user = sug["user"]
        comment_text = sug["comment_text"]
        
        t0 = time.monotonic()
        tts_engine = "skipped"
        
        if not _flags["REPLY_ENABLED"]:
            log.info("[REPLY_DISABLED] Would reply to %s: %r", user, reply_text)
        elif _flags["DRY_RUN"]:
            log.info("[DRY_RUN] Would reply to %s: %r", user, reply_text)
        elif tts:
            try:
                tts_result = await tts.speak(reply_text)
                tts_engine = tts_result.engine
                idr_tts = cost.record_tts(tts_engine, tts_result.char_count)
                log.info("[tts:%s] %d chars (+Rp %.2f)", tts_engine, tts_result.char_count, idr_tts)
            except Exception as e:
                log.error("TTS error: %s", e)
                await ws.broadcast({
                    "type": "error",
                    "ts": time.time(),
                    "category": "tts",
                    "user": user,
                    "detail": str(e)[:300],
                })
        
        latency_ms = int((time.monotonic() - t0) * 1000)
        state.replies += 1
        state.record_latency(latency_ms)
        
        await ws.broadcast({
            "type": "reply.sent",
            "ts": time.time(),
            "suggestion_id": suggestion_id,
            "user": user,
            "comment": comment_text,
            "reply": reply_text,
            "tier": sug["source"],
            "tts": tts_engine,
            "latency_ms": latency_ms,
        })
        
        return {"ok": True, "reply": reply_text, "user": user}

    async def _speak_reply(text: str) -> None:
        try:
            await tts.speak(text)
        except Exception as e:
            log.error("TTS speak error: %s", e)

    async def cmd_reply_reject(p: dict[str, object]) -> dict[str, object]:
        """Reject a reply suggestion — remove from pending."""
        suggestion_id = str(p.get("suggestion_id", "")).strip()
        if suggestion_id in _pending_suggestions:
            _pending_suggestions.pop(suggestion_id)
        return {"ok": True, "suggestion_id": suggestion_id}

    async def cmd_reply_regen(p: dict[str, object]) -> dict[str, object]:
        """Regenerate reply suggestions for a comment."""
        import uuid
        suggestion_id = str(p.get("suggestion_id", "")).strip()
        hint = str(p.get("hint", "")).strip()
        
        if not suggestion_id or suggestion_id not in _pending_suggestions:
            raise RuntimeError("suggestion_id not found")
        
        sug = _pending_suggestions[suggestion_id]
        text = sug["comment_text"]
        intent = sug["intent"]
        user = sug["user"]
        
        # For now, ignore hint and just regenerate
        # TODO: incorporate hint into LLM prompt
        current_product = live_director.get_state().get("product", "PALOMA")
        result = await suggester.handle(text, intent, product=current_product, user=user)
        
        # Update existing suggestion
        sug["replies"] = result["replies"]
        sug["source"] = result["source"]
        
        await ws.broadcast({
            "type": "reply.suggestion",
            "ts": time.time(),
            "suggestion_id": suggestion_id,
            "user": user,
            "comment_id": sug["comment_id"],
            "comment_text": text,
            "intent": intent,
            "replies": result["replies"],
            "source": result["source"],
        })
        
        return {
            "ok": True,
            "suggestion_id": suggestion_id,
            "replies": result["replies"],
            "source": result["source"],
        }

    async def cmd_reply_suggest(p: dict[str, object]) -> dict[str, object]:
        """Generate reply suggestions for a comment."""
        text = str(p.get("text", "")).strip()
        intent = str(p.get("intent", "other")).strip()
        product = str(p.get("product", "")).strip()
        user = str(p.get("user", "")).strip()
        comment_id = str(p.get("comment_id", f"{user}_{int(time.time())}"))
        if not text:
            raise RuntimeError("text required")
        result = await suggester.handle(text, intent, product=product, user=user)
        return {
            "comment_id": comment_id,
            "replies": result["replies"],
            "source": result["source"],
            "cached": result["cached"],
        }

    async def cmd_budget_get(_p: dict[str, object]) -> dict[str, object]:
        return budget_guard.snapshot()

    # ── v0.4 Live Director commands ──────────────────────────────────────────

    async def cmd_live_start(_p: dict[str, object]) -> dict[str, object]:
        await live_director.start()
        return {"ok": True, "state": live_director.get_state()}

    async def cmd_live_pause(_p: dict[str, object]) -> dict[str, object]:
        await live_director.pause()
        return {"ok": True, "state": live_director.get_state()}

    async def cmd_live_resume(_p: dict[str, object]) -> dict[str, object]:
        await live_director.resume()
        return {"ok": True, "state": live_director.get_state()}

    async def cmd_live_stop(_p: dict[str, object]) -> dict[str, object]:
        await live_director.stop()
        return {"ok": True}

    async def cmd_live_emergency_stop(p: dict[str, object]) -> dict[str, object]:
        operator_id = str(p.get("operator_id", "operator"))
        await live_director.emergency_stop(operator_id)
        return {"ok": True}

    async def cmd_live_get_state(_p: dict[str, object]) -> dict[str, object]:
        # PATCH 4a: Broadcast live.state untuk sync ke frontend
        state = live_director.get_state()
        await ws.broadcast({"type": "live.state", **state})
        return state

    for cmd_name, cmd_handler, category in [
        # existing 19
        ("test_ffplay", cmd_test_ffplay, "system"),
        ("test_ninerouter", cmd_test_ninerouter, "llm"),
        ("test_llm", cmd_test_llm, "llm"),
        ("test_cartesia_key", cmd_test_cartesia_key, "tts"),
        ("test_cartesia_all", cmd_test_cartesia_all, "tts"),
        ("test_edge_tts", cmd_test_edge_tts, "tts"),
        ("test_tts_voice_out", cmd_test_tts_voice_out, "tts"),
        ("test_tiktok_conn", cmd_test_tiktok_conn, "tiktok"),
        ("reload_persona", cmd_reload_persona, "config"),
        ("save_persona", cmd_save_persona, "config"),
        ("test_reply", cmd_test_reply, "llm"),
        ("test_guardrail", cmd_test_guardrail, "guardrail"),
        ("reset_cost_today", cmd_reset_cost_today, "cost"),
        ("reload_env", cmd_reload_env, "config"),
        ("set_reply_enabled", cmd_set_reply_enabled, "config"),
        ("set_dry_run", cmd_set_dry_run, "config"),
        ("update_llm_tier", cmd_update_llm_tier, "llm"),
        ("test_llm_custom", cmd_test_llm_custom, "llm"),
        ("list_ninerouter_models", cmd_list_ninerouter_models, "llm"),
        # P3 new 11
        ("read_env", cmd_read_env, "config"),
        ("save_env", cmd_save_env, "config"),
        ("set_cartesia_config", cmd_set_cartesia_config, "tts"),
        ("add_cartesia_key", cmd_add_cartesia_key, "tts"),
        ("remove_cartesia_key", cmd_remove_cartesia_key, "tts"),
        ("update_guardrail", cmd_update_guardrail, "guardrail"),
        ("set_budget_idr", cmd_set_budget_idr, "cost"),
        ("connect_tiktok", cmd_connect_tiktok, "tiktok"),
        ("disconnect_tiktok", cmd_disconnect_tiktok, "tiktok"),
        ("list_audio_devices", cmd_list_audio_devices, "system"),
        ("read_cost_history", cmd_read_cost_history, "cost"),
        # TTS generate with download/play
        ("generate_edge_tts", cmd_generate_edge_tts, "tts"),
        ("generate_cartesia_tts", cmd_generate_cartesia_tts, "tts"),
        ("audio.list", cmd_audio_list, "audio"),
        ("audio.play", cmd_audio_play, "audio"),
        ("audio.stop", cmd_audio_stop, "audio"),
        ("budget.get", cmd_budget_get, "cost"),
        ("reply.approve", cmd_reply_approve, "reply"),
        ("reply.reject", cmd_reply_reject, "reply"),
        ("reply.regen", cmd_reply_regen, "reply"),
        ("reply.suggest", cmd_reply_suggest, "reply"),
        ("live.start", cmd_live_start, "director"),
        ("live.pause", cmd_live_pause, "director"),
        ("live.resume", cmd_live_resume, "director"),
        ("live.stop", cmd_live_stop, "director"),
        ("live.emergency_stop", cmd_live_emergency_stop, "director"),
        ("live.get_state", cmd_live_get_state, "director"),
    ]:
        ws.register_command(cmd_name, _wrap_cmd(cmd_name, category, cmd_handler))

    # ── TikTok event handler ────────────────────────────────────────────────

    _classifier_threshold = float(os.getenv("CLASSIFIER_LLM_THRESHOLD", "0.80"))
    _pending_suggestions: dict[str, dict[str, Any]] = {}  # suggestion_id -> {user, comment_id, text, intent, replies, source}

    async def handle_comment(ev: TTEvent) -> None:
        """Classify comment, generate suggestions, and broadcast events."""
        # Guardrail check first
        gr = guardrail.check(ev.user, ev.text)
        if not gr.accepted:
            await ws.broadcast({
                "type": "tiktok.comment",
                "ts": time.time(),
                "user": ev.user,
                "text": ev.text,
                "intent": f"dropped:{gr.reason}",
            })
            return

        # Rule-first classification
        intent = rules_classify(ev.text)

        # LLM fallback for low-confidence non-forbidden
        if intent.needs_llm and not intent.safe_to_skip:
            intent = await classify_with_llm(ev.text, llm)
            await ws.broadcast({
                "type": "classifier.llm_used",
                "ts": time.time(),
                "comment_id": f"{ev.user}_{int(time.time())}",
                "tokens_used": 20,  # approximate
            })

        # Broadcast comment with intent
        await ws.broadcast({
            "type": "tiktok.comment",
            "ts": time.time(),
            "user": ev.user,
            "text": ev.text,
            "intent": intent.name,
        })

        await ws.broadcast({
            "type": "comment.classified",
            "ts": time.time(),
            "comment_id": f"{ev.user}_{int(time.time())}",
            "user": ev.user,
            "text": ev.text,
            "intent": intent.name,
            "confidence": intent.confidence,
            "reason": intent.reason,
            "method": "rule" if not intent.needs_llm or intent.safe_to_skip else "llm",
            # PATCH 4b: Tambah source field untuk DecisionStream reasoning
            "source": "rules" if not intent.needs_llm or intent.safe_to_skip else "llm",
        })

        # Generate suggestions for valuable comments
        if not intent.safe_to_skip:
            import uuid
            comment_id = f"c_{uuid.uuid4().hex[:8]}"
            suggestion_id = f"s_{uuid.uuid4().hex[:8]}"
            
            try:
                current_product = live_director.get_state().get("product", "PALOMA")
                result = await suggester.handle(ev.text, intent.name, product=current_product, user=ev.user)
                
                _pending_suggestions[suggestion_id] = {
                    "user": ev.user,
                    "comment_id": comment_id,
                    "comment_text": ev.text,
                    "intent": intent.name,
                    "replies": result["replies"],
                    "source": result["source"],
                }
                
                await ws.broadcast({
                    "type": "reply.suggestion",
                    "ts": time.time(),
                    "suggestion_id": suggestion_id,
                    "user": ev.user,
                    "comment_id": comment_id,
                    "comment_text": ev.text,
                    "intent": intent.name,
                    "replies": result["replies"],
                    "source": result["source"],
                })
            except Exception as e:
                log.error("Failed to generate suggestion for %s: %s", ev.user, e)
                await ws.broadcast({
                    "type": "error",
                    "ts": time.time(),
                    "category": "suggester",
                    "user": ev.user,
                    "detail": str(e)[:200],
                })

    async def on_tt_event(ev: TTEvent) -> None:
        if ev.type == "connected":
            state.status = "live"
        elif ev.type == "disconnected":
            state.status = "reconnecting"
        elif ev.type == "offline":
            state.status = "waiting_for_live"
        elif ev.type == "comment":
            state.comments += 1
            asyncio.create_task(handle_comment(ev))
            if _flags["REPLY_ENABLED"]:
                gr = guardrail.check(ev.user, ev.text)
                if gr.accepted:
                    await queue.put(ReplyJob(user=ev.user, text=ev.text, ts=time.time()))
                else:
                    log.info("guardrail skipped (%s) for %s", gr.reason, ev.user)
        elif ev.type == "gift":
            state.gifts += 1
        elif ev.type == "join":
            state.joins += 1
        await ws.broadcast({
            "type": "tiktok_event", "ts": time.time(),
            "event_type": ev.type, "user": ev.user,
            "text": ev.text, "count": ev.count,
        })

    tt_supervisor = TikTokSupervisor(on_tt_event)
    if TIKTOK_USERNAME:
        log.info("Starting TikTok adapter for @%s", TIKTOK_USERNAME)
        await tt_supervisor.connect(TIKTOK_USERNAME)
    else:
        log.warning("TIKTOK_USERNAME not set — standby, connect via UI")

    http_task = asyncio.create_task(_run_http(llm, audio_lib_manager, live_director, cost), name="http")
    log.info("HTTP API listening on http://%s:%d", HTTP_HOST, HTTP_PORT)

    _last_cost_log_hour = -1
    try:
        while True:
            uptime = int(time.time() - state.start_ts)
            cost_snap = cost.snapshot()
            mode = "p3-reply-loop" if _flags["REPLY_ENABLED"] else "p3-readonly"
            await ws.broadcast({
                "type": "metrics", "ts": time.time(),
                "status": state.status, "uptime_s": uptime,
                "viewers": state.viewers, "comments": state.comments,
                "replies": state.replies, "gifts": state.gifts,
                "joins": state.joins, "queue_size": queue.size(),
                "latency_p95_ms": state.p95_latency(),
                "cost_idr": round(cost_snap["total_idr"], 2),
                "budget_idr": cost_snap["budget_idr"],
                "budget_pct": cost_snap["budget_pct"],
                "over_budget": cost_snap["over_budget"],
                "by_tier": cost_snap["by_tier"],
                "llm_calls": cost_snap["llm_calls"],
                "tts_calls": cost_snap["tts_calls"],
                "mode": mode,
                "reply_enabled": _flags["REPLY_ENABLED"],
                "dry_run": _flags["DRY_RUN"],
                "cartesia_pool": tts.pool.stats() if tts else [],
                "llm_models": llm.get_model_list(),
                "tiktok_username": tt_supervisor.current_username,
                "tiktok_running": tt_supervisor.is_running(),
                "guardrail": guardrail.config_snapshot(),
            })
            _current_hour = int(time.time() // 3600)
            if _current_hour != _last_cost_log_hour:
                _last_cost_log_hour = _current_hour
                with Path("costs.jsonl").open("a", encoding="utf-8") as _f:
                    _f.write(json.dumps({"ts": time.time(), "total_idr": cost_snap["total_idr"], "by_tier": cost_snap["by_tier"]}) + "\n")
            await asyncio.sleep(HEARTBEAT_INTERVAL_S)
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("shutting down")
        await queue.stop()
        http_task.cancel()
        await tt_supervisor.disconnect()
        await ws.stop()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Goodbye!")
