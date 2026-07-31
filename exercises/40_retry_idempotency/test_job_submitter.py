"""Tests for retry idempotency and completed-result caching."""

import unittest

from job_submitter import (
    IdempotencyConflict,
    JobSubmitter,
    TransientSubmissionError,
)


class RecordingGateway:
    def __init__(self, result: int = 42) -> None:
        self.result = result
        self.calls: list[tuple[str, str]] = []

    def submit(self, payload: str, *, idempotency_key: str) -> int:
        self.calls.append((payload, idempotency_key))
        return self.result


class AmbiguousGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.accepted: dict[str, int] = {}
        self._first_response_is_lost = True

    def submit(self, payload: str, *, idempotency_key: str) -> int:
        self.calls.append((payload, idempotency_key))
        if idempotency_key not in self.accepted:
            self.accepted[idempotency_key] = 100 + len(self.accepted)

        result = self.accepted[idempotency_key]
        if self._first_response_is_lost:
            self._first_response_is_lost = False
            raise TransientSubmissionError("response lost after acceptance")
        return result


class AlwaysTransientGateway:
    def __init__(self) -> None:
        self.calls = 0

    def submit(self, payload: str, *, idempotency_key: str) -> int:
        self.calls += 1
        raise TransientSubmissionError("still unavailable")


def key_factory(*keys: str):
    values = iter(keys)
    return lambda: next(values)


class TestStableOperationIdentity(unittest.TestCase):
    def test_ambiguous_retry_creates_only_one_remote_job(self):
        gateway = AmbiguousGateway()
        submitter = JobSubmitter(
            gateway,
            key_factory("attempt-a", "attempt-b", "attempt-c"),
        )

        result = submitter.submit("build-report", operation_id="operation-7")

        self.assertEqual(result, 100)
        self.assertEqual(len(gateway.accepted), 1)
        self.assertEqual(
            [key for _payload, key in gateway.calls],
            ["operation-7", "operation-7"],
        )

    def test_generated_operation_id_is_reused_for_attempt(self):
        gateway = RecordingGateway()
        submitter = JobSubmitter(
            gateway,
            key_factory("generated-1", "attempt-1"),
        )

        submitter.submit("build-report")

        self.assertEqual(gateway.calls, [("build-report", "generated-1")])


class TestCompletedResultCache(unittest.TestCase):
    def test_falsy_completed_result_is_still_cached(self):
        gateway = RecordingGateway(result=0)
        submitter = JobSubmitter(gateway, key_factory("unused-a", "unused-b"))

        first = submitter.submit("empty-batch", operation_id="operation-0")
        second = submitter.submit("empty-batch", operation_id="operation-0")

        self.assertEqual((first, second), (0, 0))
        self.assertEqual(len(gateway.calls), 1)

    def test_truthy_completed_result_is_cached(self):
        gateway = RecordingGateway(result=81)
        submitter = JobSubmitter(gateway, key_factory("unused"))

        first = submitter.submit("build-report", operation_id="operation-8")
        second = submitter.submit("build-report", operation_id="operation-8")

        self.assertEqual((first, second), (81, 81))
        self.assertEqual(len(gateway.calls), 1)


class TestOperationConflicts(unittest.TestCase):
    def test_same_operation_id_rejects_different_payload(self):
        gateway = RecordingGateway(result=81)
        submitter = JobSubmitter(gateway, key_factory("unused"))
        submitter.submit("build-report", operation_id="operation-8")

        with self.assertRaisesRegex(IdempotencyConflict, "operation-8"):
            submitter.submit("delete-report", operation_id="operation-8")

        self.assertEqual(len(gateway.calls), 1)


class TestRetryContract(unittest.TestCase):
    def test_transient_failures_stop_at_max_attempts(self):
        gateway = AlwaysTransientGateway()
        submitter = JobSubmitter(
            gateway,
            key_factory("attempt-a", "attempt-b", "attempt-c"),
        )

        with self.assertRaises(TransientSubmissionError):
            submitter.submit(
                "build-report",
                operation_id="operation-9",
                max_attempts=3,
            )

        self.assertEqual(gateway.calls, 3)


if __name__ == "__main__":
    unittest.main()
