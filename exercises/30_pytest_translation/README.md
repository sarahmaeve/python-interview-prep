# Exercise 30: Pytest Translation

Translate an existing `unittest` test suite into idiomatic `pytest`. The production code in `temperature_monitor.py` has no bugs — the goal is muscle memory for the unittest → pytest idioms you'll see in most 2025 Python codebases.

## How to run

```bash
# Run the reference unittest suite (verifies temperature_monitor works)
python3 -m unittest test_temperature_monitor_unittest

# Run your pytest translation
python3 -m pytest test_temperature_monitor.py -v
```

Pytest must be installed. If you set up the repo via `pip install --group dev` (or the Makefile's `make test-pytest` target), it already is.

Your goal: fill in the TODOs in `test_temperature_monitor.py` until `pytest -v` reports 14 passing tests — all with real assertions, not vacuous `...` bodies.

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

## Hints

<details>
<summary>Hint 1 (general)</summary>

Start with the fixture. Once `monitor` returns a real `TemperatureMonitor`, five of the tests immediately work once you replace `...` with an `assert`.

The parametrize decorator takes a comma-separated argument string and a list of tuples:

```python
@pytest.mark.parametrize("celsius,expected", [
    (-5.0, True),
    (0.0, False),
    # ...
])
def test_classification(monitor, celsius, expected):
    reading = Reading(celsius=celsius)
    assert monitor.is_out_of_range(reading) == expected
```

</details>

<details>
<summary>Hint 2 (solution sketch)</summary>

The fixture:

```python
@pytest.fixture
def monitor() -> TemperatureMonitor:
    return TemperatureMonitor(low_threshold=0, high_threshold=30)
```

Simple assertion replacements:

```python
def test_empty_monitor_has_no_latest(monitor):
    assert monitor.latest() is None
```

See the solution walkthrough for the full translation.

</details>

## Relevant reading

- `guides/03_unittest_fundamentals.py` — Section 9 (pytest translation cheat sheet)
