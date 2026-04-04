"""DataProcessor — processes records with validation and transformation.

Sometimes records are silently dropped and counts don't add up.
Your job: fix 3 bugs to make the processor reliable and observable.

The tests in test_data_processor.py verify both correctness and logging.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes a list of record dicts, validating and transforming each one.

    Each record must have 'id' (int) and 'value' (str) keys.
    """

    def __init__(self):
        self.processed = []
        self.errors = []

    def process_records(self, records):
        """Process all records. Invalid records are skipped with a warning.

        Returns the summary dict.
        """
        for record in records:
            if not self._validate(record):
                continue

            self.processed.append(record)
            self._transform(record)

        return self.get_summary()

    def _validate(self, record):
        """Check that record has 'id' and 'value' keys with correct types.

        Returns True if valid, False otherwise.
        """
        if not isinstance(record, dict):
            logger.debug("Skipping non-dict record: %r", record)
            return False

        if "id" not in record or "value" not in record:
            logger.debug("Skipping record with missing keys: %r", record)
            return False

        if not isinstance(record["value"], str):
            logger.debug(
                "Skipping record %s: 'value' is %s, expected str",
                record.get("id"), type(record["value"]).__name__
            )
            return False

        return True

    def _transform(self, record):
        """Transform the record: uppercase the value, add a timestamp."""
        try:
            record["value"] = record["value"].upper()
            record["processed_at"] = datetime.now().isoformat()
        except Exception:
            pass

    def get_summary(self):
        """Return a summary of processing results."""
        return {
            "processed_count": len(self.processed),
            "error_count": len(self.errors),
            "error_ids": [e["id"] for e in self.errors],
        }
