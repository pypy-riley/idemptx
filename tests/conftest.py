import fakeredis
import pytest
import pytest_asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from idemptx.backend.memory import InMemoryBackend
from idemptx.backend.redis import AsyncRedisBackend, RedisBackend
from idemptx.decorator import idempotent
from idemptx.exceptions import ConflictRequestException, MissingKeyException


@pytest.fixture(params=['memory', 'redis', 'async-redis'])
def backend(request):
    if request.param == 'memory':
        return InMemoryBackend()
    elif request.param == 'redis':
        redis_client = fakeredis.FakeRedis(decode_responses=True)
        return RedisBackend(redis_client)
    elif request.param == 'async-redis':
        redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
        return AsyncRedisBackend(redis_client)


@pytest.fixture
def app(backend):
    app = FastAPI()

    @app.exception_handler(MissingKeyException)
    async def handle_missing_key(request: Request, exc: MissingKeyException):
        return JSONResponse(status_code=400, content={'detail': str(exc)})

    @app.exception_handler(ConflictRequestException)
    async def handle_conflict(request: Request, exc: ConflictRequestException):
        return JSONResponse(status_code=409, content={'detail': str(exc)})

    @app.post('/echo')
    @idempotent(storage_backend=backend)
    async def echo(request: Request):
        data = await request.json()
        return JSONResponse(content={'echo': data})

    return app


@pytest.fixture
def sync_client(app, backend):
    if isinstance(backend, AsyncRedisBackend):
        return None
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(app, backend):
    if not isinstance(backend, AsyncRedisBackend):
        yield None
        return
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client
