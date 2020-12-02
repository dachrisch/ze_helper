import json
from datetime import datetime
from importlib import resources


class BrowserMock(dict):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.selected = False
        with resources.open_text('tests', 'calendar_fixture.json5') as values:
            self.submit_values = [{'username': 'cd', 'password': 'test'}]
            for value in json.load(values):
                if 'dateTime' not in value['start']:
                    continue
                self.submit_values.append({
                    'start': datetime.fromisoformat(value['start']['dateTime']).strftime('%H:%M'),
                    'ende': datetime.fromisoformat(value['end']['dateTime']).strftime('%H:%M'),
                    'tag': datetime.fromisoformat(value['start']['dateTime']).strftime('%d.%m.%Y'),
                    'kommentar': value['summary']
                })

    def set_cookiejar(self, a):
        pass

    def set_handle_robots(self, a):
        pass

    def open(self, url):
        pass

    def title(self):
        if self.counter:
            return 'Zeiterfassung - Arbeitszeiten'
        else:
            return 'Zeiterfassung - Login'

    def select_form(self, nr):
        pass

    def submit(self):
        for key, value in self.submit_values[self.counter].items():
            self.assert_submit_value(key, value)
        self.counter += 1

    def assert_submit_value(self, value: str, expected: str):
        assert expected == self[value], 'expected [%s] but was [%s]' % (expected, self[value])

    def find_control(self, a):
        return self

    def get(self, label):
        return self

    def response(self):
        return self

    def read(self):
        return b''
