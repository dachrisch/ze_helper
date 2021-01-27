import calendar
import logging
from configparser import ConfigParser
from datetime import datetime
from logging import getLogger, basicConfig

import requests
from requests.auth import HTTPBasicAuth

from entity.day import DayEntry, WorkshopDayEntry, WorkshopPrepDayEntry, InternalDayEntry
from service.gcal import GoogleCalendarService, GoogleCalendarServiceBuilder


class ClockodoDay(object):
    def __init__(self, start_date: datetime, end_date: datetime, comment, customer_id, service_id, billable):
        self.comment = comment
        self.billable = billable
        self.service_id = service_id
        self.customer_id = customer_id
        self.end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        self.start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')


class ClockodoDayMapper(object):
    def to_clockodo_day(self, event: DayEntry):
        date = datetime.strptime(event.date, '%d.%m.%Y')
        start_time = datetime.strptime(event.start, '%H:%M')
        end_time = datetime.strptime(event.end, '%H:%M')
        start_date = datetime(date.year, date.month, date.day, start_time.hour, start_time.minute, 0)
        end_date = datetime(date.year, date.month, date.day, end_time.hour, end_time.minute, 0)
        if event.__class__ == WorkshopDayEntry:
            return ClockodoDay(start_date, end_date, event.comment, 1462125, 549396, 1)
        elif event.__class__ == WorkshopPrepDayEntry:
            return ClockodoDay(start_date, end_date, event.comment, 1462125, 572017, 1)
        elif event.__class__ == InternalDayEntry or event.__class__ == DayEntry:
            return ClockodoDay(start_date, end_date, event.comment, 1361511, 549394, 1)
        else:
            raise Exception("don't know how to map [%s]" % event)

    def json_to_logging(self, json: dict):
        if 'services_name' in json:
            service = json['services_name']
        else:
            service = json['services_id']
        return f"({service})[from={json['time_since']}, duration={json['duration_time']}, text={json['text']}]"


class ClockodoEntryService(object):
    base_url = 'https://my.clockodo.com/api'

    def __init__(self, email: str, api_key: str):
        self.api_key = api_key
        self.email = email
        self.google_calendar_service = GoogleCalendarService(GoogleCalendarServiceBuilder())
        self.day_entry_mapper = ClockodoDayMapper()

    def delete_entries(self, year: int, month: int):
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

        current_entries = self._current_entries(first_day, last_day)
        for entry in current_entries:
            self._delete(entry)

    def enter_events_from_gcal(self, year, month):
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
        for event in self.google_calendar_service.events_in_range(first_day, last_day):
            self._enter(event)

    def _get_auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.email, self.api_key)

    def _get_user_id(self) -> str:
        users = requests.get(self.base_url + '/users', auth=self._get_auth()).json()['users']
        user_id = list(filter(lambda x: x['email'] == self.email, users))[0]['id']
        return user_id

    def _current_entries(self, first_day, last_day):
        current_entries = requests.get(self.base_url + '/entries', auth=self._get_auth(),
                                       params={'time_since': first_day.strftime('%Y-%m-%d %H:%M:%S'),
                                               'time_until': last_day.strftime('%Y-%m-%d %H:%M:%S'),
                                               'filter[users_id]': self._get_user_id()}).json()['entries']
        return current_entries

    def _delete(self, entry: dict):
        getLogger(self.__class__.__name__).info(f'deleting entry [{self.day_entry_mapper.json_to_logging(entry)}]...')
        response = requests.delete(self.base_url + '/entries/%s' % entry['id'], auth=self._get_auth())
        assert response.json()['success'] is True, response.json()

    def _enter(self, event: DayEntry):
        day_entry = self.day_entry_mapper.to_clockodo_day(event)
        response = requests.post(self.base_url + '/entries', auth=self._get_auth(),
                                 params={'customers_id': day_entry.customer_id,
                                         'billable': day_entry.billable,
                                         'services_id': day_entry.service_id,
                                         'time_since': day_entry.start_date_str,
                                         'time_until': day_entry.end_date_str,
                                         'text': day_entry.comment})

        getLogger(self.__class__.__name__).info(
            f'inserting entry [{self.day_entry_mapper.json_to_logging(response.json()["entry"])}]...')


def main():
    basicConfig(level=logging.INFO)
    config_parser = ConfigParser()
    config_parser.read('credentials.properties')
    email = config_parser['credentials']['email']
    api_key = config_parser['credentials']['api_key']
    entry_service = ClockodoEntryService(email, api_key)
    entry_service.delete_entries(2021, 1)
    entry_service.enter_events_from_gcal(2021, 1)


main()
