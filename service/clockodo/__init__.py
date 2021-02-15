from functools import lru_cache
from logging import getLogger

import requests
from requests.auth import HTTPBasicAuth

from service.clockodo.credentials import CredentialsProvider
from service.clockodo.day import ClockodoDay


class ClockodoService(object):
    base_url = 'https://my.clockodo.com/api'

    def __init__(self, credentials_provider: CredentialsProvider):
        self.credentials_provider = credentials_provider

    def _get_auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.credentials_provider.email, self.credentials_provider.api_key)

    def _get_user_id(self) -> str:
        users = requests.get(self.base_url + '/users', auth=self._get_auth()).json()['users']
        user_id = list(filter(lambda x: x['email'] == self.credentials_provider.email, users))[0]['id']
        return user_id

    def current_entries(self, first_day, last_day):
        current_entries = requests.get(self.base_url + '/entries', auth=self._get_auth(),
                                       params={'time_since': first_day.strftime('%Y-%m-%d %H:%M:%S'),
                                               'time_until': last_day.strftime('%Y-%m-%d %H:%M:%S'),
                                               'filter[users_id]': self._get_user_id()}).json()['entries']
        return current_entries

    def delete(self, entry: dict):
        response = requests.delete(self.base_url + '/entries/%s' % entry['id'], auth=self._get_auth())
        assert response.json()['success'] is True, response.json()

    def enter(self, day_entry: ClockodoDay):
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

    @lru_cache(128)
    def retrieve(self, endpoint):
        return requests.get(self.base_url + f'/{endpoint}', auth=self._get_auth()).json()[endpoint]
