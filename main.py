#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Dec 6, 2012

@author: cda
'''
import getpass
import logging
from logging import getLogger, basicConfig

from service.ze import ZE


def main(arguments):
    username = arguments['username']
    year = arguments['year']
    month = arguments['month']

    password = getpass.getpass('password for [%s]: ' % username)
    ze = ZE().login(username, password)
    ze.worktime_for(year, month).enter_from_gcal()


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
            'username': username}


def validate_arguments(arguments):
    year = arguments['year']
    month = arguments['month']
    if not ((month < 13) and (month > 0)):
        getLogger(__name__).info('invalid month: %s (1..12)' % month)
        sys.exit(1)
    if not ((year < 2100) and (year > 2000)):
        getLogger(__name__).info('invalid year: %s (2000..2100)' % year)
        sys.exit(2)


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
