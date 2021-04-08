import logging
from configparser import ConfigParser
from functools import partial
from logging import basicConfig
from optparse import OptionParser
from unittest.mock import patch

from clockodo.dry import post_logger, delete_logger
from clockodo.entry import ClockodoEntryService
from clockodo.mapper import ClockodoDayMapper
from clockodo.resolution import ClockodoResolutionService
from gcal.mapper import GoogleCalendarMapper
from gcal.processor import WholeMonthProcessor
from gcal.service import GoogleDayEntryService, GoogleCalendarService, GoogleCalendarServiceBuilder


def clockodo_entries_for(year: int, month: int):
    config_parser = ConfigParser()
    config_parser.read('credentials.properties')
    email = config_parser['credentials']['email']
    api_key = config_parser['credentials']['api_key']
    entry_service = build_service(email, api_key)
    entry_service.delete_entries(year, month)
    entry_service.enter_events_from_gcal(year, month)


def build_service(email: str, api_key: str) -> ClockodoEntryService:
    return ClockodoEntryService(email, api_key, GoogleDayEntryService(
        GoogleCalendarService(GoogleCalendarServiceBuilder()),
        GoogleCalendarMapper(),
        WholeMonthProcessor()),
                                ClockodoDayMapper(ClockodoResolutionService(email, api_key)))


def main(arguments_parser: OptionParser):
    basicConfig(level=logging.INFO)
    year, month, dry_run = parse_arguments(arguments_parser)

    if dry_run:
        with patch(f'{ClockodoEntryService.__module__}.requests.delete',
                   side_effect=partial(delete_logger, method='delete')):
            with patch(f'{ClockodoEntryService.__module__}.requests.post',
                       side_effect=partial(post_logger, method='post')):
                clockodo_entries_for(year, month)
    else:
        clockodo_entries_for(year, month)


def parse_arguments(arguments_parser):
    (options, arguments) = arguments_parser.parse_args()
    if len(arguments) != 1 or len(arguments[0]) != 6:
        arguments_parser.error('incorrect date')
        sys.exit(-1)
    yearmonth = arguments[0]
    year, month = map(int, (yearmonth[:4], yearmonth[4:6]))
    if not ((month < 13) and (month > 0)):
        arguments_parser.error('invalid month: %s (1..12)' % month)
        sys.exit(1)
    if not ((year < 2100) and (year > 2000)):
        arguments_parser.error('invalid year: %s (2000..2100)' % year)
        sys.exit(2)
    return year, month, options.dry_run


if __name__ == '__main__':
    import sys

    parser = OptionParser('%prog [options] {year}{month}')
    parser.add_option('-d', '--dry', dest='dry_run', action='store_true',
                      help='just print what would be done')

    main(parser)
