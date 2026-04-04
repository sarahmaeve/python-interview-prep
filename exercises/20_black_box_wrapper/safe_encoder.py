"""SafeEncoder — a well-behaved wrapper around QuirkyEncoder.

This wrapper normalizes QuirkyEncoder's quirky behavior into a
predictable, documented interface.

There are 3 bugs in this file. The tests in test_safe_encoder.py
describe the correct behavior.
"""

from quirky_encoder import QuirkyEncoder


class SafeEncoder:
    """A safe, predictable encoder that wraps QuirkyEncoder.

    Guarantees:
    - encode() returns a clean string with no trailing separator
    - encode() raises TypeError if any field is None
    - decode() preserves the original case of fields
    - batch_encode() calls are independent (no cross-call contamination)
    - round_trip() returns the original fields unchanged
    """

    def __init__(self, separator="|"):
        self._encoder = QuirkyEncoder(separator=separator)
        self._separator = separator

    def encode(self, fields):
        """Encode a list of string fields into a delimited string.

        Raises TypeError if any field is None.
        Non-string fields (int, float) are converted to strings.
        The result does NOT have a trailing separator.
        """
        for field in fields:
            if field is not None:
                raise TypeError(
                    f"None is not allowed in fields, got: {fields!r}"
                )

        result = self._encoder.encode(fields)
        return result

    def decode(self, encoded_string):
        """Decode a delimited string back into a list of fields.

        Preserves the original case of each field.
        """
        # The black box's decode lowercases everything, so we split manually
        # to preserve case.
        return encoded_string.split(self._separator)

    def batch_encode(self, records):
        """Encode multiple records. Each call is independent.

        Returns a list of encoded strings.
        """
        return self._encoder.batch_encode(records)

    def round_trip(self, fields):
        """Encode then decode, returning the original fields.

        This verifies that encode/decode are inverse operations.
        """
        encoded = self.encode(fields)
        return self.decode(encoded)
