"""
idemptx - FastAPI Idempotency Decorator

Exposes:
- `idempotent`: The main decorator to apply to your FastAPI routes.
- Exception hierarchy for idempotency-related errors.
"""

from .decorator import idempotent
from .exceptions import (
    ConflictRequestException,
    IdempotencyConflictException,
    IdempotencyException,
    MissingKeyException,
    RequestInProgressException,
)

__all__ = [
    'idempotent',
    'IdempotencyException',
    'MissingKeyException',
    'IdempotencyConflictException',
    'ConflictRequestException',
    'RequestInProgressException',
]
