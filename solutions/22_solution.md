# Solution: Exercise 22 — Systems Integration

## Bugs Found

### Bug 1 — Timeout not passed to urlopen

**Location:** `service_client.py`, `fetch()` method

```python
# Before (no timeout — can hang forever)
response = urlopen(url)

# After
response = urlopen(url, timeout=self.config["timeout"])
```

**Why it matters:** Without an explicit timeout, `urlopen` uses the system's default socket timeout, which can be very long (or infinite). In CI, a hung request can consume the entire build timeout with no useful error message. The `test_fetch_passes_timeout` test verifies the timeout is actually passed through.

### Bug 2 — Import-time default argument

**Location:** `service_client.py`, `ServiceClient.__init__`

```python
# Before (get_config() evaluated ONCE at import time)
class ServiceClient:
    def __init__(self, config=get_config()):
        self.config = config

# After (get_config() evaluated at call time)
class ServiceClient:
    def __init__(self, config=None):
        self.config = config if config is not None else get_config()
```

**Why it matters:** The default argument `config=get_config()` is evaluated when the class is defined (import time), not when `__init__` is called. Tests that set `os.environ` before creating a client still get the old config from import time. The `test_config_not_cached_at_import` test exposes this by setting `API_BASE_URL` in the environment and checking that a new client sees it.

This is the same mutable-default trap from Exercise 06, but with a function call instead of a list literal.

### Bug 3 — health_check reads environment directly

**Location:** `service_client.py`, `health_check()` method

```python
# Before (reads os.environ, ignoring injected config)
if os.environ.get("CI", "").lower() in ("true", "1"):
    return True

# After (uses the config that was injected or loaded)
if self.config["is_ci"]:
    return True
```

**Why it matters:** The rest of the class uses `self.config` for all settings, but `health_check` bypasses this and reads `os.environ` directly. This means tests can't control the CI flag by injecting a config dict — the behavior depends on the actual environment. The `test_health_check_uses_config_ci_flag` test catches this by injecting `{"is_ci": True}` while clearing `os.environ`.

## Diagnosis Process

The three test failures point directly at the three bugs:

1. `test_fetch_passes_timeout` — asserts `kwargs.get("timeout") == 7`, gets `None`
2. `test_config_not_cached_at_import` — asserts `base_url == "http://env-server:5000"`, gets `"http://localhost:8080"`
3. `test_health_check_uses_config_ci_flag` — asserts `True`, gets `False`

Each failure message tells you exactly what's wrong. The skill is connecting the test expectation to the code path.

## Discussion Question Perspectives

**1. Environment parity:** If CI uses `http://ci-mock-server` and production uses `http://real-api.internal`, you're not testing real network behavior. Use the same base URL structure in CI. Better: inject the full config so tests don't depend on any environment variables.

**2. Retry in CI:** 3 retries × 2-second backoff × hundreds of tests = potentially hours of waiting on transient failures. In CI, consider `retries=1` or `retries=0` with a separate integration test step that does retry. Fast feedback > resilience in CI.

**3. Timeout tuning:** 50 tests × 30s timeout = 25 minutes worst case, but the build times out at 5 minutes. Set per-request timeout to ~5s in CI. Too low and you'll get false failures on slow queries. The key insight: the per-request timeout must be much less than `(build timeout / test count)`.

**4. Health check skip:** Pros: CI runs fast, no flaky health check failures. Cons: if the service config is wrong (typo in URL, wrong port), you won't find out until production. A middle ground: run the health check but make it non-blocking (log a warning, don't fail the build).

**5. Mocking vs. real services:** Mocks are fast, deterministic, and test your code's logic. Real services test integration, catch serialization bugs, and validate API contracts. Use mocks for unit tests (fast feedback) and a real service for a small set of integration tests (catch interface bugs). Don't mock everything — that tests your mocks, not your code.
