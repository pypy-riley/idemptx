class IdempotencyException(Exception):
    """Base exception class for all idempotency-related errors."""

    pass


class MissingKeyException(IdempotencyException):
    """Raised when the Idempotency-Key header is missing but required."""

    pass


class IdempotencyConflictException(IdempotencyException):
    """Base class for idempotency conflicts, such as mismatched requests or in-progress operations."""

    pass


class ConflictRequestException(IdempotencyConflictException):
    """Raised when the same Idempotency-Key is used with different request content."""

    pass


class RequestInProgressException(IdempotencyConflictException):
    """Raised when the same Idempotency-Key is currently being processed by another request."""

    pass
