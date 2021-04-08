from abc import ABC
from copy import deepcopy
from datetime import datetime

from gcal.entity import DayEntry


class OverlappingSplitter(ABC):
    def accept(self, day_entries: [DayEntry]) -> bool:
        raise NotImplementedError

    def split(self, day_entries: [DayEntry]) -> [DayEntry]:
        raise NotImplementedError


class MiddleEntryOverlappingSplitter(OverlappingSplitter):
    def accept(self, day_entries: [DayEntry]) -> bool:
        if len(day_entries) != 2:
            return False
        else:
            (outside, inside) = day_entries
            return outside.start < inside.start and inside.end < outside.end

    def split(self, day_entries: [DayEntry]) -> [DayEntry]:
        (outside_1, middle) = deepcopy(day_entries)

        outside_2 = DayEntry(middle.end, outside_1.end, outside_1.summary, outside_1.description, outside_1.color_id)
        outside_1.end = middle.start
        return outside_1, middle, outside_2


class EndEntryOverlappingSplitter(OverlappingSplitter):
    def accept(self, day_entries: [DayEntry]) -> bool:
        if len(day_entries) != 2:
            return False
        else:
            (first, last) = day_entries
            return first.start < last.start < first.end and last.start < first.end < last.end

    def split(self, day_entries: [DayEntry]) -> [DayEntry]:
        (first, last) = deepcopy(day_entries)
        first.end = last.start
        return first, last


class SameStartOverlappingSplitter(OverlappingSplitter):
    def accept(self, day_entries: [DayEntry]) -> bool:
        if len(day_entries) != 2:
            return False
        else:
            (first, last) = day_entries
            return first.start == last.start and first.end != last.end

    def split(self, day_entries: [DayEntry]) -> [DayEntry]:
        (first, last) = deepcopy(day_entries)
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

    def split(self, day_entries: [DayEntry]) -> [DayEntry]:
        entries_stack = list(deepcopy(day_entries))
        entries_stack.reverse()
        all_split_day_entries = []
        one = entries_stack.pop()
        while len(entries_stack) > 0:
            two = entries_stack.pop()
            if any(map(lambda splitter: splitter.accept((one, two)), self.splitters)):
                split_day_entries = filter(lambda splitter: splitter.accept((one, two)),
                                           self.splitters).__next__().split(
                    (one, two))
                all_split_day_entries.extend(split_day_entries[:-1])
                one = split_day_entries[-1]
            else:
                all_split_day_entries.append(one)
                one = two

        all_split_day_entries.append(one)
        return tuple(all_split_day_entries)

    def accept(self, day_entries: [DayEntry]) -> bool:
        return len(day_entries) > 1 and self.are_same_day(day_entries[0].start, day_entries)

    @staticmethod
    def are_same_day(check_date: datetime, day_entries: [DayEntry]) -> bool:
        return all(check_date.date() == entry.start.date() for entry in day_entries)
