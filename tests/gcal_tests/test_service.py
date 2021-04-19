import unittest

from clockodo.entity import ClockodoDay, ClockodoIdMapping
from clockodo.mapper import ClockodoDayMapper
from gcal.mapper import CalendarEventMapper
from gcal.processor import WholeMonthProcessor
from gcal.service import GoogleCalendarEventProcessor, GoogleCalendarService
from gcal.splitter import MultipleEntriesOverlappingSplitter
from shared.persistence import PersistenceMapping
from sync.service import GoogleCalendarEventUpdaterService
from tests.calendar_mock import GoogleCalendarServiceBuilderMock
from tests.clockodo_tests.clockodo_mock import ClockodoResolutionServiceMock


class TestGoogleDayEntryService(unittest.TestCase):
    def test_processing_events_from_gcal(self):
        self.assertEqual(23, len(GoogleCalendarEventProcessor(
            GoogleCalendarService(GoogleCalendarServiceBuilderMock.from_fixture()), CalendarEventMapper(),
            WholeMonthProcessor()).calendar_events_in_month(2020, 8)))


class TestGoogleCalendarEventUpdaterService(unittest.TestCase):
    def test_write_private_properties_single_entry(self):
        json_entry = {
            'id': '123',
            'start': {
                'dateTime': '2020-08-03T10:00:00+02:00'
            },
            'end': {
                'dateTime': '2020-08-03T12:00:00+02:00'
            },
            'summary': 'Test Event'
        }
        calendar_event = CalendarEventMapper().to_calendar_event(json_entry)

        clockodo_day = ClockodoDay(calendar_event.start, calendar_event.end, calendar_event.summary,
                                   ClockodoIdMapping(2, 3, 4))
        clockodo_day.update_persistence_mapping(PersistenceMapping('1234'))

        GoogleCalendarEventUpdaterService(
            GoogleCalendarService(GoogleCalendarServiceBuilderMock((json_entry,)))).store_clockodo_link(calendar_event,
                                                                                                        clockodo_day)

        self.assertEqual({'private': {'clockodo_mapping': {'direct': {'clockodo_id': '1234'}}}},
                         json_entry.get('extendedProperties'))
