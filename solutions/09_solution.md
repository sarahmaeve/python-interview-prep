# Solution: Exercise 09 -- External API Client

## Bugs Found

### Bug 1: Wrong JSON key in `get_temperature`

**Location:** `get_temperature`, line 26

The code reads `data["main"]["temperature"]`, but the API returns the key `"temp"`.

**Diagnosis:** The test `test_returns_temperature_as_float` mocks the response as `{"main": {"temp": 22.5}}`. Accessing `["temperature"]` raises `KeyError`.

**Before:**
```python
return float(data["main"]["temperature"])
```

**After:**
```python
return float(data["main"]["temp"])
```

**Why it matters:** Always match the exact key names from the API contract. A mismatch silently compiles but fails at runtime -- tests that mock the real response shape catch this instantly.

---

### Bug 2: Off-by-one in `get_temperature_with_retry`

**Location:** `get_temperature_with_retry`, line 43

`range(retries)` produces `0, 1, ..., retries-1`. The condition `attempt == retries` is never true, so the exception is silently swallowed on the last attempt and the function returns `None`.

**Diagnosis:** `test_raises_after_all_retries_exhausted` expects `URLError` to propagate after 2 attempts. With the bug, the loop ends without raising.

**Before:**
```python
if attempt == retries:
    raise
```

**After:**
```python
if attempt == retries - 1:
    raise
```

**Why it matters:** Off-by-one errors in retry loops are common. A useful mental model: `range(n)` ends at `n-1`, so the last attempt index is `n-1`.

---

### Bug 3: City name not URL-encoded in `get_forecast`

**Location:** `get_forecast`, line 31

Spaces in city names (e.g., "New York") produce invalid URLs.

**Diagnosis:** `test_url_encodes_city_name` asserts no raw space in the URL and expects `New%20York`.

**Before:**
```python
url = f"{self.base_url}/forecast?city={city}&days={days}"
```

**After:**
```python
from urllib.parse import quote
# ...
url = f"{self.base_url}/forecast?city={quote(city)}&days={days}"
```

(Add `from urllib.parse import quote` at the top of the file.)

**Why it matters:** Any user-supplied string embedded in a URL must be percent-encoded. This is a security and correctness concern -- unencoded values can break request parsing or enable injection.

---

## Discussion

- **Mocking `urlopen`:** Patching at the module level (`weather_client.urlopen`) ensures no real HTTP calls are made. This is the standard pattern for testing I/O boundaries.
- **Retry design:** The retry method delegates to `get_temperature`, keeping retry logic separate from request logic. An alternative is to use a decorator like `tenacity.retry`.
- **URL building:** For production code, consider `urllib.parse.urlencode` to handle all query parameters uniformly rather than encoding them one at a time.
