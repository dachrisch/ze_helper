import posixpath
from functools import lru_cache
from logging import getLogger
from typing import Dict, Any, List

import requests
from requests.auth import HTTPBasicAuth


class ResolutionError(ValueError):
    pass


class ClockodoApiConnector(object):
    base_url = 'https://my.clockodo.com/api'

    def __init__(self, email: str, api_key: str):
        self.email = email
        self.api_key = api_key

    def _get_auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.email, self.api_key)

    def _get_user_id(self) -> str:
        user_id = list(filter(lambda x: x['email'] == self.email, self.api_get_all('users')))[0]['id']
        return user_id

    @lru_cache(128)
    def api_get_all(self, endpoint: str):
        return requests.get(posixpath.join(self.base_url, endpoint), auth=self._get_auth()).json()[endpoint]

    def api_get(self, endpoint: str, resource_id: int):
        return requests.get(posixpath.join(self.base_url, endpoint, str(resource_id)), auth=self._get_auth()).json()

    def api_find(self, endpoint: str, params: Dict) -> List[Dict]:
        params_copy = params.copy()
        params_copy['filter[users_id]'] = self._get_user_id()
        return requests.get(posixpath.join(self.base_url, endpoint), auth=self._get_auth(), params=params_copy).json()[
            endpoint]

    def api_delete(self, endpoint: str, resource_id: int):
        response = requests.delete(posixpath.join(self.base_url, endpoint, str(resource_id)), auth=self._get_auth())
        getLogger(self.__class__.__name__).debug(response.json())
        assert 'success' in response.json(), response.json()

    def api_post_entry(self, params: Dict[str, Any]):
        response = requests.post(posixpath.join(self.base_url, 'entries'), auth=self._get_auth(),
                                 params={'customers_id': params['customers_id'],
                                         'projects_id': params['projects_id'],
                                         'billable': params['billable'],
                                         'services_id': params['services_id'],
                                         'time_since': params['time_since'],
                                         'time_until': params['time_until'],
                                         'text': params['text']})
        getLogger(self.__class__.__name__).debug(response.json())
        assert 'entry' in response.json(), response.json()
        return response.json()['entry']
