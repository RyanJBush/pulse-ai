from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class CacheItem(Generic[T]):
    value: T
    expires_at: datetime


class TTLCache(Generic[T]):
    def __init__(self, ttl_seconds: int = 30):
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, CacheItem[T]] = {}
        self._lock = Lock()

    def get(self, key: str) -> T | None:
        now = datetime.now(timezone.utc)
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            if item.expires_at <= now:
                self._items.pop(key, None)
                return None
            return item.value

    def set(self, key: str, value: T) -> None:
        with self._lock:
            self._items[key] = CacheItem(
                value=value,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds),
            )

    def invalidate(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._items.clear()
            else:
                self._items.pop(key, None)
