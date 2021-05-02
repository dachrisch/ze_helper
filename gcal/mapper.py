from typing import Dict

from gcal.entity import CalendarEvent
from gcal.handler import HourlyCalendarEventHandler, MultiCalendarEventHandler, FailingCalendarEventHandler


class CalendarEventMapper(object):
    def __init__(self):
        self.handlers = (HourlyCalendarEventHandler(), MultiCalendarEventHandler(), FailingCalendarEventHandler())

    def to_calendar_event(self, json_entry: Dict) -> CalendarEvent:
        entry = None
        for handler in self.handlers:
            if handler.accept(json_entry):
                entry = handler.process(json_entry)
                break
        assert entry
        return entry

    def to_calendar_events(self, json_entries: [Dict]) -> [CalendarEvent]:
        return tuple(map(lambda entry: self.to_calendar_event(entry), json_entries))
