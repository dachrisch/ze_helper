from clockodo.connector import ClockodoApiConnector


class ClockodoApiConnectorMock(ClockodoApiConnector):
    def __init__(self):
        super().__init__('test@here', 'none')

    def api_get_all(self, endpoint):
        endpoint_map = {
            'customers': (
                {
                    'name': 'it-agile GmbH',
                    'id': 1,
                    'billable_default': 0,
                    'projects': ({'name': 'Interne Struktur und Organisation', 'id': 1},)
                }, {'name': 'AOK Systems GmbH',
                    'id': 1462125,
                    'billable_default': 1,
                    'projects': ({'name': 'Coach the Coaches PO 10528/10721', 'id': 1325527},)}
            ),
            'services': ({'name': 'Interne Arbeitszeit',
                          'id': 1},
                         {'name': 'Coaching',
                          'id': 572638}
                         )
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
            'customers': ({'name': 'it-agile GmbH', 'id': 'test_customer_id', 'billable_default': False,
                           'projects': ({'name': 'Interne Struktur und Organisation', 'id': 'test_project_id'},)},)
        },
        'services': {
            'services': ({'name': 'Interne Arbeitszeit', 'id': 'test_service_id'},
                         {'name': 'AOK Systems GmbH', 'id': 'test_service_id'})
        },
        'entries': {
            'entries': [{'services_name': 'Test Service',
                         'time_since': '2021-02-01 10:30:00',
                         'time_until': '2021-02-01 13:00:00',
                         'customers_id': 'test_customer_id',
                         'projects_id': 'test_project_id',
                         'services_id': 'test_services_id',
                         'billable': 1,
                         'duration_time': 1,
                         'text': 'test',
                         'lumpSum': None,
                         'id': 1},
                        {'services_name': 'Test Service',
                         'time_since': '2021-02-01 10:30:00',
                         'time_until': '2021-02-01 13:00:00',
                         'customers_id': 'test_customer_id',
                         'projects_id': 'test_project_id',
                         'services_id': 'test_services_id',
                         'billable': 1,
                         'duration_time': 1,
                         'text': 'test',
                         'lumpSum': 2000,
                         'id': 1}
                        ], },
        'project': {},
        '1462125': {'project': {'id': 1462125, 'customers_id': 1345, 'name': 'Test Project'}}
    }
    if args[0].startswith('https://my.clockodo.com/api/'):
        return MockResponse(args[0].split('/')[-1], fixtures)
    else:
        raise ValueError(f'unknown url {args[0]}')
