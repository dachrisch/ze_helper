import unittest
from datetime import datetime

from gcal.entity import CalendarEvent
from gcal.filter import VacationCalendarEventFilter, BreakCalendarEventFilter


class TestFilterDayEntries(unittest.TestCase):
    def test_filter_vacations(self):
        workcalendar_event = CalendarEvent(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 12), 'Arbeit')
        calendar_events = (CalendarEvent(datetime(2021, 2, 1), datetime(2021, 2, 3), 'Urlaub'),
                       workcalendar_event)

        self.assertEqual((workcalendar_event,), VacationCalendarEventFilter().filter(calendar_events))

    def test_filter_breaks(self):
        workcalendar_event = CalendarEvent(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 13), 'Arbeit')
        calendar_events = (CalendarEvent(datetime(2021, 2, 1, 12), datetime(2021, 2, 3, 12, 30), 'Pause'),
                       workcalendar_event)

        self.assertEqual((workcalendar_event,), BreakCalendarEventFilter().filter(calendar_events))
