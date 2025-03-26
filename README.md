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

---

## 📦 Installation

```bash
pip install idemptx
```

---

## 🚀 Quick Start

```python
from fastapi import FastAPI, Request
from idemptx import idempotent
from idemptx.backend.redis import RedisBackend

app = FastAPI()
redis_backend = RedisBackend()

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

## 🔐 Response Headers

| Header | Description |
|--------|-------------|
| `Idempotency-Key` | Echoed back to client |
| `X-Idempotency-Signature` | Hash of request for conflict detection |
| `X-Idempotency-Status` | `"hit"` or `"new"` |

---

## 📄 License

MIT License © 2025 [pypy-riley](https://github.com/pypy-riley)

