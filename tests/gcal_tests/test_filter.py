import unittest
from datetime import datetime

from gcal.entity import DayEntry
from gcal.filter import VacationDayEntryFilter, BreakDayEntryFilter


class TestFilterDayEntries(unittest.TestCase):
    def test_filter_vacations(self):
        workday_entry = DayEntry(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 12), 'Arbeit')
        day_entries = (DayEntry(datetime(2021, 2, 1), datetime(2021, 2, 3), 'Urlaub'),
                       workday_entry)

        self.assertEqual((workday_entry,), VacationDayEntryFilter().filter(day_entries))

    def test_filter_breaks(self):
        workday_entry = DayEntry(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 13), 'Arbeit')
        day_entries = (DayEntry(datetime(2021, 2, 1, 12), datetime(2021, 2, 3, 12, 30), 'Pause'),
                       workday_entry)

        self.assertEqual((workday_entry,), BreakDayEntryFilter().filter(day_entries))
