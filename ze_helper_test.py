#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Dec 6, 2012

@author: cda
'''
import unittest
import getpass
from main import WorkTimePage, ZE

class ZeHelperTest(unittest.TestCase):
	def xtest_connect_to_ze_prod(self):
		worktime = ZE().login('cd', getpass.getpass('password for [%s]: ' % 'cd'))
		worktime.enter_rowe('01.12.2012')
	def test_iterate_weekdays(self):
		assert WorkTimePage.enumerate_workdays(2012, 12) == (3,4,5,6,7,10,11,12,13,14,17,18,19,20,21,24,25,26,27,28,31), WorkTimePage.enumerate_workdays(2012, 12)

if __name__ == '__main__':
    unittest.main()