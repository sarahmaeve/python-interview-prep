"""Tests for the event router.

Do NOT modify this file.  Fix the bugs in event_router.py until every
test passes.
"""

import unittest

from event_router import handle_event, route_all


class TestClick(unittest.TestCase):
    def test_click_coordinates(self):
        result = handle_event({"type": "click", "x": 3, "y": 5})
        self.assertEqual(result, "click at (3, 5)")


class TestScroll(unittest.TestCase):
    def test_scroll_down(self):
        self.assertEqual(handle_event({"type": "scroll", "delta": 10}),
                         "scroll down by 10")

    def test_scroll_up(self):
        self.assertEqual(handle_event({"type": "scroll", "delta": -5}),
                         "scroll up by 5")


class TestKeypress(unittest.TestCase):
    def test_plain_key(self):
        result = handle_event({"type": "keypress", "key": "a",
                               "modifiers": []})
        self.assertEqual(result, "key: a")

    def test_modifiers_are_honored(self):
        """Modifiers from the event must reach the handler — bug: the
        current dispatch drops the list and calls the handler with []."""
        result = handle_event({"type": "keypress", "key": "s",
                               "modifiers": ["ctrl", "shift"]})
        self.assertEqual(result, "key: ctrl+shift+s")


class TestResize(unittest.TestCase):
    def test_resize_carries_dimensions(self):
        """The resize handler needs width and height — bug: the current
        dispatch discards them and returns a bare 'resized'."""
        result = handle_event({"type": "resize", "width": 1024, "height": 768})
        self.assertEqual(result, "resized to 1024x768")


class TestUnknownEvent(unittest.TestCase):
    """Unknown events must produce a clear error, not silently return None."""

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            handle_event({"type": "teleport", "x": 1})

    def test_missing_type_raises(self):
        with self.assertRaises(ValueError):
            handle_event({"no_type": "here"})

    def test_handler_never_returns_none(self):
        """Even borderline cases must produce a real string or raise —
        never None.  None values propagate into downstream pipelines
        and cause mysterious failures elsewhere."""
        for ev in [{"type": "click", "x": 0, "y": 0},
                   {"type": "scroll", "delta": 0},
                   {"type": "keypress", "key": "a", "modifiers": []},
                   {"type": "resize", "width": 1, "height": 1}]:
            with self.subTest(event=ev):
                self.assertIsNotNone(handle_event(ev))


class TestRouteAll(unittest.TestCase):
    def test_routes_valid_events(self):
        results = route_all([
            {"type": "click", "x": 1, "y": 2},
            {"type": "scroll", "delta": 3},
        ])
        self.assertEqual(results, ["click at (1, 2)", "scroll down by 3"])

    def test_drops_unknown_without_none(self):
        """route_all catches errors from unknown events — the result
        list must contain real strings, never None."""
        results = route_all([
            {"type": "click", "x": 1, "y": 2},
            {"type": "mystery"},
            {"type": "scroll", "delta": 3},
        ])
        self.assertEqual(results, ["click at (1, 2)", "scroll down by 3"])
        self.assertNotIn(None, results)


if __name__ == "__main__":
    unittest.main()
