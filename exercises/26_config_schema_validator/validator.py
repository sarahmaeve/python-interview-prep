from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldSchema:
    """Defines the expected type and constraints for a single config field.

    Attributes:
        name: The config key name.
        expected_type: The Python type (e.g., str, int, list).
        required: Whether this field must be present (default: True).
        default: Default value if the field is missing (only used when required=False).
        validator: Optional callable that takes the value and returns True/False.
                   If provided and returns False, the field is invalid.
    """
    name: str
    expected_type: type
    required: bool = True
    default: Any = None
    validator: Any = None  # Optional[Callable[[Any], bool]]


@dataclass
class ValidationError:
    """A single validation failure.

    Attributes:
        field: The config key that failed validation.
        message: A human-readable description of what went wrong.
    """
    field: str
    message: str


@dataclass
class ValidationResult:
    """The result of validating a config dict against a schema.

    Attributes:
        is_valid: True if all validations passed.
        errors: List of ValidationError instances (empty if valid).
        config: The validated config dict with defaults applied;
                config is an empty dict if is_valid is False (to prevent use
                of unvalidated data).
    """
    is_valid: bool
    errors: list = field(default_factory=list)
    config: dict = field(default_factory=dict)


def validate(config: dict, schema: list[FieldSchema]) -> ValidationResult:
    """Validate *config* against *schema*.

    Checks:
    1. Required fields are present.
    2. Values match expected_type (use isinstance).
    3. Custom validators pass (if provided).
    4. Apply defaults for missing optional fields.

    Collects ALL errors — does not stop at the first.

    Args:
        config: The configuration dict to validate.
        schema: A list of FieldSchema defining expected fields.

    Returns:
        A ValidationResult with is_valid, errors, and the validated config.
    """
    pass
