import calendar
from datetime import datetime
from logging import getLogger

import requests

from clockodo.entity import ClockodoDay
from clockodo.service import ClockodoService


class ClockodoEntryService(ClockodoService):

    def delete_entries(self, year: int, month: int):
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

        current_entries = self._current_entries(first_day, last_day)
        for entry in current_entries:
            self._delete(entry)

    def enter_calendar_events(self, clockodo_days: [ClockodoDay]):
        for clockodo_day in clockodo_days:
            self._enter(clockodo_day)

    def _current_entries(self, first_day, last_day):
        current_entries = requests.get(self.base_url + '/entries', auth=self._get_auth(),
                                       params={'time_since': first_day.strftime('%Y-%m-%d %H:%M:%S'),
                                               'time_until': last_day.strftime('%Y-%m-%d %H:%M:%S'),
                                               'filter[users_id]': self._get_user_id()}).json()['entries']
        return current_entries

    def _delete(self, entry: dict):
        getLogger(self.__class__.__name__).info(f'deleting entry [{self._entry_fields_to_string(entry)}]...')
        response = requests.delete(self.base_url + '/entries/%s' % entry['id'], auth=self._get_auth())
        assert 'success' in response.json(), response.json()

    @staticmethod
    def _entry_fields_to_string(entry):
        return f"{entry['services_name']}(from='{entry['time_since']}', to='{entry['time_until']}', text='{entry['text']}')"

    def _enter(self, clockodo_day: ClockodoDay):
        getLogger(self.__class__.__name__).info(f'inserting entry [{clockodo_day}]...')
        response = requests.post(self.base_url + '/entries', auth=self._get_auth(),
                                 params={'customers_id': clockodo_day.customer_id,
                                         'projects_id': clockodo_day.project_id,
                                         'billable': clockodo_day.billable,
                                         'services_id': clockodo_day.service_id,
                                         'time_since': clockodo_day.start_date_str,
                                         'time_until': clockodo_day.end_date_str,
                                         'text': clockodo_day.comment})

        getLogger(self.__class__.__name__).debug(response.json())
        if 'error' in response.json():
            getLogger(self.__class__.__name__).error(f'error inserting {clockodo_day}: {response.json()["error"]}')
