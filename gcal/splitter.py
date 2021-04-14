from abc import ABC
from copy import deepcopy
from datetime import datetime

from gcal.entity import CalendarEvent


class OverlappingSplitter(ABC):
    def accept(self, calendar_events: [CalendarEvent]) -> bool:
        raise NotImplementedError

    def split(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        raise NotImplementedError


class MiddleEntryOverlappingSplitter(OverlappingSplitter):
    def accept(self, calendar_events: [CalendarEvent]) -> bool:
        if len(calendar_events) != 2:
            return False
        else:
            (outside, inside) = calendar_events
            return outside.start < inside.start and inside.end < outside.end

    def split(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        (outside_1, middle) = deepcopy(calendar_events)

        outside_2 = outside_1.replace(start=middle.end)
        outside_1.end = middle.start
        return outside_1, middle, outside_2


class EndEntryOverlappingSplitter(OverlappingSplitter):
    def accept(self, calendar_events: [CalendarEvent]) -> bool:
        if len(calendar_events) != 2:
            return False
        else:
            (first, last) = calendar_events
            return first.start < last.start < first.end and last.start < first.end < last.end

    def split(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        (first, last) = deepcopy(calendar_events)
        first.end = last.start
        return first, last


class SameStartOverlappingSplitter(OverlappingSplitter):
    def accept(self, calendar_events: [CalendarEvent]) -> bool:
        if len(calendar_events) != 2:
            return False
        else:
            (first, last) = calendar_events
            return first.start == last.start and first.end != last.end

    def split(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        (first, last) = deepcopy(calendar_events)
        if first.end > last.end:
            new_first = last
            new_last = first
        else:
            new_first = first
            new_last = last

        new_last.start = new_first.end
        return new_first, new_last


class MultipleEntriesOverlappingSplitter(OverlappingSplitter):

    def __init__(self):
        self.splitters = (
            MiddleEntryOverlappingSplitter(), EndEntryOverlappingSplitter(), SameStartOverlappingSplitter())

    def split(self, calendar_events: [CalendarEvent]) -> [CalendarEvent]:
        entries_stack = list(deepcopy(calendar_events))
        entries_stack.reverse()
        all_split_calendar_events = []
        one = entries_stack.pop()
        while len(entries_stack) > 0:
            two = entries_stack.pop()
            if any(map(lambda splitter: splitter.accept((one, two)), self.splitters)):
                split_calendar_events = filter(lambda splitter: splitter.accept((one, two)),
                                               self.splitters).__next__().split(
                    (one, two))
                all_split_calendar_events.extend(split_calendar_events[:-1])
                one = split_calendar_events[-1]
            else:
                all_split_calendar_events.append(one)
                one = two

        all_split_calendar_events.append(one)
        return tuple(all_split_calendar_events)

    def accept(self, calendar_events: [CalendarEvent]) -> bool:
        return len(calendar_events) > 1 and self.are_same_day(calendar_events[0].start, calendar_events)

    @staticmethod
    def are_same_day(check_date: datetime, calendar_events: [CalendarEvent]) -> bool:
        return all(check_date.date() == entry.start.date() for entry in calendar_events)
