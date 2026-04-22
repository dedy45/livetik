"""Main entry point for Bang Hack worker (dev-wired)."""

import asyncio
import logging
import time
from typing import NoReturn

from .ipc.ws_server import WSServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
log = logging.getLogger("banghack")


async def main() -> NoReturn:
    """Main orchestrator with WebSocket server and dummy metrics broadcast."""
    log.info("🎙️ Bang Hack Worker v0.1.0-dev starting")
    
    # Initialize WebSocket server
    ws = WSServer(host="127.0.0.1", port=8765)
    await ws.start()

    start_ts = time.time()
    tick = 0
    
    try:
        while True:
            tick += 1
            uptime = int(time.time() - start_ts)
            
            # Broadcast dummy metrics every 2 seconds
            await ws.broadcast({
                "type": "metrics",
                "ts": time.time(),
                "status": "connected" if tick > 2 else "connecting",
                "uptime_s": uptime,
                "viewers": 0,
                "comments": tick * 3,
                "replies": tick,
                "queue_size": max(0, tick % 5),
                "latency_p95_ms": 120,
                "cost_idr": tick * 50,
            })
            
            log.debug("Broadcasted metrics (tick=%d, clients=%d)", tick, len(ws.clients))
            await asyncio.sleep(2)
            
    except KeyboardInterrupt:
        log.info("Shutting down gracefully...")
        await ws.stop()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Goodbye!")

