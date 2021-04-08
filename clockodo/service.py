import requests
from requests.auth import HTTPBasicAuth


class ResolutionError(ValueError):
    pass


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
