from __future__ import annotations

from collections import deque
from threading import Lock

from app.schemas.event import EventCreate


class IngestionBuffer:
    def __init__(self):
        self._queue: deque[EventCreate] = deque()
        self._lock = Lock()
        self._enqueued = 0
        self._flushed = 0

    def enqueue_many(self, events: list[EventCreate]) -> int:
        with self._lock:
            for event in events:
                self._queue.append(event)
            self._enqueued += len(events)
            return len(self._queue)

    def drain(self, limit: int | None = None) -> list[EventCreate]:
        drained: list[EventCreate] = []
        with self._lock:
            target = len(self._queue) if limit is None else min(limit, len(self._queue))
            for _ in range(target):
                drained.append(self._queue.popleft())
            self._flushed += len(drained)
        return drained

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "queued": len(self._queue),
                "total_enqueued": self._enqueued,
                "total_flushed": self._flushed,
            }


buffer_instance = IngestionBuffer()
