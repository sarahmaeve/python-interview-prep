# Solution 17 --- Fixing Property and Composition Bugs in `temp_monitor.py`

## Bug 1: `average` Is a Plain Method, Not a `@property` (line 40)

**Location:** `TemperatureSensor.average`

**What's wrong:** `average` is defined as a regular method. Tests access it as `sensor.average` (no parentheses), so without `@property` the expression returns a bound method object, not a `float`.

**Error you'd see:** `assertIsInstance(result, float)` fails because `result` is `<bound method ...>`.

**Fix:**

```python
# Before
def average(self) -> float | None:

# After
@property
def average(self) -> float | None:
```

**Why this bug matters:** `@property` lets a class expose computed values with attribute-access syntax. Callers get a clean interface (`sensor.average`) while the implementation can run arbitrary logic. Forgetting the decorator silently returns the method object instead of calling it -- a common Python gotcha.

---

## Bug 2: `set_unit` Is a Standalone Method, Not a `@unit.setter` (line 52)

**Location:** `TemperatureSensor.set_unit`

**What's wrong:** The unit-conversion logic lives in a plain method called `set_unit`. Tests assign with `sensor.unit = "F"`, which requires a `@unit.setter`. Without it, Python raises `AttributeError: property 'unit' has no setter`.

**Error you'd see:** `AttributeError: property 'unit' has no setter`.

**Fix:**

```python
# Before
def set_unit(self, value: str) -> None:

# After
@unit.setter
def unit(self, value: str) -> None:
```

**Why this bug matters:** `@property` getter/setter pairs give you validation and side-effects (here, converting every stored reading) behind simple assignment syntax. The setter must be declared with `@<name>.setter` and share the same method name as the getter. Using a separate method name breaks the property protocol entirely.

---

## Bug 3: `add_sensor` Stores the Label String Instead of the Sensor Object (line 78)

**Location:** `MonitoringStation.add_sensor`

**What's wrong:** The dict value is `sensor.label` (a `str`) instead of `sensor` (the object). Every later method that iterates `self._sensors.values()` gets strings, not `TemperatureSensor` instances.

**Error you'd see:** `assertIsInstance(retrieved, TemperatureSensor)` fails -- `retrieved` is the string `"roof"`. Downstream, `str` objects have no `.average` or `.latest`, so `AttributeError` cascades through `all_averages`, `station_average`, and `high_alert`.

**Fix:**

```python
# Before
self._sensors[sensor.label] = sensor.label

# After
self._sensors[sensor.label] = sensor
```

**Why this bug matters:** Composition means storing *references to objects*, not copies of their data. A monitoring station HAS sensors -- it delegates work to them. Storing a label instead of the object severs that delegation chain and defeats the entire purpose of composition.

---

## Bug 4: `station_average` Does Not Filter Out `None` Averages (lines 95-98)

**Location:** `MonitoringStation.station_average`

**What's wrong:** The list comprehension collects every sensor's average, including `None` for sensors with no readings. `sum([20, 40, None])` raises `TypeError`, and even if it didn't, dividing by 3 instead of 2 gives the wrong answer.

**Error you'd see:** `TypeError: unsupported operand type(s) for +: 'float' and 'NoneType'`.

**Fix:**

```python
# Before
averages = [sensor.average for sensor in self._sensors.values()]
if not averages:
    return None
return sum(averages) / len(averages)

# After
averages = [sensor.average for sensor in self._sensors.values()
            if sensor.average is not None]
if not averages:
    return None
return sum(averages) / len(averages)
```

**Why this bug matters:** Properties that return `None` as a sentinel require callers to handle that case. When you aggregate optional values, you must decide whether `None` means "skip" or "zero." Here the spec says skip, so filtering is mandatory.

---

## Cascading Fix Note

Bug 4 is **masked** by Bug 3. While Bug 3 is present, `self._sensors.values()` yields strings, so the code crashes with `AttributeError: 'str' object has no attribute 'average'` before it ever reaches the `None`-filtering problem. Only after fixing Bug 3 (so real sensor objects are stored) does Bug 4 surface as a `TypeError` on `sum()`.

---

## Discussion

### When to use `@property` vs plain attributes

Use `@property` when you need **validation** (rejecting bad values in a setter), **computed values** (like `average` derived from `_readings`), or **side-effects** (converting readings on unit change). Stick with plain attributes for simple data that needs no guarding -- over-using properties adds complexity for no benefit.

### When composition beats inheritance

`MonitoringStation` is not a kind of sensor -- it *manages* sensors. Inheritance would force it into the sensor interface and create tight coupling. Composition keeps each class focused: sensors handle readings, the station handles aggregation. This follows the principle "favor composition over inheritance" because it is easier to add new sensor types, swap implementations, or change the station's aggregation logic without modifying the other class.
