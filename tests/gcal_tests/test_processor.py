import unittest
from copy import deepcopy
from datetime import datetime, timedelta

from gcal.entity import CalendarEvent
from gcal.filter import VacationCalendarEventFilter, BreakCalendarEventFilter
from gcal.mapper import CalendarEventMapper
from gcal.processor import WholeMonthProcessor
from tests.calendar_mock import GoogleCalendarServiceBuilderMock


class TestProcessWholeMonth(unittest.TestCase):
    def test_processes_two_days_in_a_row(self):
        source_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 2, 10), datetime(2021, 2, 2, 16), 'First Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 12), 'Second Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 2, 15), datetime(2021, 2, 2, 17), 'Last Arbeit')
                                  )
        expected_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'First Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 15), 'First Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 17), 'Last Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 2, 10), datetime(2021, 2, 2, 11), 'First Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 12), 'Second Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 2, 12), datetime(2021, 2, 2, 15), 'First Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 2, 15), datetime(2021, 2, 2, 17), 'Last Arbeit')
                                    )

        self.assertEqual(expected_calendar_events, WholeMonthProcessor().process(source_calendar_events))

    def test_processes_vacations(self):
        source_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 2), datetime(2021, 2, 2), 'Urlaub')
                                  )
        expected_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'First Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Second Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 16), 'First Arbeit')
                                    )

        self.assertEqual(expected_calendar_events, WholeMonthProcessor().process(source_calendar_events))

    def test_processes_breaks(self):
        source_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 16), 'First Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 11), datetime(2021, 2, 1, 12), 'Pause')
                                  )
        expected_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 1, 11), 'First Arbeit'),
                                    CalendarEvent(datetime(2021, 2, 1, 12), datetime(2021, 2, 1, 16), 'First Arbeit')
                                    )

        self.assertEqual(expected_calendar_events, WholeMonthProcessor().process(source_calendar_events))

    def test_processes_complete_month(self):
        source_calendar_events = CalendarEventMapper().to_calendar_events(
            GoogleCalendarServiceBuilderMock.from_fixture().calendar_events)
        self.assertEqual(23, len(source_calendar_events))
        working_days = list(VacationCalendarEventFilter().filter(source_calendar_events))
        self.assertEqual(22, len(working_days))
        self.assertEqual(23, len(BreakCalendarEventFilter().filter(source_calendar_events)))
        processed_calendar_events = WholeMonthProcessor().process(source_calendar_events)
        assert working_days[-2].end.hour == 16
        working_days.append(deepcopy(working_days[-2]))
        working_days[-2].end -= timedelta(hours=4)
        working_days[-1].start += timedelta(hours=4)
        self.assertEqual(self._to_comparable_list(working_days), self._to_comparable_list(processed_calendar_events))

    def test_special_month(self):
        source_calendar_events = (CalendarEvent(datetime(2021, 2, 1, 8, 30), datetime(2021, 2, 1, 17), 'First Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 9, 30), datetime(2021, 2, 1, 12, 30),
                                                'Second Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 12, 30), datetime(2021, 2, 1, 13), 'Pause'),
                                  CalendarEvent(datetime(2021, 2, 1, 13), datetime(2021, 2, 1, 15), 'Third Arbeit'),
                                  CalendarEvent(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 16), 'Fourth Arbeit'),
                                  )
        expected_calendar_events = (
        CalendarEvent(datetime(2021, 2, 1, 8, 30), datetime(2021, 2, 1, 9, 30), 'First Arbeit'),
        CalendarEvent(datetime(2021, 2, 1, 9, 30), datetime(2021, 2, 1, 12, 30), 'Second Arbeit'),
        CalendarEvent(datetime(2021, 2, 1, 13), datetime(2021, 2, 1, 15), 'Third Arbeit'),
        CalendarEvent(datetime(2021, 2, 1, 15), datetime(2021, 2, 1, 16), 'Fourth Arbeit'),
        CalendarEvent(datetime(2021, 2, 1, 16), datetime(2021, 2, 1, 17), 'First Arbeit'),
        )

        self.assertEqual(expected_calendar_events, WholeMonthProcessor().process(source_calendar_events))

    def _to_comparable_list(self, working_days: [CalendarEvent]) -> [str]:
        return [f'{event.start.day} {event.start.hour}-{event.summary}' for event in working_days]


if __name__ == '__main__':
    unittest.main()
