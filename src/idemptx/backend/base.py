from abc import ABC, abstractmethod
from typing import Annotated


class StorageBackend(ABC):
    """
    Abstract base class for implementing idempotency key storage.

    This interface defines the required methods for storing and retrieving
    cached responses and request locks used in idempotent API handling.
    """

    @abstractmethod
    def get(self, key: Annotated[str, 'The cache key to retrieve']) -> dict | None:
        """
        Retrieve a cached response by key.

        :param key: The cache key used for retrieval (usually includes path + Idempotency-Key)
        :return: A dictionary containing cached response data, or None if not found
        """
        pass

    @abstractmethod
    def set(
        self,
        key: Annotated[str, 'The cache key to store under'],
        value: Annotated[dict, 'The response payload to cache'],
        ttl: Annotated[int, 'Time-to-live for the cached value (in seconds)'],
    ) -> None:
        """
        Store a response value in the cache with expiration.

        :param key: The cache key to store the data under
        :param value: Dictionary with response data, status code, headers, etc.
        :param ttl: Time in seconds the value should remain in the cache
        """
        pass

    @abstractmethod
    def acquire_lock(
        self,
        key: Annotated[str, 'The cache key to lock (same as cache key)'],
        ttl: Annotated[int, 'Expiration for the lock (in seconds)'],
    ) -> bool:
        """
        Attempt to acquire a lock for the given key.

        :param key: The key to lock (usually same as the cache key)
        :param ttl: Lock expiration time in seconds
        :return: True if the lock was successfully acquired, False otherwise
        """
        pass

    @abstractmethod
    def release_lock(self, key: Annotated[str, 'The lock key to release']) -> None:
        """
        Release the lock for a given key.

        :param key: The key to release the lock on
        """
        pass


class AsyncStorageBackend(ABC):
    """
    Abstract base class for implementing asynchronous idempotency key storage.

    This interface defines async versions of the required methods for
    storing and retrieving cached responses and locks in idempotent API handling.
    """

    @abstractmethod
    async def get(self, key: Annotated[str, 'Cache key']) -> dict | None:
        """
        Asynchronously retrieve a cached response by key.

        :param key: The cache key used for retrieval (usually includes path + Idempotency-Key)
        :return: A dictionary containing cached response data, or None if not found
        """
        pass

    @abstractmethod
    async def set(self, key: Annotated[str, 'Cache key'], value: dict, ttl: int) -> None:
        """
        Asynchronously store a response in the cache with TTL.

        :param key: The cache key to store the data under
        :param value: Dictionary with response data, status code, headers, etc.
        :param ttl: Time in seconds the value should remain in the cache
        """
        pass

    @abstractmethod
    async def acquire_lock(self, key: Annotated[str, 'Lock key'], ttl: int) -> bool:
        """
        Attempt to acquire a lock for the given key asynchronously.

        :param key: The key to lock (usually same as the cache key)
        :param ttl: Lock expiration time in seconds
        :return: True if the lock was successfully acquired, False otherwise
        """
        pass

    @abstractmethod
    async def release_lock(self, key: Annotated[str, 'Lock key']) -> None:
        """
        Asynchronously release the lock for a given key.

        :param key: The key to release the lock on
        """
        pass
