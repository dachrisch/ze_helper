#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Dec 6, 2012

@author: cda
"""
import getpass
import logging
from logging import getLogger, basicConfig

from service.ze import ZE


def main(args):
    username = args['username']
    year = args['year']
    month = args['month']

    getLogger(__name__).info('creating ZE entries in %02d.%04d' % (month, year))
    password = getpass.getpass('password for [%s]: ' % username)
    ze = ZE().login(username, password)
    worktime_page = ze.worktime_for(year, month)
    worktime_page.delete_entries()
    worktime_page.enter_from_gcal()


def split_arguments(args):
    username, yearmonth = args.split('@')
    year, month = map(int, (yearmonth[:4], yearmonth[4:6]))
    return {'year': year,
            'month': month,
            'username': username}


def validate_arguments(args):
    year = args['year']
    month = args['month']
    if not ((month < 13) and (month > 0)):
        getLogger(__name__).error('invalid month: %s (1..12)' % month)
        sys.exit(1)
    if not ((year < 2100) and (year > 2000)):
        getLogger(__name__).error('invalid year: %s (2000..2100)' % year)
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

    basicConfig(level=logging.INFO)

    program = sys.argv[0]
    if len(sys.argv) != 2:
        getLogger(__name__).info('usage: %s user@{year}{month}[-[from_day]:[to_day]]' % program)
        sys.exit(-1)
    arguments = split_arguments(sys.argv[1])
    validate_arguments(arguments)

    disable_ssl_check()

    main(arguments)
