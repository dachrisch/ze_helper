#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Dec 6, 2012

@author: cda
'''
import json
import unittest
from importlib import resources

import mechanize

from main import split_arguments
from service.gcal import GoogleCalendarServiceBuilder
from service.ze import ZeEntryService
from tests.browser_mock import BrowserMock
from tests.calendar_mock import CalendarServiceMock


class ZeHelperTest(unittest.TestCase):

    def test_split_arguments_simple(self):
        arguments = split_arguments("cd@201202")
        self.assertIn('year', arguments.keys())
        self.assertEqual(2012, arguments['year'])
        self.assertIn('month', arguments.keys())
        self.assertEqual(2, arguments['month'])
        self.assertIn('username', arguments.keys())
        self.assertEqual('cd', arguments['username'])

    def test_entries_from_gcal(self):
        mechanize.Browser = BrowserMock
        with resources.open_text('tests', 'calendar_fixture.json5') as events:
            json_load = json.load(events)
            mock = CalendarServiceMock(json_load)
        GoogleCalendarServiceBuilder.build = lambda x: mock
        ze = ZeEntryService()
        ze.browser.submit_values[22] = {'start': '10:00', 'ende': '12:00', 'tag': '29.08.2020',
                                        'kommentar': 'Overlapping-Kurzarbeit'}
        ze.browser.submit_values[23] = {'start': '12:00', 'ende': '14:00', 'tag': '29.08.2020',
                                        'kommentar': 'Overlapping-Work'}
        ze.browser.submit_values.append({'start': '14:00', 'ende': '16:00', 'tag': '29.08.2020',
                                         'kommentar': 'Overlapping-Kurzarbeit'})
        ze.login('cd', 'test').enter_from_gcal(2020, 8)


if __name__ == '__main__':
    unittest.main()
