"""Tests for the config schema validator.

All tests are stubs (they pass trivially when the functions return None/pass).
Implement validate() in validator.py so that every test exercises real
behaviour and passes.

Do NOT change the test assertions -- only add code to validator.py.
"""

from __future__ import annotations

import unittest
from validator import FieldSchema, ValidationResult, ValidationError, validate


class TestValidateRequired(unittest.TestCase):

    def test_valid_config_passes(self):
        """A config that matches the schema should return is_valid=True."""
        # TODO: Define a schema with required string and int fields.
        # Pass a valid config. Assert is_valid is True and errors is empty.
        self.fail("not implemented")

    def test_missing_required_field(self):
        """A missing required field should produce a ValidationError."""
        # TODO: Define a schema requiring "host". Pass config without "host".
        # Assert is_valid is False and at least one error references "host".
        self.fail("not implemented")

    def test_collects_all_errors(self):
        """All errors should be reported, not just the first one."""
        # TODO: Define a schema requiring 3 fields. Pass empty config.
        # Assert len(result.errors) == 3.
        self.fail("not implemented")


class TestValidateTypes(unittest.TestCase):

    def test_wrong_type_is_invalid(self):
        """Passing a string where int is expected should produce an error."""
        # TODO: Schema requires "port" as int.
        # Pass config with port="not_a_number".
        # Assert is_valid is False and errors mention "port".
        self.fail("not implemented")

    def test_correct_type_passes(self):
        """Passing the correct type should not produce an error for that field."""
        # TODO: Schema requires "port" as int. Pass port=8080.
        # Assert is_valid is True.
        self.fail("not implemented")


class TestValidateDefaults(unittest.TestCase):

    def test_default_applied_for_missing_optional(self):
        """An optional field with a default should be filled in on the result."""
        # TODO: Schema has optional "port" (required=False, default=5432).
        # Config has no "port" key. Assert result.config["port"] == 5432.
        self.fail("not implemented")

    def test_provided_value_overrides_default(self):
        """If the field is present in config, the given value is used, not the default."""
        # TODO: Same schema as above but config has port=9999.
        # Assert result.config["port"] == 9999.
        self.fail("not implemented")


class TestCustomValidator(unittest.TestCase):

    def test_custom_validator_passes(self):
        """A value that satisfies the custom validator should be accepted."""
        # TODO: Schema has "port" (int) with validator=lambda p: 1 <= p <= 65535.
        # Pass port=8080. Assert is_valid is True.
        self.fail("not implemented")

    def test_custom_validator_fails(self):
        """A value that fails the custom validator should produce an error."""
        # TODO: Same schema. Pass port=99999 (out of range).
        # Assert is_valid is False and errors mention "port".
        self.fail("not implemented")



class TestOptionalMissingNoTypeError(unittest.TestCase):
    def test_absent_optional_does_not_produce_type_error(self):
        """An optional field that is missing should not trigger a type check."""
        # TODO: Schema has optional "debug" (bool, default=False).
        # Config has no "debug" key. Assert is_valid is True.
        self.fail("not implemented")


if __name__ == "__main__":
    unittest.main()
