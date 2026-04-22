"""Main entry — P2-B: TikTok read + LLM + TTS reply loop with budget cap."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import NoReturn

import uvicorn
from dotenv import load_dotenv

from .adapters.cartesia_pool import CartesiaPool
from .adapters.llm import LLMAdapter
from .adapters.tiktok import TikTokAdapter, TTEvent
from .adapters.tts import TTSAdapter
from .core.cost import CostTracker
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
REPLY_ENABLED = os.getenv("REPLY_ENABLED", "false").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
HTTP_HOST = os.getenv("HTTP_HOST", "127.0.0.1")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8766"))
HEARTBEAT_INTERVAL_S = 5


async def _run_http(llm: LLMAdapter) -> None:
    """Run FastAPI HTTP server for config/model API."""
    app = create_app(llm)
    config = uvicorn.Config(
        app,
        host=HTTP_HOST,
        port=HTTP_PORT,
        log_level="warning",
        access_log=False,
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
    log.info("🎙️ Bang Hack Worker v0.2.0-dev (P2-B) starting")
    log.info("REPLY_ENABLED=%s DRY_RUN=%s", REPLY_ENABLED, DRY_RUN)

    ws = WSServer(host="127.0.0.1", port=8765)
    await ws.start()

    state = State()
    guardrail = Guardrail()
    cost = CostTracker()
    persona_text = load_persona("config/persona.md")
    llm = LLMAdapter()

    # TTS is optional (only if Cartesia key configured)
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
        if DRY_RUN:
            log.info("[DRY_RUN] Would reply to %s: %r", job.user, job.text)
            reply_text = f"[dry_run] Halo {job.user}, pesanmu: {job.text[:40]}"
            tier = "ninerouter"
            prompt_tok = 0
            completion_tok = 0
        else:
            result = await llm.reply(persona_text, prompt)
            if result.tier == "error" or not result.text:
                log.error("LLM failed for %s — no reply", job.user)
                return
            reply_text = result.text
            tier = result.tier
            prompt_tok = result.prompt_tokens
            completion_tok = result.completion_tokens
            idr = cost.record_llm(tier, prompt_tok, completion_tok)
            log.info("[llm:%s] %s → %r (+Rp %.2f)", tier, job.user, reply_text[:60], idr)
        # TTS
        tts_engine = "skipped"
        if tts and not DRY_RUN:
            try:
                tts_result = await tts.speak(reply_text)
                tts_engine = tts_result.engine
                idr_tts = cost.record_tts(tts_engine, tts_result.char_count)
                log.info("[tts:%s] %d chars (+Rp %.2f)", tts_engine, tts_result.char_count, idr_tts)
            except Exception as e:
                log.error("TTS error: %s", e)
        # Update state + broadcast
        state.replies += 1
        latency_ms = int((time.monotonic() - t0) * 1000)
        state.record_latency(latency_ms)
        await ws.broadcast({
            "type": "reply_event",
            "ts": time.time(),
            "user": job.user,
            "comment": job.text,
            "reply": reply_text,
            "tier": tier,
            "tts": tts_engine,
            "latency_ms": latency_ms,
        })

    queue.start_worker(handle_reply)

    async def on_tt_event(ev: TTEvent) -> None:
        if ev.type == "connected":
            state.status = "live"
        elif ev.type == "disconnected":
            state.status = "reconnecting"
        elif ev.type == "offline":
            state.status = "waiting_for_live"
        elif ev.type == "comment":
            state.comments += 1
            # Decide whether to reply
            if REPLY_ENABLED:
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
            "type": "tiktok_event",
            "ts": time.time(),
            "event_type": ev.type,
            "user": ev.user,
            "text": ev.text,
            "count": ev.count,
        })

    tiktok_task: asyncio.Task[None] | None = None
    if TIKTOK_USERNAME:
        log.info("Starting TikTok adapter for @%s", TIKTOK_USERNAME)
        tt = TikTokAdapter(TIKTOK_USERNAME, on_tt_event)
        tiktok_task = asyncio.create_task(tt.run_with_retry(), name="tiktok")
    else:
        log.warning("TIKTOK_USERNAME not set — heartbeat only")

    # Start HTTP API server (config + model discovery)
    http_task = asyncio.create_task(_run_http(llm), name="http")
    log.info("HTTP API listening on http://%s:%d", HTTP_HOST, HTTP_PORT)

    mode = "p2b-reply-loop" if REPLY_ENABLED else "p2b-readonly"
    try:
        while True:
            uptime = int(time.time() - state.start_ts)
            cost_snap = cost.snapshot()
            await ws.broadcast({
                "type": "metrics",
                "ts": time.time(),
                "status": state.status,
                "uptime_s": uptime,
                "viewers": state.viewers,
                "comments": state.comments,
                "replies": state.replies,
                "gifts": state.gifts,
                "joins": state.joins,
                "queue_size": queue.size(),
                "latency_p95_ms": state.p95_latency(),
                "cost_idr": round(cost_snap["total_idr"], 2),
                "budget_idr": cost_snap["budget_idr"],
                "budget_pct": cost_snap["budget_pct"],
                "over_budget": cost_snap["over_budget"],
                "mode": mode,
                "reply_enabled": REPLY_ENABLED,
                "dry_run": DRY_RUN,
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
