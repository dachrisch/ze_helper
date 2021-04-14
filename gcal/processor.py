from gcal.entity import CalendarEvent
from gcal.filter import VacationCalendarEventFilter, BreakCalendarEventFilter
from gcal.splitter import MultipleEntriesOverlappingSplitter


class WholeMonthProcessor(object):
    def __init__(self, pre_filter=VacationCalendarEventFilter(), day_splitter=MultipleEntriesOverlappingSplitter(),
                 post_filter=BreakCalendarEventFilter()):
        self.pre_filter = pre_filter
        self.post_filter = post_filter
        self.day_splitter = day_splitter

    def process(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        pre_processed = self.pre_filter.filter(calendar_events)
        processed = self._per_day_process(pre_processed)
        post_processed = self.post_filter.filter(processed)
        return post_processed

    def _per_day_process(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        days = set(map(lambda entry: entry.start.day, calendar_events))
        processed_events = []
        for day in days:
            same_day_events = filter(lambda event: event.start.day == day, calendar_events)
            processed_events.extend(self.day_splitter.split(same_day_events))
        return tuple(processed_events)
