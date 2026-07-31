"""Reproduce the duplicate-job symptom reported by the incident scenario."""

from job_submitter import JobSubmitter, TransientSubmissionError


class IncidentGateway:
    """Record accepted jobs while losing the first response."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.accepted: dict[str, int] = {}
        self._lose_first_response = True

    def submit(self, payload: str, *, idempotency_key: str) -> int:
        self.calls.append((payload, idempotency_key))
        if idempotency_key not in self.accepted:
            self.accepted[idempotency_key] = 100 + len(self.accepted)

        result = self.accepted[idempotency_key]
        if self._lose_first_response:
            self._lose_first_response = False
            raise TransientSubmissionError("response lost after acceptance")
        return result


def main() -> None:
    gateway = IncidentGateway()
    keys = iter(("attempt-a", "attempt-b", "attempt-c"))
    submitter = JobSubmitter(gateway, key_factory=lambda: next(keys))

    result = submitter.submit("build-report", operation_id="operation-7")

    print("logical operation: operation-7")
    print(f"returned job: {result}")
    print("gateway calls:")
    for payload, key in gateway.calls:
        print(f"  payload={payload} idempotency_key={key}")
    print("accepted remote jobs:")
    for key, job_id in gateway.accepted.items():
        print(f"  idempotency_key={key} job={job_id}")
    print(f"remote job count: {len(gateway.accepted)}")


if __name__ == "__main__":
    main()

