import json
from typing import Annotated

import redis
import redis.asyncio as aioredis

from .base import AsyncStorageBackend, StorageBackend


class BaseRedisBackend:
    """
    Shared base logic for both sync and async Redis backends.
    Provides common key formatting and JSON serialization.
    """

    def __init__(self, prefix: Annotated[str, 'Key prefix namespace'] = 'idempotency:'):
        self.prefix = prefix

    def _key(self, key: str) -> str:
        return f'{self.prefix}{key}'

    def _lock_key(self, key: str) -> str:
        return f'{self._key(key)}:lock'

    @staticmethod
    def _encode(value: dict) -> str:
        return json.dumps(value)

    @staticmethod
    def _decode(value: bytes | str | None) -> dict | None:
        if not value:
            return None
        return json.loads(value)


class RedisBackend(StorageBackend, BaseRedisBackend):
    """
    Redis-based synchronous implementation of the StorageBackend interface.

    Stores idempotent response payloads and manages distributed locks using Redis.
    """

    def __init__(
        self,
        host: Annotated[str, 'Redis host'] = 'localhost',
        port: Annotated[int, 'Redis port'] = 6379,
        db: Annotated[int, 'Redis DB index'] = 0,
        prefix: Annotated[str, 'Key prefix namespace'] = 'idempotency:',
    ):
        self.redis = redis.Redis(host=host, port=port, db=db)
        super().__init__(prefix=prefix)

    def get(self, key: str) -> dict | None:
        return self._decode(self.redis.get(self._key(key)))

    def set(self, key: str, value: dict, ttl: int) -> None:
        self.redis.set(self._key(key), self._encode(value), ex=ttl)

    def acquire_lock(self, key: str, ttl: int) -> bool:
        return bool(self.redis.set(self._lock_key(key), '1', nx=True, ex=ttl))

    def release_lock(self, key: str) -> None:
        self.redis.delete(self._lock_key(key))


class AsyncRedisBackend(AsyncStorageBackend, BaseRedisBackend):
    """
    Redis-based asynchronous implementation of the AsyncStorageBackend interface.

    Supports awaitable operations for idempotent response caching and distributed locking.
    """

    def __init__(
        self,
        host: Annotated[str, 'Redis host'] = 'localhost',
        port: Annotated[int, 'Redis port'] = 6379,
        db: Annotated[int, 'Redis DB index'] = 0,
        prefix: Annotated[str, 'Key prefix namespace'] = 'idempotency:',
    ):
        self.redis = aioredis.Redis(host=host, port=port, db=db)
        super().__init__(prefix=prefix)

    async def get(self, key: str) -> dict | None:
        return self._decode(await self.redis.get(self._key(key)))

    async def set(self, key: str, value: dict, ttl: int) -> None:
        await self.redis.set(self._key(key), self._encode(value), ex=ttl)

    async def acquire_lock(self, key: str, ttl: int) -> bool:
        return await self.redis.set(self._lock_key(key), '1', nx=True, ex=ttl)

    async def release_lock(self, key: str) -> None:
        await self.redis.delete(self._lock_key(key))
