from datetime import datetime


class Event:
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
        return self._tag_index.get(tag, [])

    def get_summary(self):
        summary = {}
        for event in self._events:
            event.tags.sort()
            for tag in event.tags:
                summary[tag] = summary.get(tag, 0) + 1
        return summary
