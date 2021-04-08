import calendar
from datetime import datetime
from logging import getLogger

import requests

from clockodo.mapper import ClockodoDayMapper
from clockodo.service import ClockodoService
from gcal.entity import DayEntry
from gcal.service import GoogleDayEntryService


class ClockodoEntryService(ClockodoService):

    def __init__(self, email: str, api_key: str, entry_processor: GoogleDayEntryService,
                 day_entry_mapper: ClockodoDayMapper):
        super().__init__(email, api_key)
        self.entry_processor = entry_processor

        self.day_entry_mapper = day_entry_mapper

    def delete_entries(self, year: int, month: int):
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

        current_entries = self._current_entries(first_day, last_day)
        for entry in current_entries:
            self._delete(entry)

    def enter_events_from_gcal(self, year, month):
        for event in self.entry_processor.day_entries_in_month(year, month):
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
        assert 'success' in response.json(), response.json()

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
