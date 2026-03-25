import unittest
from config_parser import ConfigParser


class TestConfigParserInit(unittest.TestCase):
    def test_init_no_defaults(self):
        cp = ConfigParser()
        self.assertEqual(cp.get_config(), {})

    def test_init_with_defaults(self):
        cp = ConfigParser(defaults={"debug": False, "timeout": 30})
        self.assertEqual(cp.get_config(), {})


class TestLoadConfig(unittest.TestCase):
    def test_load_basic(self):
        cp = ConfigParser(defaults={"debug": False})
        cp.load_config({"host": "localhost", "port": 8080})
        self.assertEqual(cp.get("host"), "localhost")
        self.assertEqual(cp.get("port"), 8080)

    def test_load_applies_defaults_for_missing_keys(self):
        cp = ConfigParser(defaults={"debug": False, "timeout": 30})
        cp.load_config({"host": "localhost"})
        self.assertEqual(cp.get("debug"), False)
        self.assertEqual(cp.get("timeout"), 30)
        self.assertEqual(cp.get("host"), "localhost")

    def test_load_config_does_not_swallow_keyboard_interrupt(self):
        """KeyboardInterrupt must propagate — bare except must not catch it."""
        cp = ConfigParser()
        bad_dict = BadDict()
        with self.assertRaises(KeyboardInterrupt):
            cp.load_config(bad_dict)


class TestGet(unittest.TestCase):
    def test_get_existing_key(self):
        cp = ConfigParser()
        cp.load_config({"color": "blue"})
        self.assertEqual(cp.get("color"), "blue")

    def test_get_missing_key_raises_key_error(self):
        cp = ConfigParser()
        cp.load_config({"a": 1})
        with self.assertRaises(KeyError):
            cp.get("missing")


class TestGetInt(unittest.TestCase):
    def test_get_int_valid(self):
        cp = ConfigParser()
        cp.load_config({"port": "8080"})
        self.assertEqual(cp.get_int("port"), 8080)

    def test_get_int_invalid_raises_value_error_with_details(self):
        """ValueError message must mention both the key and the bad value."""
        cp = ConfigParser()
        cp.load_config({"port": "not_a_number"})
        with self.assertRaisesRegex(ValueError, r"port"):
            cp.get_int("port")
        # Run again to also check the bad value appears in the message
        with self.assertRaisesRegex(ValueError, r"not_a_number"):
            cp.get_int("port")


class TestValidate(unittest.TestCase):
    def test_validate_passes_when_all_present(self):
        cp = ConfigParser()
        cp.load_config({"host": "localhost", "port": 8080})
        cp.validate(["host", "port"])  # should not raise

    def test_validate_raises_on_missing_keys(self):
        cp = ConfigParser()
        cp.load_config({"host": "localhost"})
        with self.assertRaisesRegex(ValueError, r"port"):
            cp.validate(["host", "port", "debug"])

    def test_validate_raises_type_error_for_none(self):
        """TypeError must propagate when None is passed instead of a list."""
        cp = ConfigParser()
        cp.load_config({"host": "localhost"})
        with self.assertRaises(TypeError):
            cp.validate(None)


# ---------------------------------------------------------------------------
# Helper used by test_load_config_does_not_swallow_keyboard_interrupt
# ---------------------------------------------------------------------------
class BadDict(dict):
    """A dict-like object whose items() raises KeyboardInterrupt."""

    def items(self):
        raise KeyboardInterrupt("simulated ctrl-c")


if __name__ == "__main__":
    unittest.main()
