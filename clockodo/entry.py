import calendar
from copy import deepcopy
from datetime import datetime
from logging import getLogger
from typing import Dict, List

from clockodo.connector import ClockodoApiConnector
from clockodo.entity import ClockodoDay
from shared.persistence import PersistenceMapping


class ClockodoEntryService(object):
    def __init__(self, api_connector: ClockodoApiConnector):
        self.api_connector = api_connector

    def delete_entries(self, year: int, month: int):
        for entry in self.current_entries(year, month):
            self._delete(entry)

    def enter_calendar_events(self, clockodo_days: [ClockodoDay]):
        return tuple(map(lambda clockodo_day: self.enter(clockodo_day), clockodo_days))

    def current_entries(self, year: int, month: int) -> List[Dict]:
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
        all_entries = self.api_connector.api_find('entries', {'time_since': first_day.strftime('%Y-%m-%d %H:%M:%S'),
                                                              'time_until': last_day.strftime('%Y-%m-%d %H:%M:%S')})
        current_entries = self.filter_no_lumpsum(all_entries)
        return current_entries

    def filter_no_lumpsum(self, entries:List[Dict]) -> List[Dict]:
        return list(filter(lambda entry: entry['lumpSum'] == None, entries))

    def _delete(self, entry: Dict):
        getLogger(self.__class__.__name__).info(f'deleting entry [{self._entry_fields_to_string(entry)}]...')
        self.api_connector.api_delete('entries', entry['id'])

    @staticmethod
    def _entry_fields_to_string(entry) -> str:
        return f"{entry['services_name']}(from='{entry['time_since']}', to='{entry['time_until']}', text='{entry['text']}')"

    def enter(self, clockodo_day: ClockodoDay) -> ClockodoDay:
        getLogger(self.__class__.__name__).info(f'inserting entry [{clockodo_day}]...')
        posted_entry = self.api_connector.api_post_entry({'customers_id': clockodo_day.customer_id,
                                                          'projects_id': clockodo_day.project_id,
                                                          'billable': clockodo_day.billable,
                                                          'services_id': clockodo_day.service_id,
                                                          'time_since': clockodo_day.start_date_str,
                                                          'time_until': clockodo_day.end_date_str,
                                                          'text': clockodo_day.comment})

        assert 'id' in posted_entry, posted_entry
        persistent_clockodo_day = deepcopy(clockodo_day)
        persistent_clockodo_day.update_persistence_mapping(PersistenceMapping(posted_entry['id']))

        return persistent_clockodo_day
