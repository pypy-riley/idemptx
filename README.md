# 🧹 idemptx

[![PyPI - Version](https://img.shields.io/pypi/v/idemptx?color=blue)](https://pypi.org/project/idemptx/)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

> A minimal, pluggable idempotency decorator for FastAPI, designed for payment and retry-safe APIs.

Supports Redis as backend for deduplication, distributed locking, and response caching.

---

## ✨ Features

- ✅ Supports `Idempotency-Key` header out of the box
- 🔒 Redis-backed lock to prevent double execution
- ⚡️ Sync & Async backends with auto-detection
- 🧠 Request signature validation (method + URL + headers + body)
- ⏳ Configurable `wait_timeout` behavior
- 🔁 Response replay from cache (with headers)
- 🔢 In-memory backend for testing/local use

---

## 📦 Installation

```bash
pip install idemptx
```

---

## 🚀 Quick Start

```python
import redis
from fastapi import FastAPI, Request
from idemptx import idempotent
from idemptx.backend import RedisBackend

app = FastAPI()
client = redis.Redis(host='localhost', port=6379, db=0)
redis_backend = RedisBackend(client)

@app.post('/orders')
@idempotent(storage_backend=redis_backend)
async def create_order(request: Request):
    return {'status': 'created'}
```

> ⚠️ You must include `request: Request` in your endpoint parameters!

---

## 🔧 Advanced Usage

```python
@idempotent(
    storage_backend=redis_backend,
    key_ttl=60,
    wait_timeout=3.0,
    validate_signature=True,
)
```

- `key_ttl`: How long to hold cache and lock (in seconds)
- `wait_timeout`: Wait for lock to be released (0 = immediate failure)
- `validate_signature`: Whether to compare request content on replays

---

## 🔀 Async Redis Backend

```python
import redis.asyncio as aioredis
from idemptx.backend import AsyncRedisBackend

async_client = aioredis.Redis(host='localhost', port=6379, db=0)
async_backend = AsyncRedisBackend(async_client)
```

---

## 🔖 In-memory Backend (for testing only)

```python
from idemptx.backend import InMemoryBackend

backend = InMemoryBackend()

@app.post('/example')
@idempotent(storage_backend=backend)
async def create_something(request: Request):
    return {'ok': True}
```

> Note: Not suitable for multi-process or production environments.

---

## 🔐 Response Headers

| Header                    | Description                            |
|---------------------------|----------------------------------------|
| `Idempotency-Key`         | Echoed back to client                  |
| `X-Idempotency-Signature` | Hash of request for conflict detection |
| `X-Idempotency-Status`    | `"hit"` or `"new"`                     |

---

## ❗️Limitations

Currently, only `JSONResponse` is supported for caching.

If your endpoint uses `response_model`, the return value is typically a Pydantic model, which FastAPI wraps *after* the decorator has executed. This means the idempotency decorator cannot cache the final serialized response or set headers reliably in this case.

To enable caching, please return a `JSONResponse` explicitly from your endpoint.

Support for `response_model` and automatic response wrapping may be added in a future version.

---

## 📄 License

MIT License © 2025 [pypy-riley](https://github.com/pypy-riley)
