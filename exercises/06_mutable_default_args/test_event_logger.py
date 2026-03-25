import unittest
from event_logger import Event, EventLogger


class TestEventCreation(unittest.TestCase):

    def test_event_stores_name(self):
        event = Event("deploy")
        self.assertEqual(event.name, "deploy")

    def test_event_default_tags_is_empty_list(self):
        event = Event("deploy")
        self.assertEqual(event.tags, [])

    def test_event_custom_tags(self):
        event = Event("deploy", tags=["prod", "urgent"])
        self.assertEqual(event.tags, ["prod", "urgent"])

    def test_default_tags_are_independent_between_events(self):
        """Two events created without explicit tags must NOT share the same
        list object. Mutating one must not affect the other."""
        event1 = Event("first")
        event2 = Event("second")
        event1.tags.append("added-later")
        self.assertEqual(event2.tags, [])


class TestEventLogger(unittest.TestCase):

    def test_log_and_retrieve_event(self):
        logger = EventLogger()
        event = Event("deploy", tags=["prod"])
        logger.log_event(event)
        result = logger.get_events_by_tag("prod")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "deploy")

    def test_get_events_by_tag_returns_only_matching(self):
        logger = EventLogger()
        logger.log_event(Event("deploy", tags=["prod"]))
        logger.log_event(Event("test", tags=["staging"]))
        result = logger.get_events_by_tag("prod")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "deploy")

    def test_get_events_by_tag_returns_copy_not_internal_list(self):
        """Callers must not be able to mutate the logger's internal state
        by modifying the returned list."""
        logger = EventLogger()
        logger.log_event(Event("deploy", tags=["prod"]))
        result = logger.get_events_by_tag("prod")
        result.clear()
        self.assertEqual(len(logger.get_events_by_tag("prod")), 1)

    def test_get_events_by_tag_empty(self):
        logger = EventLogger()
        self.assertEqual(logger.get_events_by_tag("nonexistent"), [])


class TestGetSummary(unittest.TestCase):

    def test_summary_counts_tags(self):
        logger = EventLogger()
        logger.log_event(Event("deploy", tags=["prod", "urgent"]))
        logger.log_event(Event("rollback", tags=["prod"]))
        summary = logger.get_summary()
        self.assertEqual(summary["prod"], 2)
        self.assertEqual(summary["urgent"], 1)

    def test_summary_empty_logger(self):
        logger = EventLogger()
        self.assertEqual(logger.get_summary(), {})

    def test_summary_does_not_mutate_event_tag_order(self):
        """get_summary must not change the order of tags on existing events."""
        event = Event("deploy", tags=["zebra", "alpha", "middle"])
        logger = EventLogger()
        logger.log_event(event)
        logger.get_summary()
        self.assertEqual(event.tags, ["zebra", "alpha", "middle"])

    def test_summary_with_multiple_tags_per_event(self):
        logger = EventLogger()
        logger.log_event(Event("e1", tags=["a", "b"]))
        logger.log_event(Event("e2", tags=["b", "c"]))
        logger.log_event(Event("e3", tags=["a", "c"]))
        summary = logger.get_summary()
        self.assertEqual(summary["a"], 2)
        self.assertEqual(summary["b"], 2)
        self.assertEqual(summary["c"], 2)


if __name__ == "__main__":
    unittest.main()
