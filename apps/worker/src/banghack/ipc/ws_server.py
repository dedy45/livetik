"""WebSocket server untuk broadcast event ke controller UI."""
import asyncio
import json
import logging
from typing import Any

import websockets

log = logging.getLogger(__name__)


class WSServer:
    """WebSocket server untuk real-time communication dengan controller."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        """Initialize WebSocket server.

        Args:
            host: Host address to bind to
            port: Port number to listen on
        """
        self.host = host
        self.port = port
        self.clients: set[Any] = set()
        self._server: Any = None

    async def _handler(self, ws: Any) -> None:
        """Handle individual WebSocket connection.

        Args:
            ws: WebSocket connection protocol
        """
        self.clients.add(ws)
        log.info("Client connected (total=%d)", len(self.clients))
        try:
            # Send hello event immediately
            await ws.send(json.dumps({
                "type": "hello",
                "server": "banghack",
                "version": "0.1.0-dev"
            }))
            # Keep connection alive, ignore inbound messages for now
            async for _ in ws:
                pass
        finally:
            self.clients.discard(ws)
            log.info("Client disconnected (total=%d)", len(self.clients))

    async def start(self) -> None:
        """Start the WebSocket server."""
        self._server = await websockets.serve(self._handler, self.host, self.port)
        log.info("WS server listening on ws://%s:%d", self.host, self.port)

    async def broadcast(self, event: dict[str, Any]) -> None:
        """Broadcast event to all connected clients.

        Args:
            event: Event dictionary to broadcast
        """
        if not self.clients:
            return
        msg = json.dumps(event)
        await asyncio.gather(
            *(c.send(msg) for c in self.clients),
            return_exceptions=True,
        )

    async def stop(self) -> None:
        """Stop the WebSocket server and close all connections."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
