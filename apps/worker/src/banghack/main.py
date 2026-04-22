"""Main entry point for Bang Hack worker (P0-final, idle-aware)."""

import asyncio
import logging
import time
from typing import NoReturn

from .ipc.ws_server import WSServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("banghack")

# Broadcast setiap 5 detik = cukup untuk heartbeat UI, tidak spam log
HEARTBEAT_INTERVAL_S = 5


async def main() -> NoReturn:
    """Main orchestrator with idle-aware heartbeat."""
    log.info("🎙️ Bang Hack Worker v0.1.0-dev starting")
    log.info("Mode: IDLE (TikTok adapter belum aktif, no LLM calls, no cost)")

    ws = WSServer(host="127.0.0.1", port=8765)
    await ws.start()

    start_ts = time.time()
    try:
        while True:
            uptime = int(time.time() - start_ts)
            # Semua counter tetap 0 sampai adapter real dibuat di fase P2.
            # Status "idle" = worker hidup tapi belum connect ke TikTok.
            await ws.broadcast({
                "type": "metrics",
                "ts": time.time(),
                "status": "idle",
                "uptime_s": uptime,
                "viewers": 0,
                "comments": 0,
                "replies": 0,
                "queue_size": 0,
                "latency_p95_ms": 0,
                "cost_idr": 0,
                "mode": "dev-idle",
            })
            await asyncio.sleep(HEARTBEAT_INTERVAL_S)
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("shutting down")
        await ws.stop()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Goodbye!")

