from functools import lru_cache

import requests

from clockodo.entity import ClockodoIdMapping
from clockodo.service import ClockodoService, ResolutionError


class ClockodoResolutionService(ClockodoService):
    def __init__(self, email: str, api_key: str):
        super().__init__(email, api_key)

    def resolve_for(self, customer_name: str, project_name: str, service_name: str) -> ClockodoIdMapping:
        resolved_customer = next(
            filter(lambda customer: customer['name'] == customer_name, self._retrieve('customers')),
            None)
        if not resolved_customer:
            raise ResolutionError(f'no mapping found for customer [{customer_name}]')
        customer_id = resolved_customer['id']
        billable = 1 if resolved_customer['billable_default'] else 0
        project_id = next(filter(lambda project: project['name'] == project_name, resolved_customer['projects']),
                          {'id': 0})['id']
        if not project_id:
            raise ResolutionError(f'no mapping found for project [{project_name}]')
        service_id = next(filter(lambda service: service['name'] == service_name, self._retrieve('services')),
                          {'id': 0})['id']
        if not service_id:
            raise ResolutionError(f'no mapping found for service [{service_name}]')
        return ClockodoIdMapping(customer_id, project_id, service_id, billable)

    @lru_cache(128)
    def _retrieve(self, endpoint):
        return requests.get(self.base_url + f'/{endpoint}', auth=self._get_auth()).json()[endpoint]
