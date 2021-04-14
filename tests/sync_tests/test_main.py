import unittest
from optparse import OptionParser
from unittest import TestCase, mock
from unittest.mock import patch

from google_auth_oauthlib.flow import InstalledAppFlow

from sync.main import build_service, parse_arguments, main
from sync.service import CalendarSyncService


class SysExitAssertionError(AssertionError):
    def __init__(self, status: int, message: str):
        self.message = message
        self.status = status


class FailingOptionsParser(OptionParser):
    def __init__(self, args_=[]):
        super().__init__()
        self.args_ = args_
        self.add_option('-d', dest='dry_run', action='store_true')

    def _get_args(self, args):
        return self.args_

    def exit(self, status=0, msg=None):
        raise SysExitAssertionError(status, msg)

    def print_usage(self, file=None):
        pass


class TestMainParse(TestCase):
    @patch(f'{InstalledAppFlow.__module__}.{InstalledAppFlow.__name__}.from_client_secrets_file')
    def test_build_service(self, flow_mock):
        self.assertIsInstance(build_service('test@here', 'None'), CalendarSyncService)

    def test_parse_fails_on_empty_arguments(self):
        self._assert_optparse_fail('', 'incorrect date')

    def test_parse_fails_on_too_short_arguments(self):
        self._assert_optparse_fail('20210', 'incorrect date')

    def test_parse_fails_on_too_many_arguments(self):
        self._assert_optparse_fail('2021077', 'incorrect date')

    def test_parse_fail_year_before_2000(self):
        self._assert_optparse_fail('199908', 'invalid year')

    def test_parse_fail_year_after_2100(self):
        self._assert_optparse_fail('210108', 'invalid year')

    def test_parse_fail_month_0(self):
        self._assert_optparse_fail('202100', 'invalid month')

    def test_parse_fail_month_after_12(self):
        self._assert_optparse_fail('202113', 'invalid month')

    def test_parse_valid_year_month(self):
        year, month, dry_run = parse_arguments(FailingOptionsParser(['202008']))
        self.assertEqual(2020, year)
        self.assertEqual(8, month)
        self.assertFalse(dry_run)

    def _assert_optparse_fail(self, argument, expected_error, fail_status=2):
        with self.assertRaises(SysExitAssertionError) as context:
            parse_arguments(FailingOptionsParser([argument]))
        self.assertEqual(fail_status, context.exception.status)
        self.assertRegex(context.exception.message, f'error: {expected_error}')


class TestMainExecute(TestCase):

    @mock.patch(f'{main.__module__}.basicConfig')
    @mock.patch(f'{main.__module__}.build_service')
    @mock.patch(f'{main.__module__}.get_credentials')
    def test_main_performs_sync(self, credentials_mock, build_service_mock, logger_mock):
        credentials_mock.return_value = ('test@here', 'None')
        main(FailingOptionsParser(['202008']))
        self.assertEqual('().sync_month', build_service_mock.mock_calls[1][0])
        self.assertEqual((2020, 8), build_service_mock.mock_calls[1][1])


if __name__ == '__main__':
    unittest.main()