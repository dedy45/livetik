"""Reply queue — asyncio.Queue(20) processed one-at-a-time (TTS lock inside tts adapter)."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass(slots=True)
class ReplyJob:
    user: str
    text: str
    ts: float


ReplyHandler = Callable[[ReplyJob], Awaitable[None]]


class ReplyQueue:
    def __init__(self, maxsize: int = 20) -> None:
        self._q: asyncio.Queue[ReplyJob] = asyncio.Queue(maxsize=maxsize)
        self._worker_task: asyncio.Task[None] | None = None

    def size(self) -> int:
        return self._q.qsize()

    async def put(self, job: ReplyJob) -> bool:
        try:
            self._q.put_nowait(job)
            return True
        except asyncio.QueueFull:
            log.warning("queue FULL, dropping job user=%s", job.user)
            return False

    def start_worker(self, handler: ReplyHandler) -> None:
        if self._worker_task and not self._worker_task.done():
            return
        self._worker_task = asyncio.create_task(self._run(handler), name="reply-worker")

    async def _run(self, handler: ReplyHandler) -> None:
        while True:
            job = await self._q.get()
            try:
                await handler(job)
            except Exception as e:
                log.error("reply handler failed for %s: %s", job.user, e)
            finally:
                self._q.task_done()

    async def stop(self) -> None:
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
