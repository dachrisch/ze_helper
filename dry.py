import calendar
import logging
import sys
from datetime import datetime, timedelta
from functools import reduce
from logging import getLogger, basicConfig

from service.gcal import GoogleCalendarServiceBuilder, GoogleCalendarServiceWrapper


def main(yearmonth: str):
    year, month = map(int, (yearmonth[:4], yearmonth[4:6]))
    service = GoogleCalendarServiceWrapper(GoogleCalendarServiceBuilder())
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])
    events = service.events_in_range(first_day, last_day)

    for event in events:
        getLogger(__name__).info(event)

    for label in set(map(lambda event: event.label, events)):
        time_in_label = reduce(lambda x, y: x + y.timediff, filter(lambda event: event.label == label, events),
                               timedelta())
        getLogger(__name__).info(f'{label}: {time_in_label.total_seconds() / 60 / 60:.2f}')


if __name__ == '__main__':
    basicConfig(level=logging.DEBUG)
    if len(sys.argv) != 2:
        getLogger(__name__).error('usage: %s {year}{month}' % sys.argv[0])
        sys.exit(-1)
    main(sys.argv[1])
