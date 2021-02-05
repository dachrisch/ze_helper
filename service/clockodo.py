import calendar
import logging
from configparser import ConfigParser
from datetime import datetime
from functools import lru_cache
from logging import getLogger, basicConfig

import requests
from requests.auth import HTTPBasicAuth

from entity.day import DayEntry, WorkshopDayEntry, WorkshopPrepDayEntry, InternalDayEntry, CustomerDayEntry, \
    ShorttimeDayEntry
from service.gcal import GoogleCalendarService, GoogleCalendarServiceBuilder


class ClockodoIdMapping(object):
    def __init__(self, customer_id: int, project_id: int, service_id: int, billable: int = 1):
        self.billable = billable
        self.service_id = service_id
        self.project_id = project_id
        self.customer_id = customer_id


class ClockodoDay(object):
    def __init__(self, start_date: datetime, end_date: datetime, comment: str, mapping: ClockodoIdMapping):
        self.comment = comment
        self.billable = mapping.billable
        self.service_id = mapping.service_id
        self.customer_id = mapping.customer_id
        self.project_id = mapping.project_id
        self.end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        self.start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')

    def __str__(self):
        return f"({self.customer_id})[from={self.start_date_str}, to={self.end_date_str}, comment={self.comment}]"


class ClockodoService(object):
    base_url = 'https://my.clockodo.com/api'

    def __init__(self, email: str, api_key: str):
        self.email = email
        self.api_key = api_key

    def _get_auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.email, self.api_key)

    def _get_user_id(self) -> str:
        users = requests.get(self.base_url + '/users', auth=self._get_auth()).json()['users']
        user_id = list(filter(lambda x: x['email'] == self.email, users))[0]['id']
        return user_id


class MappingError(ValueError):
    pass


class ClockodoResolutionService(ClockodoService):
    def __init__(self, email: str, api_key: str):
        super().__init__(email, api_key)

    def resolve_for(self, customer_name: str, project_name: str, service_name: str) -> ClockodoIdMapping:
        resolved_customer = next(
            filter(lambda customer: customer['name'] == customer_name, self._retrieve('customers')),
            None)
        if not resolved_customer:
            raise MappingError(f'no mapping found for customer [{customer_name}]')
        customer_id = resolved_customer['id']
        billable = 1 if resolved_customer['billable_default'] else 0
        project_id = next(filter(lambda project: project['name'] == project_name, resolved_customer['projects']),
                          {'id': 0})['id']
        if not project_id:
            raise MappingError(f'no mapping found for project [{project_name}]')
        service_id = next(filter(lambda service: service['name'] == service_name, self._retrieve('services')),
                          {'id': 0})['id']
        if not service_id:
            raise MappingError(f'no mapping found for service [{service_name}]')
        return ClockodoIdMapping(customer_id, project_id, service_id, billable)

    @lru_cache(128)
    def _retrieve(self, endpoint):
        return requests.get(self.base_url + f'/{endpoint}', auth=self._get_auth()).json()[endpoint]


class ClockodoDayMapper(object):

    def __init__(self, resolution_service: ClockodoResolutionService):
        self.resolution_service = resolution_service

    def to_clockodo_day(self, event: DayEntry) -> ClockodoDay:
        date = datetime.strptime(event.date, '%d.%m.%Y')
        start_time = datetime.strptime(event.start, '%H:%M')
        end_time = datetime.strptime(event.end, '%H:%M')
        start_date = datetime(date.year, date.month, date.day, start_time.hour, start_time.minute, 0)
        end_date = datetime(date.year, date.month, date.day, end_time.hour, end_time.minute, 0)
        mapping = None
        if isinstance(event, WorkshopDayEntry):
            mapping = self.resolution_service.resolve_for('Bayer AG',
                                                          'PM-Trainings 9-13 Bst.-Nr.: 2950100643',
                                                          'Inhouse Schulung')
        elif isinstance(event, WorkshopPrepDayEntry):
            mapping = self.resolution_service.resolve_for('Bayer AG',
                                                          'PM-Trainings 9-13 Bst.-Nr.: 2950100643',
                                                          'Inhouse Schulung Vor-/ Nachbereitung')
        elif isinstance(event, InternalDayEntry):
            mapping = self.resolution_service.resolve_for('it-agile GmbH', 'Vertrieb', 'Interne Arbeitszeit')
        elif isinstance(event, CustomerDayEntry):
            mapping = self.resolution_service.resolve_for('AOK Systems GmbH', 'Coach the Coaches', 'Coaching')
        elif isinstance(event, ShorttimeDayEntry):
            mapping = self.resolution_service.resolve_for('it-agile GmbH', 'Kurzarbeit', 'Interne Arbeitszeit')
        else:
            raise Exception("don't know how to map [%s]" % event)

        return ClockodoDay(start_date, end_date, event.comment, mapping)

    def json_to_logging(self, json: dict):
        if 'services_name' in json:
            service = json['services_name']
        else:
            service = json['services_id']
        return f"({service})[from={json['time_since']}, duration={json['duration_time']}, text={json['text']}]"


class ClockodoEntryService(ClockodoService):

    def __init__(self, email: str, api_key: str):
        super().__init__(email, api_key)
        self.google_calendar_service = GoogleCalendarService(GoogleCalendarServiceBuilder())
        self.day_entry_mapper = ClockodoDayMapper(ClockodoResolutionService(email, api_key))

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
        getLogger(self.__class__.__name__).info(f'inserting entry [{day_entry}]...')
        response = requests.post(self.base_url + '/entries', auth=self._get_auth(),
                                 params={'customers_id': day_entry.customer_id,
                                         'projects_id': day_entry.project_id,
                                         'billable': day_entry.billable,
                                         'services_id': day_entry.service_id,
                                         'time_since': day_entry.start_date_str,
                                         'time_until': day_entry.end_date_str,
                                         'text': day_entry.comment})

        getLogger(self.__class__.__name__).debug(response.json())
        if 'error' in response.json():
            getLogger(self.__class__.__name__).error(f'error inserting {day_entry}: {response.json()["error"]}')


def clockodo_entries_for(year: int, month: int):
    config_parser = ConfigParser()
    config_parser.read('credentials.properties')
    email = config_parser['credentials']['email']
    api_key = config_parser['credentials']['api_key']
    entry_service = ClockodoEntryService(email, api_key)
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
