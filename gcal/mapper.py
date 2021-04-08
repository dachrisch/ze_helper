from gcal.entity import DayEntry
from gcal.handler import HourlyDayEntryHandler, MultiDayEntryHandler, FailingDayEntryHandler


class GoogleCalendarMapper(object):
    def __init__(self):
        self.handlers = (HourlyDayEntryHandler(), MultiDayEntryHandler(), FailingDayEntryHandler())

    def to_day_entry(self, json_entry: dict) -> DayEntry:
        entry = None
        for handler in self.handlers:
            if handler.accept(json_entry):
                entry = handler.process(json_entry)
                break
        assert entry
        return entry

    def to_day_entries(self, json_entries: [dict]) -> [DayEntry]:
        return tuple(map(lambda entry: self.to_day_entry(entry), json_entries))
