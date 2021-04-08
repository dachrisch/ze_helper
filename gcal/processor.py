from gcal.entity import DayEntry
from gcal.filter import VacationDayEntryFilter, BreakDayEntryFilter
from gcal.splitter import MultipleEntriesOverlappingSplitter


class WholeMonthProcessor(object):
    def __init__(self, pre_filter=VacationDayEntryFilter(), day_splitter=MultipleEntriesOverlappingSplitter(),
                 post_filter=BreakDayEntryFilter()):
        self.pre_filter = pre_filter
        self.post_filter = post_filter
        self.day_splitter = day_splitter

    def process(self, day_entries: [DayEntry]) -> [DayEntry]:
        pre_processed = self.pre_filter.filter(day_entries)
        processed = self._per_day_process(pre_processed)
        post_processed = self.post_filter.filter(processed)
        return post_processed

    def _per_day_process(self, day_entries: [DayEntry]) -> [DayEntry]:
        days = set(map(lambda entry: entry.start.day, day_entries))
        processed_events = []
        for day in days:
            same_day_events = filter(lambda event: event.start.day == day, day_entries)
            processed_events.extend(self.day_splitter.split(same_day_events))
        return tuple(processed_events)
