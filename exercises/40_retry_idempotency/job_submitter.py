"""Retrying job submission with idempotency bugs."""

import uuid
from collections.abc import Callable
from typing import Protocol


class TransientSubmissionError(Exception):
    """The submission outcome is unknown and the operation may be retried."""


class IdempotencyConflict(ValueError):
    """An operation ID was reused for a different request."""


class JobGateway(Protocol):
    """Remote job-creation boundary."""

    def submit(self, payload: str, *, idempotency_key: str) -> int:
        """Return the remote job ID."""


class JobSubmitter:
    """Submit jobs with retries and local completed-result caching."""

    def __init__(
        self,
        gateway: JobGateway,
        key_factory: Callable[[], str] | None = None,
    ) -> None:
        self.gateway = gateway
        self._key_factory = key_factory or (lambda: uuid.uuid4().hex)
        self._payloads: dict[str, str] = {}
        self._results: dict[str, int] = {}

    def submit(
        self,
        payload: str,
        *,
        operation_id: str | None = None,
        max_attempts: int = 3,
    ) -> int:
        """Submit one logical operation, retrying ambiguous failures."""
        operation_id = operation_id or self._key_factory()
        self._payloads[operation_id] = payload

        cached = self._results.get(operation_id)
        if cached:
            return cached

        last_error: TransientSubmissionError | None = None
        for _ in range(max_attempts):
            attempt_key = self._key_factory()
            try:
                result = self.gateway.submit(
                    payload,
                    idempotency_key=attempt_key,
                )
            except TransientSubmissionError as exc:
                last_error = exc
            else:
                self._results[operation_id] = result
                return result

        assert last_error is not None
        raise last_error
