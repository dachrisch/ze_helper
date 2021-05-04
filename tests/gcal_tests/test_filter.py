import unittest
from datetime import datetime

from gcal.entity import CalendarEvent
from gcal.filter import VacationCalendarEventFilter, BreakCalendarEventFilter, BusyCalendarEventFilter, \
    CalendarEventFilterChain


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

    def test_filter_free(self):
        workcalendar_event = CalendarEvent(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 12), 'Arbeit')
        calendar_events = (CalendarEvent(datetime(2021, 2, 1), datetime(2021, 2, 3), 'Arbeit', busy=False),
                           workcalendar_event)

        self.assertEqual((workcalendar_event,), BusyCalendarEventFilter().filter(calendar_events))

    def test_dont_filter_busy(self):
        calendar_events = (CalendarEvent(datetime(2021, 2, 1), datetime(2021, 2, 3), 'Arbeit', busy=True),
                           (CalendarEvent(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 12), 'Arbeit')))

        self.assertEqual(calendar_events, BusyCalendarEventFilter().filter(calendar_events))

    def test_filter_vacation_and_busy_free(self):
        calendar_event = CalendarEvent(datetime(2021, 2, 1, 10), datetime(2021, 2, 3, 11), 'Arbeit', busy=True)
        calendar_events = (calendar_event,
                           CalendarEvent(datetime(2021, 2, 2, 11), datetime(2021, 2, 2, 12), 'Pause'),
                           CalendarEvent(datetime(2021, 2, 2, 13), datetime(2021, 2, 2, 14), 'Arbeit', busy=False),
                           CalendarEvent(datetime(2021, 2, 3), datetime(2021, 2, 4), 'Urlaub'),
                           CalendarEvent(datetime(2021, 2, 5), datetime(2021, 2, 5), 'Arbeit', busy=False)
                           )

        self.assertEqual((calendar_event,), CalendarEventFilterChain(
            (BusyCalendarEventFilter(), BreakCalendarEventFilter(), VacationCalendarEventFilter())).filter(
            calendar_events))
