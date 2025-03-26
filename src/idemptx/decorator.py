import asyncio
import hashlib
import inspect
import json
import logging
from functools import wraps
from typing import Annotated, Any, Callable, TypeVar

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from .backend.base import AsyncStorageBackend, StorageBackend
from .exceptions import ConflictRequestException, MissingKeyException, RequestInProgressException

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable)


def hash_request(request: Request, body: bytes) -> str:
    """
    Generates a unique signature based on the request's method, URL, headers, and body content.
    """

    headers = dict(request.headers)
    headers_str = json.dumps(headers, sort_keys=True)

    raw = f'{request.method} {request.url!s} {headers_str} {body.decode()}'
    return hashlib.sha256(raw.encode()).hexdigest()


async def _maybe_await(result: Any) -> Any:
    """
    Awaits the result if it's awaitable, otherwise returns it directly.
    """
    if inspect.isawaitable(result):
        return await result
    return result


async def _get_cached_response(
    storage_backend: StorageBackend | AsyncStorageBackend, cache_key: str, req_signature: str, validate: bool
) -> JSONResponse | None:
    """
    Internal helper to get cache and validate signature.
    Returns JSONResponse if valid cache exists, else None.
    """
    cached = await _maybe_await(storage_backend.get(cache_key))
    if not cached:
        return None

    if validate and cached.get('request_signature') != req_signature:
        raise ConflictRequestException('Request payload does not match previous Idempotency-Key usage.')

    response_headers = dict(cached.get('headers', {}))
    response_headers['X-Idempotency-Status'] = 'hit'

    return JSONResponse(
        content=cached['data'],
        status_code=cached['status_code'],
        headers=response_headers,
    )


async def _wait_for_cached_response(
    storage_backend, cache_key: str, req_signature: str, validate: bool, timeout: float, interval: float = 0.1
) -> JSONResponse | None:
    """
    Waits until a valid cached response is available or timeout is reached.

    Returns:
        JSONResponse if found within timeout, else None
    """
    waited = 0.0
    while waited < timeout:
        await asyncio.sleep(interval)
        waited += interval

        cached_response = await _get_cached_response(
            storage_backend=storage_backend, cache_key=cache_key, req_signature=req_signature, validate=validate
        )
        if cached_response:
            return cached_response

    return None


def idempotent(  # noqa: C901
    storage_backend: Annotated[
        StorageBackend | AsyncStorageBackend, 'Implements the idempotency storage logic (e.g., RedisBackend)'
    ],
    key_ttl: Annotated[int, 'TTL for the cache and lock, in seconds'] = 300,
    required: Annotated[bool, 'Whether Idempotency-Key header is required'] = True,
    wait_timeout: Annotated[
        float, 'Maximum time to wait (in seconds) for the first request to complete. Set to 0 to disable waiting.'
    ] = 0,
    validate_signature: Annotated[bool, 'Whether to validate request signature against cached one'] = True,
) -> Callable[[F], F]:
    """
    FastAPI decorator that provides idempotency support.
    """

    def decorator(func: F) -> F:  # noqa: C901
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request')
            if request is None:
                raise ValueError(
                    'Missing "request" in endpoint parameters. Please include "request: Request" as an argument in your FastAPI route function.'
                )

            idempotency_key = request.headers.get('Idempotency-Key')
            if not idempotency_key:
                if required:
                    raise MissingKeyException('Missing Idempotency-Key')
                return await func(*args, **kwargs)

            body = await request.body()
            req_signature = hash_request(request, body)
            cache_key = f'idempotency:{request.url.path}:{idempotency_key}'

            # Check if already cached
            cached_response = await _get_cached_response(
                storage_backend, cache_key, req_signature, validate=validate_signature
            )
            if cached_response:
                return cached_response

            lock_acquired = await _maybe_await(storage_backend.acquire_lock(cache_key, ttl=key_ttl))
            if not lock_acquired:
                if wait_timeout > 0:
                    cached_response = await _wait_for_cached_response(
                        storage_backend,
                        cache_key,
                        req_signature,
                        validate=validate_signature,
                        timeout=wait_timeout,
                    )
                    if cached_response:
                        return cached_response

                    # timeout or still no cached value
                raise RequestInProgressException('Request is being processed. Try again later.')

            try:
                response: Response = await func(*args, **kwargs)
                response.headers['Idempotency-Key'] = idempotency_key
                response.headers['X-Idempotency-Signature'] = req_signature

                if isinstance(response, JSONResponse):
                    try:
                        json_data = json.loads(response.body)
                        response_headers = dict(response.headers)
                        await _maybe_await(
                            storage_backend.set(
                                cache_key,
                                {
                                    'data': json_data,
                                    'status_code': response.status_code,
                                    'headers': response_headers,
                                    'request_signature': req_signature,
                                },
                                ttl=key_ttl,
                            )
                        )

                    except Exception as e:
                        logger.error(f'Failed to cache response: {e}')

                response.headers['X-Idempotency-Status'] = 'new'
                return response

            finally:
                await _maybe_await(storage_backend.release_lock(cache_key))

        return wrapper

    return decorator
