from clockodo.resolution import ClockodoResolutionService


class ClockodoResolutionServiceMock(ClockodoResolutionService):
    def __init__(self):
        super().__init__("None", "None")

    def _retrieve(self, endpoint):
        endpoint_map = {
            'customers': (
                {
                    'name': 'it-agile GmbH',
                    'id': 1,
                    'billable_default': 0,
                    'projects': ({'name': 'Vertrieb', 'id': 1},)
                },
            ),
            'services': ({
                             'name': 'Interne Arbeitszeit',
                             'id': 1
                         },)
        }
        return endpoint_map[endpoint]


class MockResponse(object):

    def __init__(self, endpoint, return_json):
        self.endpoint = endpoint
        self.return_json = return_json

    def json(self):
        return self.return_json[self.endpoint]


def mocked_requests_post(*args, **kwargs):
    if args[0].startswith('https://my.clockodo.com/api/entries'):
        kwargs['id'] = 2
        return MockResponse('entries', {'entries': {'entry': kwargs}})
    else:
        raise ValueError(f'unknown url {args[0]}')


def mocked_requests_delete(*args, **kwargs):
    if args[0].startswith('https://my.clockodo.com/api/'):
        return MockResponse('/'.join(args[0].split('/')[-2:]), {'entries/1': 'success'})
    else:
        raise ValueError(f'unknown url {args[0]}')


def mocked_requests_get(*args, **kwargs):
    fixtures = {
        'users': {
            'users': ({'id': 1, 'email': 'test@here'},), },
        'customers': {
            'customers': ({'name': 'HDI', 'id': 'test_customer_id', 'billable_default': True,
                           'projects': ({'name': 'Design Sprint Bestellung 4500200459', 'id': 'test_project_id'},)},)
        },
        'services': {
            'services': ({'name': 'Workshop-Durchführung', 'id':'test_service_id'},)
        },
        'entries': {
            'entries': ({'services_name': 'Test Service',
                         'time_since': 1,
                         'time_until': 2,
                         'duration_time': 1,
                         'text': 'test',
                         'id': 1},), }
    }
    if args[0].startswith('https://my.clockodo.com/api/'):
        return MockResponse(args[0].split('/')[-1], fixtures)
    else:
        raise ValueError(f'unknown url {args[0]}')
