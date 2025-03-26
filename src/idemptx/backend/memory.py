import threading
import time
from typing import Annotated

from .base import StorageBackend


class InMemoryBackend(StorageBackend):
    """
    In-memory implementation of the StorageBackend interface.

    This backend is useful for local development, testing, or single-instance deployments.
    It is not recommended for production use in distributed or multi-worker environments.
    """

    def __init__(self):
        self._store: dict[str, tuple[float, dict]] = {}
        self._locks: dict[str, float] = {}
        self._lock = threading.Lock()

    def _now(self) -> float:
        return time.time()

    def get(self, key: Annotated[str, 'Cache key']) -> dict | None:
        with self._lock:
            entry = self._store.get(key)
            if entry and self._now() < entry[0]:
                return entry[1]
            return None

    def set(self, key: Annotated[str, 'Cache key'], value: dict, ttl: int) -> None:
        with self._lock:
            self._store[key] = (self._now() + ttl, value)

    def acquire_lock(self, key: Annotated[str, 'Lock key'], ttl: int) -> bool:
        with self._lock:
            now = self._now()
            if key not in self._locks or now > self._locks[key]:
                self._locks[key] = now + ttl
                return True
            return False

    def release_lock(self, key: Annotated[str, 'Lock key']) -> None:
        with self._lock:
            self._locks.pop(key, None)
