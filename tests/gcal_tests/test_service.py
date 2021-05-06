import unittest

from clockodo.entity import ClockodoDay, ClockodoIdMapping
from gcal.mapper import CalendarEventMapper
from gcal.processor import WholeMonthProcessor
from gcal.service import GoogleCalendarEventProcessor, GoogleCalendarService
from shared.persistence import PersistenceMapping
from tests.calendar_mock import GoogleCalendarServiceBuilderMock


class TestGoogleDayEntryService(unittest.TestCase):
    def test_processing_events_from_gcal(self):
        self.assertEqual(21, len(GoogleCalendarEventProcessor(
            GoogleCalendarService(GoogleCalendarServiceBuilderMock.from_fixture()), CalendarEventMapper(),
            WholeMonthProcessor()).calendar_events_in_month(2020, 8)))

