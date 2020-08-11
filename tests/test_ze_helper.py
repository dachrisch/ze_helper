#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Dec 6, 2012

@author: cda
'''
import getpass
import json
import unittest
from datetime import datetime
from importlib import resources

import mechanize

from main import split_arguments
from service.gcal import GoogleCalendarServiceBuilder
from service.ze import ZE
from tests.test_calendar_service import CalendarServiceMock


class ZeHelperTest(unittest.TestCase):
    def xtest_connect_to_ze_prod(self):
        worktime = ZE().login('cd', getpass.getpass('password for [%s]: ' % 'cd'))
        worktime.enter_rowe('01.12.2012')

    def test_split_arguments_simple(self):
        arguments = split_arguments("cd@201202")
        assert 'year' in arguments.keys(), arguments.keys()
        assert 2012 == arguments['year'], arguments['year']
        assert 'month' in arguments.keys(), arguments.keys()
        assert 2 == arguments['month'], arguments['month']
        assert 'username' in arguments.keys(), arguments.keys()
        assert 'cd' == arguments['username'], arguments['username']

    def test_split_arguments_complex(self):
        arguments = split_arguments("cd@201202-05:08")
        assert 'year' in arguments.keys(), arguments.keys()
        assert 2012 == arguments['year'], arguments['year']
        assert 'month' in arguments.keys(), arguments.keys()
        assert 2 == arguments['month'], arguments['month']
        assert 'username' in arguments.keys(), arguments.keys()
        assert 'cd' == arguments['username'], arguments['username']

    def test_entries_from_gcal(self):
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

        mechanize.Browser = BrowserMock
        GoogleCalendarServiceBuilder.build = lambda x: CalendarServiceMock()
        ze = ZE()
        ze.login('cd', 'test').worktime_for(2020, 8).enter_from_gcal()


if __name__ == '__main__':
    unittest.main()
