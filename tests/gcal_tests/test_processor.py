import unittest
from copy import deepcopy
from datetime import datetime, timedelta

from gcal.entity import DayEntry
from gcal.filter import VacationDayEntryFilter, BreakDayEntryFilter
from gcal.mapper import GoogleCalendarMapper
from gcal.processor import WholeMonthProcessor
from tests.calendar_mock import GoogleCalendarServiceBuilderMock


class TestProcessWholeMonth(unittest.TestCase):
    def test_processes_two_days_in_a_row(self):
        source_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'),
                              DayEntry(datetime(2021, 2, 2, 10), datetime(2021, 2, 2, 16), 'First Arbeit'),
                              DayEntry(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 12), 'Second Arbeit'),
                              DayEntry(datetime(2021, 2, 2, 15), datetime(2021, 2, 2, 17), 'Last Arbeit')
                              )
        expected_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 15), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'),
                                DayEntry(datetime(2021, 2, 2, 10), datetime(2021, 2, 2, 11), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 12), 'Second Arbeit'),
                                DayEntry(datetime(2021, 2, 2, 12), datetime(2021, 2, 2, 15), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 2, 15), datetime(2021, 2, 2, 17), 'Last Arbeit')
                                )

        self.assertEqual(expected_day_entries, WholeMonthProcessor().process(source_day_entries))

    def test_processes_vacations(self):
        source_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                              DayEntry(datetime(2021, 2, 2), datetime(2021, 2, 2), 'Urlaub')
                              )
        expected_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 16), 'First Arbeit')
                                )

        self.assertEqual(expected_day_entries, WholeMonthProcessor().process(source_day_entries))

    def test_processes_breaks(self):
        source_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Pause')
                              )
        expected_day_entries = (DayEntry(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 16), 'First Arbeit')
                                )

        self.assertEqual(expected_day_entries, WholeMonthProcessor().process(source_day_entries))

    def test_processes_complete_month(self):
        source_day_entries = GoogleCalendarMapper().to_day_entries(GoogleCalendarServiceBuilderMock().calendar_events)
        self.assertEqual(23, len(source_day_entries))
        working_days = list(VacationDayEntryFilter().filter(source_day_entries))
        self.assertEqual(22, len(working_days))
        self.assertEqual(23, len(BreakDayEntryFilter().filter(source_day_entries)))
        processed_day_entries = WholeMonthProcessor().process(source_day_entries)
        assert working_days[-2].end.hour == 16
        working_days.append(deepcopy(working_days[-2]))
        working_days[-2].end -= timedelta(hours=4)
        working_days[-1].start += timedelta(hours=4)
        self.assertEqual(self._to_comparable_list(working_days), self._to_comparable_list(processed_day_entries))

    def test_special_month(self):
        source_day_entries = (DayEntry(datetime(2021, 2, 1, 8, 30), datetime(2021, 2, 1, 17), 'First Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 9, 30), datetime(2021, 2, 1, 12, 30), 'Second Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 12, 30), datetime(2021, 2, 1, 13), 'Pause'),
                              DayEntry(datetime(2021, 2, 1, 13), datetime(2021, 2, 1, 15), 'Third Arbeit'),
                              DayEntry(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 16), 'Fourth Arbeit'),
                              )
        expected_day_entries = (DayEntry(datetime(2021, 2, 1, 8, 30), datetime(2021, 2, 1, 9, 30), 'First Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 9, 30), datetime(2021, 2, 1, 12, 30), 'Second Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 13), datetime(2021, 2, 1, 15), 'Third Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 16), 'Fourth Arbeit'),
                                DayEntry(datetime(2021, 2, 1, 16), datetime(2021, 2, 1, 17), 'First Arbeit'),
                                )

        self.assertEqual(expected_day_entries, WholeMonthProcessor().process(source_day_entries))

    def _to_comparable_list(self, working_days: [DayEntry]) -> [str]:
        return [f'{event.start.day} {event.start.hour}-{event.summary}' for event in working_days]


if __name__ == '__main__':
    unittest.main()
