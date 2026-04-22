"""Main entry — P2-C: TikTok read + LLM + TTS reply loop + bidirectional WS commands."""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import NoReturn

import httpx
import uvicorn
from dotenv import load_dotenv

from .adapters.cartesia_pool import CartesiaPool
from .adapters.llm import LLMAdapter
from .adapters.tiktok import TikTokAdapter, TTEvent
from .adapters.tts import TTSAdapter
from .core.cost import CostDay, CostTracker
from .core.guardrail import Guardrail
from .core.persona import load_persona
from .core.queue import ReplyJob, ReplyQueue
from .ipc.http_server import create_app
from .ipc.ws_server import WSServer

load_dotenv()

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


async def _run_http(llm: LLMAdapter) -> None:
    """Run FastAPI HTTP server for config/model API."""
    app = create_app(llm)
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

    async def cmd_test_tts_voice_out(p: dict[str, object]) -> dict[str, object]:
        if not tts:
            raise RuntimeError("TTS not initialized — check CARTESIA_API_KEYS")
        text = str(p.get("text", "Halo bos, Bang Hack di sini makasih udah mampir"))
        result = await tts.speak(text)
        if result.engine == "error":
            raise RuntimeError("TTS engine error — check logs")
        return {
            "engine": result.engine, "char_count": result.char_count,
            "duration_s": round(result.duration_s, 2), "key": result.key_preview,
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
        return {"char_count": len(new_text), "preview": new_text[:200]}

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
        return {"reply_enabled": _flags["REPLY_ENABLED"], "note": "runtime only, not persisted"}

    async def cmd_set_dry_run(p: dict[str, object]) -> dict[str, object]:
        _flags["DRY_RUN"] = bool(p.get("value", False))
        return {"dry_run": _flags["DRY_RUN"], "note": "runtime only, not persisted"}

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

    for cmd_name, cmd_handler in [
        ("test_ffplay", cmd_test_ffplay),
        ("test_ninerouter", cmd_test_ninerouter),
        ("test_llm", cmd_test_llm),
        ("test_cartesia_key", cmd_test_cartesia_key),
        ("test_cartesia_all", cmd_test_cartesia_all),
        ("test_edge_tts", cmd_test_edge_tts),
        ("test_tts_voice_out", cmd_test_tts_voice_out),
        ("test_tiktok_conn", cmd_test_tiktok_conn),
        ("reload_persona", cmd_reload_persona),
        ("test_reply", cmd_test_reply),
        ("test_guardrail", cmd_test_guardrail),
        ("reset_cost_today", cmd_reset_cost_today),
        ("reload_env", cmd_reload_env),
        ("set_reply_enabled", cmd_set_reply_enabled),
        ("set_dry_run", cmd_set_dry_run),
        ("update_llm_tier", cmd_update_llm_tier),
        ("test_llm_custom", cmd_test_llm_custom),
        ("list_ninerouter_models", cmd_list_ninerouter_models),
    ]:
        ws.register_command(cmd_name, cmd_handler)

    # ── TikTok event handler ────────────────────────────────────────────────

    async def on_tt_event(ev: TTEvent) -> None:
        if ev.type == "connected":
            state.status = "live"
        elif ev.type == "disconnected":
            state.status = "reconnecting"
        elif ev.type == "offline":
            state.status = "waiting_for_live"
        elif ev.type == "comment":
            state.comments += 1
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

    tiktok_task: asyncio.Task[None] | None = None
    if TIKTOK_USERNAME:
        log.info("Starting TikTok adapter for @%s", TIKTOK_USERNAME)
        tt = TikTokAdapter(TIKTOK_USERNAME, on_tt_event)
        tiktok_task = asyncio.create_task(tt.run_with_retry(), name="tiktok")
    else:
        log.warning("TIKTOK_USERNAME not set — heartbeat only")

    http_task = asyncio.create_task(_run_http(llm), name="http")
    log.info("HTTP API listening on http://%s:%d", HTTP_HOST, HTTP_PORT)

    try:
        while True:
            uptime = int(time.time() - state.start_ts)
            cost_snap = cost.snapshot()
            mode = "p2c-reply-loop" if _flags["REPLY_ENABLED"] else "p2c-readonly"
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
            })
            if tiktok_task and tiktok_task.done():
                exc = tiktok_task.exception()
                if exc:
                    log.error("TikTok task crashed: %s", exc)
                    state.status = "error"
                    tiktok_task = None
            await asyncio.sleep(HEARTBEAT_INTERVAL_S)
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("shutting down")
        await queue.stop()
        http_task.cancel()
        if tiktok_task and not tiktok_task.done():
            tiktok_task.cancel()
            try:
                await tiktok_task
            except (asyncio.CancelledError, Exception):
                pass
        await ws.stop()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Goodbye!")
