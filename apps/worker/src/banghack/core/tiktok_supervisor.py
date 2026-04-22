"""TikTokSupervisor — hot-swap TikTok adapter tanpa restart worker."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from ..adapters.tiktok import TikTokAdapter, TTEvent

log = logging.getLogger(__name__)


class TikTokSupervisor:
    def __init__(self, on_event: Callable[[TTEvent], Awaitable[None]]) -> None:
        self._on_event = on_event
        self._task: asyncio.Task[None] | None = None
        self._adapter: TikTokAdapter | None = None
        self.current_username: str = ""

    async def connect(self, username: str) -> None:
        """Connect to new username. Gracefully disconnects current first if different.

        Raises:
            RuntimeError: kalau username empty.
        """
        username = username.strip().lstrip("@")
        if not username:
            raise RuntimeError("username empty")
        if self.current_username == username and self._task and not self._task.done():
            log.info("TikTok already connected to @%s — noop", username)
            return
        await self.disconnect()
        self._adapter = TikTokAdapter(username, self._on_event)
        self._task = asyncio.create_task(
            self._adapter.run_with_retry(),
            name=f"tiktok_{username}",
        )
        self.current_username = username
        log.info("TikTok connected → @%s", username)

    async def disconnect(self) -> None:
        """Gracefully cancel current TikTok task dengan 5s timeout."""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=5)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            except Exception as e:
                log.warning("TikTok disconnect: task exited with %s", e)
        old = self.current_username
        self._task = None
        self._adapter = None
        self.current_username = ""
        if old:
            log.info("TikTok disconnected from @%s", old)

    def is_running(self) -> bool:
        return bool(self._task and not self._task.done())
