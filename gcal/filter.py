from abc import ABC

from gcal.entity import CalendarEvent


class CalendarEventFilter(ABC):
    def filter(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        raise NotImplementedError


class SummaryCalendarEventFilter(CalendarEventFilter, ABC):
    def filter_summary(self, filter_value, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        return tuple(filter(lambda calendar_event: calendar_event.summary != filter_value, calendar_events))


class VacationCalendarEventFilter(SummaryCalendarEventFilter):
    def filter(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        return self.filter_summary('Urlaub', calendar_events)


class BreakCalendarEventFilter(SummaryCalendarEventFilter):

    def filter(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        return self.filter_summary('Pause', calendar_events)
