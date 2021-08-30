from abc import ABC
from typing import Tuple

from gcal.entity import CalendarEvent


class CalendarEventFilter(ABC):
    def filter(self, calendar_events: Tuple[CalendarEvent, ...]) -> Tuple[CalendarEvent, ...]:
        raise NotImplementedError


class CalendarEventFilterChain(CalendarEventFilter):
    def filter(self, calendar_events: Tuple[CalendarEvent, ...]) -> Tuple[CalendarEvent, ...]:
        filtered = calendar_events
        for filter in self.filters:
            filtered = filter.filter(filtered)

        return filtered

    def __init__(self, filters: Tuple[CalendarEventFilter, ...]):
        self.filters = filters


class SummaryCalendarEventFilter(CalendarEventFilter, ABC):
    def filter_summary(self, filter_value, calendar_events: Tuple[CalendarEvent, ...]) -> Tuple[CalendarEvent, ...]:
        return tuple(filter(lambda calendar_event: calendar_event.summary != filter_value, calendar_events))


class VacationCalendarEventFilter(SummaryCalendarEventFilter):
    def filter(self, calendar_events: Tuple[CalendarEvent, ...]) -> Tuple[CalendarEvent, ...]:
        return self.filter_summary('Urlaub', calendar_events)


class BreakCalendarEventFilter(SummaryCalendarEventFilter):

    def filter(self, calendar_events: Tuple[CalendarEvent, ...]) -> Tuple[CalendarEvent, ...]:
        return self.filter_summary('Pause', calendar_events)


class BusyCalendarEventFilter(CalendarEventFilter):
    def filter(self, calendar_events: Tuple[CalendarEvent, ...]) -> Tuple[CalendarEvent, ...]:
        return tuple(filter(lambda calendar_event: calendar_event.busy, calendar_events))
