"""WebSocket server — bidirectional: broadcast metrics + handle inbound commands."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

import websockets

log = logging.getLogger(__name__)

CommandHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class WSServer:
    """Bidirectional WS — supports metrics broadcast AND inbound command dispatch."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.clients: set[Any] = set()
        self._server: Any = None
        self._handlers: dict[str, CommandHandler] = {}

    def register_command(self, name: str, handler: CommandHandler) -> None:
        """Register a command handler. Handler receives params dict, returns result dict."""
        self._handlers[name] = handler
        log.info("registered command: %s", name)

    async def _handle_cmd(self, ws: Any, msg: dict[str, Any]) -> None:
        name = msg.get("name", "")
        req_id = msg.get("req_id", "")
        params = msg.get("params", {})
        handler = self._handlers.get(name)
        if not handler:
            await ws.send(json.dumps({
                "type": "cmd_result", "req_id": req_id, "ok": False,
                "error": f"unknown command: {name}",
            }))
            return
        try:
            t0 = time.monotonic()
            result = await handler(params)
            latency_ms = int((time.monotonic() - t0) * 1000)
            await ws.send(json.dumps({
                "type": "cmd_result", "req_id": req_id, "name": name,
                "ok": True, "latency_ms": latency_ms, "result": result,
            }))
        except Exception as e:
            log.exception("command %s failed", name)
            await ws.send(json.dumps({
                "type": "cmd_result", "req_id": req_id, "name": name,
                "ok": False, "error": str(e),
            }))

    async def _handler(self, ws: Any) -> None:
        self.clients.add(ws)
        log.info("client connected (total=%d)", len(self.clients))
        try:
            await ws.send(json.dumps({
                "type": "hello", "server": "banghack", "version": "0.3.0-dev",
                "commands": list(self._handlers.keys()),
            }))
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if msg.get("type") == "cmd":
                    asyncio.create_task(self._handle_cmd(ws, msg))
        finally:
            self.clients.discard(ws)
            log.info("client disconnected (total=%d)", len(self.clients))

    async def start(self) -> None:
        self._server = await websockets.serve(self._handler, self.host, self.port)
        log.info("WS server listening on ws://%s:%d", self.host, self.port)

    async def broadcast(self, event: dict[str, Any]) -> None:
        if not self.clients:
            return
        msg = json.dumps(event)
        await asyncio.gather(*(c.send(msg) for c in self.clients), return_exceptions=True)

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()
