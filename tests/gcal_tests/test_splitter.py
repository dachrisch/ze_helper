import unittest
from datetime import datetime

from gcal.entity import CalendarEvent
from gcal.splitter import MiddleEntryOverlappingSplitter, EndEntryOverlappingSplitter, \
    MultipleEntriesOverlappingSplitter, SameStartOverlappingSplitter


class TestSplitDayEntries(unittest.TestCase):

    def test_split_overlapping_middle(self):
        source_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'Big Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Small Arbeit'))
        expected_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'Big Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Small Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 16), 'Big Arbeit'))

        self.assertTrue(MiddleEntryOverlappingSplitter().accept(source_calendar_events))
        self.assertEqual(expected_calendar_events, MiddleEntryOverlappingSplitter().split(source_calendar_events))

    def test_split_overlapping_end(self):
        source_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'))
        expected_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 15), 'First Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'))

        self.assertTrue(EndEntryOverlappingSplitter().accept(source_calendar_events))
        self.assertEqual(expected_calendar_events, EndEntryOverlappingSplitter().split(source_calendar_events))

    def test_split_overlapping_middle_and_end(self):
        source_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'))
        expected_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'First Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 15), 'First Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'))
        self.assertTrue(MultipleEntriesOverlappingSplitter().accept(source_calendar_events))
        self.assertEqual(expected_calendar_events, MultipleEntriesOverlappingSplitter().split(source_calendar_events))

    def test_not_overlapping_returns_list(self):
        source_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 12), 'First Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 14), 'Second Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 14), datetime(2021, 2, 1, 16), 'Third Arbeit'))

        self.assertTrue(MultipleEntriesOverlappingSplitter().accept(source_calendar_events))
        self.assertEqual(source_calendar_events, MultipleEntriesOverlappingSplitter().split(source_calendar_events))

    def test_split_same_start_overlapping(self):
        source_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 12), 'Second Arbeit'))
        expected_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 16), 'First Arbeit'))
        self.assertTrue(SameStartOverlappingSplitter().accept(source_calendar_events))
        self.assertEqual(expected_calendar_events, SameStartOverlappingSplitter().split(source_calendar_events))
