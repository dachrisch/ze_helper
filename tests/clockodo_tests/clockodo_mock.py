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
