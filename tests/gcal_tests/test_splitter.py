import unittest
from datetime import datetime

from gcal.entity import DayEntry
from gcal.splitter import MiddleEntryOverlappingSplitter, EndEntryOverlappingSplitter, \
    MultipleEntriesOverlappingSplitter, SameStartOverlappingSplitter


class TestSplitDayEntries(unittest.TestCase):

    def test_split_overlapping_middle(self):
        source_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'Big Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Small Arbeit'))
        expected_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'Big Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Small Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 16), 'Big Arbeit'))

        self.assertTrue(MiddleEntryOverlappingSplitter().accept(source_day_entries))
        self.assertEqual(expected_day_entries, MiddleEntryOverlappingSplitter().split(source_day_entries))

    def test_split_overlapping_end(self):
        source_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'))
        expected_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 15), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'))

        self.assertTrue(EndEntryOverlappingSplitter().accept(source_day_entries))
        self.assertEqual(expected_day_entries, EndEntryOverlappingSplitter().split(source_day_entries))

    def test_split_overlapping_middle_and_end(self):
        source_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'))
        expected_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 15), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'))
        self.assertTrue(MultipleEntriesOverlappingSplitter().accept(source_day_entries))
        self.assertEqual(expected_day_entries, MultipleEntriesOverlappingSplitter().split(source_day_entries))

    def test_not_overlapping_returns_list(self):
        source_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 12), 'First Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 14), 'Second Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 14), datetime(2021, 2, 1, 16), 'Third Arbeit'))

        self.assertTrue(MultipleEntriesOverlappingSplitter().accept(source_day_entries))
        self.assertEqual(source_day_entries, MultipleEntriesOverlappingSplitter().split(source_day_entries))

    def test_split_same_start_overlapping(self):
        source_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 12), 'Second Arbeit'))
        expected_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 16), 'First Arbeit'))
        self.assertTrue(SameStartOverlappingSplitter().accept(source_day_entries))
        self.assertEqual(expected_day_entries, SameStartOverlappingSplitter().split(source_day_entries))
