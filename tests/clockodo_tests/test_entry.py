import unittest
from unittest import mock

from clockodo.entry import ClockodoEntryService
from clockodo.mapper import ClockodoDayMapper
from gcal.mapper import CalendarEventMapper
from tests.calendar_mock import GoogleCalendarServiceBuilderMock
from tests.clockodo_tests.clockodo_mock import ClockodoResolutionServiceMock, mocked_requests_post, \
    mocked_requests_delete, mocked_requests_get


class TestEntry(unittest.TestCase):
    def test_entry_logging(self):
        self.assertEqual("Coaching(from='2021-04-29 13:00:00', to='2021-04-29 14:00:00', text='WG: AG Agile Weekly')", ClockodoEntryService('test@here', 'None')._entry_fields_to_string(
            {'id': 45971948, 'users_id': 148220, 'projects_id': 1244898, 'customers_id': 1438790, 'services_id': 549399,
             'hourly_rate': 162.5, 'billable': 1, 'time_insert': '2021-04-14 16:15:59',
             'time_since': '2021-04-29 13:00:00', 'time_until': '2021-04-29 14:00:00', 'offset': 0, 'duration': 3600,
             'clocked': False, 'lumpSum': None, 'time_last_change': '2021-04-14 16:15:59',
             'time_last_change_work_time': '2021-04-14 16:15:59', 'lumpSums_id': None, 'time_clocked_since': None,
             'offline': False, 'revenue': 162.5, 'budget_is_hours': False, 'budget_is_not_strict': False,
             'customers_name': 'AOK Systems GmbH', 'projects_name': 'Coach the Coaches PO 10528/10721',
             'services_name': 'Coaching', 'users_name': 'Christian Dähn', 'lumpSums_price': None, 'lumpSums_unit': None,
             'lumpSums_name': None, 'lumpSums_amount': None, 'billed': False, 'texts_id': 15966637,
             'text': 'WG: AG Agile Weekly', 'duration_time': '01:00:00', 'offset_time': '00:00:00',
             'is_clocking': False, 'budget': 0}))


class TestEntryService(unittest.TestCase):

    @mock.patch(f'{ClockodoEntryService.__module__}.requests.get', side_effect=mocked_requests_get)
    @mock.patch(f'{ClockodoEntryService.__module__}.requests.delete', side_effect=mocked_requests_delete)
    def test_delete_one_entry(self, delete_mock, get_mock):
        entry_service = ClockodoEntryService('test@here', 'None')
        entry_service.delete_entries(2020, 8)

        self.assertTrue(get_mock.called)
        self.assertEqual('https://my.clockodo.com/api/users', get_mock.call_args_list[0].args[0])
        self.assertEqual('https://my.clockodo.com/api/entries', get_mock.call_args_list[1].args[0])
        self.assertTrue(delete_mock.called)
        self.assertEqual('https://my.clockodo.com/api/entries/1', delete_mock.call_args.args[0])

    @mock.patch(f'{ClockodoEntryService.__module__}.requests.post', side_effect=mocked_requests_post)
    def test_enter_entries(self, post_mock):
        entry_service = ClockodoEntryService('test@here', 'None')

        clockodo_days = ClockodoDayMapper(ClockodoResolutionServiceMock()).to_clockodo_days(
            CalendarEventMapper().to_calendar_events(GoogleCalendarServiceBuilderMock().calendar_events))

        entry_service.enter_calendar_events(clockodo_days)

        self.assertTrue(post_mock.called)
        self.assertEqual(23, post_mock.call_count)
        self.assertTrue(
            all([call.args[0] == 'https://my.clockodo.com/api/entries' for call in post_mock.call_args_list]))


if __name__ == '__main__':
    unittest.main()
