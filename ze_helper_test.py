#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Dec 6, 2012

@author: cda
'''
import unittest
import getpass
from main import WorkTimePage, ZE, split_arguments

class ZeHelperTest(unittest.TestCase):
	def xtest_connect_to_ze_prod(self):
		worktime = ZE().login('cd', getpass.getpass('password for [%s]: ' % 'cd'))
		worktime.enter_rowe('01.12.2012')
	def test_iterate_weekdays(self):
		assert WorkTimePage.enumerate_workdays(2012, 12) == (3,4,5,6,7,10,11,12,13,14,17,18,19,20,21,24,25,26,27,28,31), WorkTimePage.enumerate_workdays(2012, 12)
	def test_selective_days(self):
		assert WorkTimePage.enumerate_workdays(2012, 12, 7, 25) == (7,10,11,12,13,14,17,18,19,20,21,24,25), WorkTimePage.enumerate_workdays(2012, 12, 7, 25)
	def test_split_arguments_simple(self):
		arguments = split_arguments("cd@201202")
		assert 'year' in arguments.keys(), arguments.keys()
		assert 2012 == arguments['year'], arguments['year']
		assert 'month' in arguments.keys(), arguments.keys()
		assert 02 == arguments['month'], arguments['month']
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
		assert 'from_day' in arguments.keys(), arguments.keys()
		assert 5 == arguments['from_day'], arguments['from_day']
		assert 'to_day' in arguments.keys(), arguments.keys()
		assert 8 == arguments['to_day'], arguments['to_day']

if __name__ == '__main__':
    unittest.main()