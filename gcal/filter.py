from abc import ABC

from gcal.entity import DayEntry


class DayEntryFilter(ABC):
    def filter(self, day_entries: [DayEntry]) -> [DayEntry]:
        raise NotImplementedError


class SummaryDayEntryFilter(DayEntryFilter, ABC):
    def filter_summary(self, filter_value, day_entries: [DayEntry]) -> [DayEntry]:
        return tuple(filter(lambda day_entry: day_entry.summary != filter_value, day_entries))


class VacationDayEntryFilter(SummaryDayEntryFilter):
    def filter(self, day_entries: [DayEntry]) -> [DayEntry]:
        return self.filter_summary('Urlaub', day_entries)


class BreakDayEntryFilter(SummaryDayEntryFilter):

    def filter(self, day_entries: [DayEntry]) -> [DayEntry]:
        return self.filter_summary('Pause', day_entries)
