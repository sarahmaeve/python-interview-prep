from datetime import datetime


class Event:
    # BUG: mutable default argument — all events without explicit tags share this list
    def __init__(self, name, timestamp=None, tags=[]):
        self.name = name
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.tags = tags


class EventLogger:
    def __init__(self):
        self._events = []
        self._tag_index = {}  # tag -> list of events

    def log_event(self, event):
        self._events.append(event)
        for tag in event.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(event)

    def get_events_by_tag(self, tag):
        # BUG: returns the internal list directly, not a copy
        # Callers can mutate the logger's state via the returned reference
        return self._tag_index.get(tag, [])

    def get_summary(self):
        summary = {}
        for event in self._events:
            # BUG: sorts tags in place, mutating the original event's tag order
            event.tags.sort()
            for tag in event.tags:
                summary[tag] = summary.get(tag, 0) + 1
        return summary
