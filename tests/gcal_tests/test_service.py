import unittest
from datetime import datetime

from clockodo.mapper import ClockodoDayMapper
from gcal.entity import PrivateProperties
from gcal.mapper import CalendarEventMapper
from gcal.processor import WholeMonthProcessor
from gcal.service import GoogleCalendarEventProcessor, GoogleCalendarService
from shared.persistence import PersistenceMapping
from sync.service import GoogleCalendarEventUpdaterService
from tests.calendar_mock import GoogleCalendarServiceBuilderMock
from tests.clockodo_tests.clockodo_mock import ClockodoResolutionServiceMock


class TestGoogleDayEntryService(unittest.TestCase):
    def test_processing_events_from_gcal(self):
        self.assertEqual(23, len(GoogleCalendarEventProcessor(
            GoogleCalendarService(GoogleCalendarServiceBuilderMock()), CalendarEventMapper(),
            WholeMonthProcessor()).calendar_events_in_month(2020, 8)))


class TestGoogleCalendarEventUpdaterService(unittest.TestCase):
    def test_write_private_properties(self):
        calendar_service = GoogleCalendarService(GoogleCalendarServiceBuilderMock())
        single_event_date = datetime(2020, 8, 24)
        one_event = calendar_service.fetch_events_from_service(single_event_date, single_event_date.replace(hour=23))[0]

        calendar_event = CalendarEventMapper().to_calendar_event(one_event)

        clockodo_day = ClockodoDayMapper(ClockodoResolutionServiceMock()).to_clockodo_day(calendar_event)
        persistence_mapping = PersistenceMapping('1234')
        clockodo_day.update_persistence_mapping(persistence_mapping)
        GoogleCalendarEventUpdaterService(calendar_service).store_clockodo_link(calendar_event, clockodo_day)

        second = calendar_service.fetch_events_from_service(single_event_date, single_event_date.replace(hour=23))[0]
        self.assertEqual(PrivateProperties.from_mapping(persistence_mapping),
                         CalendarEventMapper().to_calendar_event(second).private_properties)


if __name__ == '__main__':
    unittest.main()
