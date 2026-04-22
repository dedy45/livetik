"""TikTok Live adapter — read-only listener (P2-A sprint).

Validates the hardest external dependency: TikTokLive package can connect
to @interiorhack.id from Windows + Indonesian IP without proxy/VPN.
No LLM, no TTS, no reply — pure event streaming into callback.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from TikTokLive import TikTokLiveClient  # type: ignore[import-not-found]
from TikTokLive.client.errors import UserOfflineError  # type: ignore[import-not-found]
from TikTokLive.events import (  # type: ignore[import-not-found]
    CommentEvent,
    ConnectEvent,
    DisconnectEvent,
    GiftEvent,
    JoinEvent,
    LikeEvent,
)

log = logging.getLogger(__name__)


@dataclass(slots=True)
class TTEvent:
    """Normalized TikTok event for downstream consumers."""

    type: str  # comment | gift | join | like | connected | disconnected | offline
    user: str
    text: str = ""
    count: int = 0


EventCallback = Callable[[TTEvent], Awaitable[None]]


class TikTokAdapter:
    """Read-only TikTok Live listener with auto-retry on offline."""

    def __init__(self, unique_id: str, callback: EventCallback) -> None:
        self.unique_id = unique_id.lstrip("@")
        self.callback = callback
        self.client = TikTokLiveClient(unique_id=f"@{self.unique_id}")
        self._register_handlers()

    def _register_handlers(self) -> None:
        @self.client.on(ConnectEvent)  # type: ignore[untyped-decorator]
        async def _on_connect(_: ConnectEvent) -> None:
            log.info("TikTok CONNECTED to @%s", self.unique_id)
            await self.callback(TTEvent(type="connected", user=self.unique_id))

        @self.client.on(DisconnectEvent)  # type: ignore[untyped-decorator]
        async def _on_disconnect(_: DisconnectEvent) -> None:
            log.info("TikTok DISCONNECTED")
            await self.callback(TTEvent(type="disconnected", user=self.unique_id))

        @self.client.on(CommentEvent)  # type: ignore[untyped-decorator]
        async def _on_comment(ev: CommentEvent) -> None:
            nickname = ev.user.nickname or ev.user.unique_id or "anon"
            log.info("[comment] %s: %s", nickname, ev.comment)
            await self.callback(
                TTEvent(type="comment", user=nickname, text=ev.comment or "")
            )

        @self.client.on(GiftEvent)  # type: ignore[untyped-decorator]
        async def _on_gift(ev: GiftEvent) -> None:
            # Skip intermediate streak events, only count the finalized one.
            if ev.gift.streakable and not ev.streaking:
                return
            nickname = ev.user.nickname or ev.user.unique_id or "anon"
            count = ev.repeat_count or 1
            log.info("[gift] %s sent %s x%d", nickname, ev.gift.name, count)
            await self.callback(
                TTEvent(type="gift", user=nickname, text=ev.gift.name, count=count)
            )

        @self.client.on(JoinEvent)  # type: ignore[untyped-decorator]
        async def _on_join(ev: JoinEvent) -> None:
            nickname = ev.user.nickname or ev.user.unique_id or "anon"
            await self.callback(TTEvent(type="join", user=nickname))

        @self.client.on(LikeEvent)  # type: ignore[untyped-decorator]
        async def _on_like(ev: LikeEvent) -> None:
            nickname = ev.user.nickname or ev.user.unique_id or "anon"
            await self.callback(
                TTEvent(type="like", user=nickname, count=ev.count or 1)
            )

    async def run_with_retry(
        self, initial_backoff_s: int = 30, max_backoff_s: int = 300
    ) -> None:
        """Run the client with exponential backoff if stream is offline.

        Blocks until cancellation. Reconnects automatically when user goes live.
        """
        backoff = initial_backoff_s
        while True:
            try:
                await self.client.connect()
                # Clean disconnect — reset backoff for next cycle.
                backoff = initial_backoff_s
            except UserOfflineError:
                log.warning(
                    "@%s is OFFLINE, retry in %ds", self.unique_id, backoff
                )
                await self.callback(
                    TTEvent(type="offline", user=self.unique_id)
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, max_backoff_s)
            except asyncio.CancelledError:
                log.info("TikTok adapter cancelled")
                raise
            except Exception as e:  # noqa: BLE001 — defensive, surface to log
                log.error("TikTok client error: %s — retry in %ds", e, backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, max_backoff_s)
