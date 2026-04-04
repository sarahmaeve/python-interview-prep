# Exercise 22: Systems Integration

An HTTP service client with retries, timeouts, and environment-aware configuration. The implementation has **3 bugs** — all related to how the code interacts with its deployment environment.

**This exercise practices:** environment variables, retry/timeout patterns, CI vs. local behavior differences, and dependency injection for testability.

## How to run the tests

```bash
cd exercises/22_systems_integration
python -m unittest test_service_client
```

Your goal: edit `service_client.py` until all tests pass.

## Bugs: 3

<details>
<summary>Hint 1 (gentle)</summary>

The timeout is configured but never actually used. Check the `urlopen()` call.
</details>

<details>
<summary>Hint 2 (moderate)</summary>

Default arguments are evaluated once, at function/class definition time. What happens if `get_config()` is used as a default parameter value in `__init__`? What do tests that set `os.environ` before creating a client see?

Also: `health_check()` checks the environment directly instead of using the injected config. Why does that matter for tests?
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. **Timeout not passed**: `fetch()` calls `urlopen(url)` without the `timeout` keyword argument. Fix: `urlopen(url, timeout=self.config["timeout"])`.

2. **Import-time default argument**: `__init__` has `config=get_config()` — this captures environment variables at import time. Tests that modify `os.environ` after import see stale config. Fix: change to `config=None` and call `get_config()` inside the method body.

3. **Direct environment access in health_check**: `health_check()` reads `os.environ.get("CI")` directly instead of `self.config["is_ci"]`. This bypasses injected config, making the method untestable. Fix: check `self.config["is_ci"]` instead.
</details>

## Discussion Questions

After fixing the bugs, consider these questions. There's no single right answer — the goal is to practice articulating trade-offs, as you would in the interview's "systems dialogue" portion.

1. **Environment parity**: This code reads `API_BASE_URL` from the environment. What could go wrong if CI uses a different base URL than production? How would you ensure the test environment is representative?

2. **Retry in CI**: The retry count defaults to 3. In a CI pipeline running hundreds of test suites, what is the impact of retries on total build time? Should CI use fewer retries? Should it use any?

3. **Timeout tuning**: The default timeout is 30 seconds. If a CI build has a 5-minute overall timeout and runs 50 tests that each make HTTP calls, what per-request timeout would be safe? What happens if you set it too low?

4. **Health check skip**: In CI mode, `health_check()` returns True without calling the service. What are the pros and cons of this approach? When would this mask a real failure?

5. **Mocking vs. real services**: The tests mock `urlopen`. An alternative is to run a local test server. What are the trade-offs? When would you choose one approach over the other?
