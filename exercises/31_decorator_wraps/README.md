# Exercise 31: Decorator `@wraps` and State

Three decorators, each with a bug. The implementation has **3 bugs** that collectively cover the most common decorator mistakes:

1. Forgetting `@functools.wraps` entirely.
2. Applying `@functools.wraps` to the wrong target.
3. Using class-level state where per-instance state was intended.

## How to run the tests

```bash
cd exercises/31_decorator_wraps
python3 -m unittest test_decorators
```

Your goal is to edit `decorators.py` until all tests pass. Do **not** modify the test file.

## Decorators under test

- `@log_calls` — logs entry/exit of each call.
- `@retry(n)` — retries on exception up to n attempts.
- `@count_calls` — class-based decorator that counts how many times each decorated function is called.

## Hints

<details>
<summary>Hint 1 (gentle)</summary>

Every bug relates to a small piece of decorator boilerplate that Guide 11 Sections 6 and 8 cover:
- `@functools.wraps(func)` on the inner wrapper.
- Where to put that decorator when your own decorator takes arguments.
- Whether a class-based decorator stores its state on the instance or on the class.

</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. `log_calls` never calls `@functools.wraps(func)` on its `wrapper` — so decorated functions show up as `"wrapper"` under introspection.
2. `retry` places `@functools.wraps(max_attempts)` on the `decorator` function. `max_attempts` is an `int` — that's the wrong target entirely, and the inner `wrapper` gets no `@wraps` at all. Move `@functools.wraps(func)` to be on `wrapper`, inside `decorator(func)`.
3. `count_calls` keeps `_count` as a class attribute, so every decorated function shares the same counter.

</details>

<details>
<summary>Hint 3 (specific)</summary>

1. In `log_calls`:
    ```python
    def log_calls(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ...
    ```
2. In `retry`:
    ```python
    def retry(max_attempts: int):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                ...
    ```
3. In `count_calls`: move the counter to the instance:
    ```python
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self._func = func
        self._count = 0

    def __call__(self, *args, **kwargs):
        self._count += 1
        return self._func(*args, **kwargs)

    @property
    def count(self):
        return self._count
    ```

</details>

## Why each of these matters in production

- **Missing `@wraps`** — `@patch("module.greet")` fails to patch because the real name was replaced by `"wrapper"`. Stack traces say "wrapper" where they should say "greet". Sphinx-generated API docs lose their docstrings.
- **`@wraps` on the wrong target** — a silent no-op (int attributes are missing so update_wrapper skips them) *plus* no wrapping on the real wrapper. You get BOTH bugs at once: `__wrapped__` points to an int, and `__name__` is still `"wrapper"`.
- **Class-level state** — looks like a counter until a second decorator application shares it. One of those "why is my test affecting the test after it" bugs.

## Relevant reading

- `guides/11_context_and_decorators.py` — Sections 5–8 (decorator basics, `wraps`, parameterised decorators, class decorators)
