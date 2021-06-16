import unittest

from gcal.mapper import CalendarEventMapper
from gcal.processor import WholeMonthProcessor
from gcal.service import GoogleCalendarEventProcessor, GoogleCalendarService
from tests.calendar_mock import GoogleCalendarServiceBuilderMock


class TestGoogleDayEntryService(unittest.TestCase):
    def test_processing_events_from_gcal(self):
        events_in_month = GoogleCalendarEventProcessor(
            GoogleCalendarService(GoogleCalendarServiceBuilderMock.from_fixture()),
            CalendarEventMapper(), WholeMonthProcessor()).calendar_events_in_month(
            2020, 8)
        self.assertEqual(21, len(events_in_month))
