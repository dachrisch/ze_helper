#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Dec 6, 2012

@author: cda
'''
import calendar
import getpass
import logging
import re
from logging import getLogger, basicConfig


class WorkTimePage:
    def __init__(self, browser, year, month):
        self.browser = browser
        assert 'Zeiterfassung - Arbeitszeiten' == self.browser.title(), self.browser.title()
        self.year = year
        self.month = month

    @staticmethod
    def enumerate_workdays(year, month, from_day=1, to_day=31):
        return tuple(map(lambda day_and_weekday: day_and_weekday[0],
                         filter(lambda day_and_weekday: day_and_weekday[0] > 0 and day_and_weekday[1] not in (5, 6)
                                                        and (day_and_weekday[0] >= from_day and day_and_weekday[
                             0] <= to_day),
                                calendar.Calendar().itermonthdays2(year, month))))

    def enter_month_rowe(self, from_day, to_day):
        for day in self.enumerate_workdays(self.year, self.month, from_day, to_day):
            entry = '%02d.%02d.%04d' % (day, self.month, self.year)
            try:
                self.enter_rowe(entry)
            except Exception:
                getLogger(self.__class__.__name__).exception('skipping entry %s', entry, exc_info=True)
                raise

    def enter_rowe(self, day):
        self.enter(day, '10', '14', '---', 'Kurzarbeit (Intern)')
        self.enter(day, '14', '18', 'Vertrieb', 'laut Beschreibung (Intern)')

    def enter(self, date, start, end, comment, label='Allgemein (aufMUC-Zelle)'):
        self.browser.select_form(nr=1)
        self.browser['tag'] = date
        self.browser['start'] = start
        self.browser['ende'] = end
        self._select_control_by_label(label)
        self.browser['kommentar'] = comment

        getLogger(self.__class__.__name__).info(f'saving {label}: {date} {start} - {end}: {comment}...')
        self.browser.submit()
        self._validate_response()

    def _validate_response(self):
        response = self.browser.response().read()
        if response.find(b'errorlist') != -1:
            for line in response.split(b'\n'):
                if b'errorlist' in line:
                    getLogger(self.__class__.__name__).error(line.strip())
            raise Exception('error while saving!')

    def close_month(self):
        self.browser.select_form(action='/akzeptieren/')
        getLogger(self.__class__.__name__).info('closing month %s/%s...' % (self.month, self.year))
        self.browser.submit()
        self._validate_response()

    def _select_control_by_label(self, label):
        self.browser.find_control('taetigkeit').get(label=label).selected = True


class ZE:
    def __init__(self):
        import mechanize
        from http import cookiejar

        # Browser
        self.browser = mechanize.Browser()
        # self.browser.set_debug_http(True)

        # Cookie Jar
        cj = cookiejar.LWPCookieJar()
        self.browser.set_cookiejar(cj)
        self.browser.set_handle_robots(False)

        self.base_url = 'https://ze.it-agile.de'
        self.browser.open(self.base_url)
        assert 'Zeiterfassung - Login' == self.browser.title()

    def login(self, username, password):
        self.username = username
        self.browser.select_form(nr=0)  # check for name
        self.browser['username'] = username
        self.browser['password'] = password

        self.browser.submit()
        return self

    def worktime_for(self, year, month):
        url = '%(base)s/%(year)s/%(month)s/%(username)s' % {
            'base': self.base_url,
            'year': year,
            'month': month,
            'username': self.username
        }
        self.browser.open(url)
        return WorkTimePage(self.browser, year, month)


def main(arguments):
    username = arguments['username']
    year = arguments['year']
    month = arguments['month']
    from_day = arguments['from_day']
    to_day = arguments['to_day']

    password = getpass.getpass('password for [%s]: ' % username)
    ze = ZE().login(username, password)
    ze.worktime_for(year, month).enter_month_rowe(from_day, to_day)
    # ze.worktime_for(year, month).close_month()


def split_arguments(arguments):
    username, yearmonth = arguments.split('@')
    from_day = 1
    to_day = 31
    if '-' in yearmonth:
        yearmonth, days = yearmonth.split('-')
        from_day, to_day = map(int, days.split(':'))
    year, month = map(int, (yearmonth[:4], yearmonth[4:6]))
    return {'year': year,
            'month': month,
            'username': username,
            'from_day': from_day,
            'to_day': to_day}


def validate_arguments(arguments):
    year = arguments['year']
    month = arguments['month']
    from_day = arguments['from_day']
    to_day = arguments['to_day']
    if not ((month < 13) and (month > 0)):
        getLogger(__name__).info('invalid month: %s (1..12)' % month)
        sys.exit(1)
    if not ((year < 2100) and (year > 2000)):
        getLogger(__name__).info('invalid year: %s (2000..2100)' % year)
        sys.exit(2)
    if not ((from_day < 32) and (from_day > 0)):
        getLogger(__name__).info('invalid from_day: %s (1..31)' % from_day)
        sys.exit(1)
    if not ((to_day < 32) and (to_day > 0)):
        getLogger(__name__).info('invalid from_day: %s (1..31)' % to_day)
        sys.exit(1)
    if not (from_day <= to_day):
        getLogger(__name__).info('from_day (%s) must be before to_day (%s)' % (from_day, to_day))
        sys.exit(1)


def disable_ssl_check():
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context


if __name__ == '__main__':
    import sys

    basicConfig(level=logging.DEBUG)

    program = sys.argv[0]
    if len(sys.argv) != 2:
        getLogger(__name__).info('usage: %s user@{year}{month}[-[from_day]:[to_day]]' % program)
        sys.exit(-1)
    arguments = split_arguments(sys.argv[1])
    validate_arguments(arguments)

    disable_ssl_check()

    main(arguments)
