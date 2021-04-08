import unittest
from unittest import mock

from clockodo.entry import ClockodoEntryService
from clockodo.mapper import ClockodoDayMapper
from gcal.mapper import GoogleCalendarMapper
from gcal.processor import WholeMonthProcessor
from gcal.service import GoogleDayEntryService, GoogleCalendarService
from tests.calendar_mock import GoogleCalendarServiceBuilderMock
from tests.clockodo_tests.clockodo_mock import ClockodoResolutionServiceMock


class MockResponse(object):

    def __init__(self, endpoint, return_json):
        self.endpoint = endpoint
        self.return_json = return_json

    def json(self):
        return self.return_json[self.endpoint]


def mocked_requests_post(*args, **kwargs):
    if args[0].startswith('https://my.clockodo.com/api/entries'):
        return MockResponse('entries', {'entries': {'item': kwargs}})
    else:
        raise ValueError(f'unknow url {args[0]}')


def mocked_requests_delete(*args, **kwargs):
    if args[0].startswith('https://my.clockodo.com/api/'):
        return MockResponse('/'.join(args[0].split('/')[-2:]), {'entries/1': 'success'})
    else:
        raise ValueError(f'unknow url {args[0]}')


def mocked_requests_get(*args, **kwargs):
    fixtures = {
        'users': {
            'users': ({'id': 1, 'email': 'test@here'},), },
        'entries': {
            'entries': ({'services_name': 'Test Service',
                         'time_since': 1,
                         'duration_time': 1,
                         'text': 'test',
                         'id': 1},), }
    }
    if args[0].startswith('https://my.clockodo.com/api/'):
        return MockResponse(args[0].split('/')[-1], fixtures)
    else:
        raise ValueError(f'unknow url {args[0]}')


class TestEntryService(unittest.TestCase):

    @mock.patch(f'{ClockodoEntryService.__module__}.requests.get', side_effect=mocked_requests_get)
    @mock.patch(f'{ClockodoEntryService.__module__}.requests.delete', side_effect=mocked_requests_delete)
    def test_delete_one_entry(self, delete_mock, get_mock):
        entry_service = ClockodoEntryService('test@here', "None", GoogleDayEntryService(
            GoogleCalendarService(GoogleCalendarServiceBuilderMock()),
            GoogleCalendarMapper(),
            WholeMonthProcessor()),
                                             ClockodoDayMapper(ClockodoResolutionServiceMock()))
        entry_service.delete_entries(2020, 8)

        self.assertTrue(get_mock.called)
        self.assertEqual('https://my.clockodo.com/api/users', get_mock.call_args_list[0].args[0])
        self.assertEqual('https://my.clockodo.com/api/entries', get_mock.call_args_list[1].args[0])
        self.assertTrue(delete_mock.called)
        self.assertEqual('https://my.clockodo.com/api/entries/1', delete_mock.call_args.args[0])

    @mock.patch(f'{ClockodoEntryService.__module__}.requests.post', side_effect=mocked_requests_post)
    def test_enter_entries(self, post_mock):
        entry_service = ClockodoEntryService('test@here', "None", GoogleDayEntryService(
            GoogleCalendarService(GoogleCalendarServiceBuilderMock()),
            GoogleCalendarMapper(),
            WholeMonthProcessor()),
                                             ClockodoDayMapper(ClockodoResolutionServiceMock()))
        entry_service.enter_events_from_gcal(2020, 8)

        self.assertTrue(post_mock.called)
        self.assertEqual(23, post_mock.call_count)
        self.assertTrue(
            all([call.args[0] == 'https://my.clockodo.com/api/entries' for call in post_mock.call_args_list]))


if __name__ == '__main__':
    unittest.main()
