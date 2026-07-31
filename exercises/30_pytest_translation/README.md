# Exercise 30: Pytest Translation

Translate an existing `unittest` test suite into idiomatic `pytest`. The production code in `temperature_monitor.py` has no bugs — the goal is muscle memory for the unittest → pytest idioms used in modern Python codebases.

## How to run

```bash
# Run the reference unittest suite (verifies temperature_monitor works)
python3 -m unittest test_temperature_monitor_unittest

# Run your pytest translation
python3 -m pytest test_temperature_monitor.py -v
```

Pytest must be installed. If you set up the repo via `pip install --group dev` (or the Makefile's `make test-pytest` target), it already is.

Your goal: fill in the TODOs in `test_temperature_monitor.py` until `pytest -v`
reports 15 passing tests — the provided example plus 14 translated cases, with
every `pytest.fail(...)` stub replaced.

## What changes

| unittest | pytest |
|---|---|
| `class TestX(TestCase):` → methods | plain `def test_*():` functions |
| `self.assertEqual(a, b)` | `assert a == b` |
| `self.assertIsNone(x)` | `assert x is None` |
| `self.assertIsInstance(x, T)` | `assert isinstance(x, T)` |
| `self.assertRaises(E)` | `with pytest.raises(E):` |
| `self.assertRaisesRegex(E, "msg")` | `with pytest.raises(E, match="msg"):` |
| `setUp` | `@pytest.fixture` that yields/returns |
| `for ... with self.subTest(x=...)` | `@pytest.mark.parametrize("x", [...])` |
| `tmpfile = tempfile.mkstemp(...)` | `tmp_path` fixture |
| `@patch("mod.fn")` | `monkeypatch` fixture or `mocker` from pytest-mock |

## Why bother learning both?

- You'll meet both in real codebases — older codebases trend unittest, newer ones trend pytest. Interview panels frequently ask candidates to refactor between them.
- The concepts are identical. Only the syntax differs. Once you have the translation in muscle memory, switching between codebases is nearly free.
- Pytest's `parametrize` is meaningfully better than unittest's `subTest` for most real-world test tables: it produces one test case per row in the output, which means your test report shows exactly which row failed, with the actual inputs in the test ID.

## Principle Primer

Translate the testing intent, not only the syntax. Fixtures express reusable
arrangement, parametrization turns data rows into separately reported cases,
and pytest's plain assertions retain useful failure introspection. Keep each
translated test's behavioral scope aligned with the reference suite.

If you get stuck, use [HINTS.md](HINTS.md).

## Relevant reading

- `guides/03_unittest_fundamentals.py` — Section 9 (pytest translation cheat sheet)
