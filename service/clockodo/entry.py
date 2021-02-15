import calendar
import logging
from datetime import datetime
from logging import getLogger, basicConfig

from service.clockodo import ClockodoService
from service.clockodo.mapping import ClockodoDayMapper
from service.gcal import GoogleCalendarServiceWrapper


class ClockodoEntryService(object):

    def __init__(self,
                 google_calendar_service: GoogleCalendarServiceWrapper,
                 clockodo_service: ClockodoService, day_entry_mapper: ClockodoDayMapper):
        self.day_entry_mapper = day_entry_mapper
        self.google_calendar_service = google_calendar_service
        self.clockodo_service = clockodo_service

    def delete_entries(self, year: int, month: int):
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

        current_entries = self.clockodo_service.current_entries(first_day, last_day)
        for entry in current_entries:
            getLogger(self.__class__.__name__).info(
                f'deleting entry [{self.day_entry_mapper.json_to_logging(entry)}]...')
            self.clockodo_service.delete(entry)

    def enter_events_from_gcal(self, year, month):
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
        for event in self.google_calendar_service.events_in_range(first_day, last_day):
            day_entry = self.day_entry_mapper.to_clockodo_day(event)
            self.clockodo_service.enter(day_entry)


def clockodo_entries_for(year: int, month: int):
    entry_service = ClockodoEntryService()
    entry_service.delete_entries(year, month)
    entry_service.enter_events_from_gcal(year, month)


def main(arguments):
    basicConfig(level=logging.INFO)
    program = arguments[0]
    if len(arguments) != 2:
        getLogger(__name__).info(f'usage: {program} {{year}}{{month}}')
        sys.exit(-1)
    yearmonth = arguments[1]
    year, month = map(int, (yearmonth[:4], yearmonth[4:6]))
    if not ((month < 13) and (month > 0)):
        getLogger(__name__).error('invalid month: %s (1..12)' % month)
        sys.exit(1)
    if not ((year < 2100) and (year > 2000)):
        getLogger(__name__).error('invalid year: %s (2000..2100)' % year)
        sys.exit(2)
    clockodo_entries_for(year, month)


if __name__ == '__main__':
    import sys

    main(sys.argv)
