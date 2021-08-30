import unittest
from unittest import mock

from clockodo.connector import ClockodoApiConnector
from clockodo.entry import ClockodoEntryService
from clockodo.mapper import ClockodoDayMapper
from clockodo.resolution import ClockodoResolutionChain
from gcal.mapper import CalendarEventMapper
from gcal.processor import WholeMonthProcessor
from gcal.service import GoogleCalendarEventProcessor, GoogleCalendarService
from sync.service import CalendarSyncService
from tests.calendar_mock import GoogleCalendarServiceBuilderMock
from tests.clockodo_tests.clockodo_mock import mocked_requests_get, \
    mocked_requests_delete, mocked_requests_post


class TestCalendarSyncService(unittest.TestCase):
    @mock.patch(f'{ClockodoApiConnector.__module__}.requests.get', side_effect=mocked_requests_get)
    @mock.patch(f'{ClockodoApiConnector.__module__}.requests.delete', side_effect=mocked_requests_delete)
    @mock.patch(f'{ClockodoApiConnector.__module__}.requests.post', side_effect=mocked_requests_post)
    def test_sync_month(self, post_mock, delete_mock, get_mock):
        calendar_service = GoogleCalendarService(GoogleCalendarServiceBuilderMock.from_fixture())
        api_connector = ClockodoApiConnector('test@here', 'None')
        CalendarSyncService(GoogleCalendarEventProcessor(
            calendar_service, CalendarEventMapper(),
            WholeMonthProcessor()), ClockodoEntryService(api_connector),
            ClockodoDayMapper(ClockodoResolutionChain(api_connector))).sync_month(2020, 8)

        self.assertTrue(get_mock.called)
        self.assertEqual('https://my.clockodo.com/api/users', get_mock.call_args_list[0].args[0])
        self.assertEqual('https://my.clockodo.com/api/entries', get_mock.call_args_list[1].args[0])
        self.assertTrue(delete_mock.called)
        self.assertEqual('https://my.clockodo.com/api/entries/1', delete_mock.call_args.args[0])
        self.assertTrue(post_mock.called)
        self.assertEqual(21, post_mock.call_count)
        self.assertTrue(
            all([call.args[0] == 'https://my.clockodo.com/api/entries' for call in post_mock.call_args_list]))
