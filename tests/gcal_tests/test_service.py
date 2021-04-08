import unittest

from gcal.mapper import GoogleCalendarMapper
from gcal.processor import WholeMonthProcessor
from gcal.service import GoogleDayEntryService, GoogleCalendarService
from tests.calendar_mock import GoogleCalendarServiceBuilderMock


class TestGoogleDayEntryService(unittest.TestCase):
    def test_processing_events_from_gcal(self):
        self.assertEqual(23, len(GoogleDayEntryService(
            GoogleCalendarService(GoogleCalendarServiceBuilderMock()), GoogleCalendarMapper(),
            WholeMonthProcessor()).day_entries_in_month(2020, 8)))


if __name__ == '__main__':
    unittest.main()
