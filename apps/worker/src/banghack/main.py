"""Main entry point for Bang Hack worker (P2-A: TikTok read-only wired)."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import NoReturn

from dotenv import load_dotenv

from .adapters.tiktok import TikTokAdapter, TTEvent
from .ipc.ws_server import WSServer

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("banghack")

TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME", "").strip().lstrip("@")
HEARTBEAT_INTERVAL_S = 5


class State:
    """Mutable worker state shared between heartbeat and TikTok callback."""

    def __init__(self) -> None:
        self.status: str = "idle"
        self.start_ts: float = time.time()
        self.comments: int = 0
        self.gifts: int = 0
        self.joins: int = 0
        self.viewers: int = 0


async def main() -> NoReturn:
    log.info("🎙️ Bang Hack Worker v0.1.0-dev (P2-A) starting")
    ws = WSServer(host="127.0.0.1", port=8765)
    await ws.start()

    state = State()

    async def on_tt_event(ev: TTEvent) -> None:
        if ev.type == "connected":
            state.status = "live"
        elif ev.type == "disconnected":
            state.status = "reconnecting"
        elif ev.type == "offline":
            state.status = "waiting_for_live"
        elif ev.type == "comment":
            state.comments += 1
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
        log.warning("TIKTOK_USERNAME not set — heartbeat only (idle)")

    try:
        while True:
            uptime = int(time.time() - state.start_ts)
            await ws.broadcast({
                "type": "metrics",
                "ts": time.time(),
                "status": state.status,
                "uptime_s": uptime,
                "viewers": state.viewers,
                "comments": state.comments,
                "replies": 0,  # P2-B territory
                "gifts": state.gifts,
                "joins": state.joins,
                "queue_size": 0,
                "latency_p95_ms": 0,
                "cost_idr": 0,  # read-only = Rp 0 GUARANTEED
                "mode": "p2a-tiktok-readonly",
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
