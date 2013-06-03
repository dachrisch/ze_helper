#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Dec 6, 2012

@author: cda
'''
import calendar
import getpass
import sys

class WorkTimePage:
	def __init__(self, browser, year, month):
		self.browser = browser
		assert 'Zeiterfassung - Arbeitszeiten' == self.browser.title(), self.browser.title()
		self.year = year
		self.month = month

	@staticmethod
	def enumerate_workdays(year, month):
		return tuple(map(lambda day_and_weekday: day_and_weekday[0], 
						filter(lambda day_and_weekday: day_and_weekday[0] > 0 and day_and_weekday[1] not in (5, 6), 
						calendar.Calendar().itermonthdays2(year, month))))

	def enter_complete_month_rowe(self):
		for day in self.enumerate_workdays(self.year, self.month):
			self.enter_rowe('%02d.%02d.%04d' % (day, self.month, self.year))
	def enter_rowe(self, day):
		self.enter(day, '9', '17', 'ROWE')
	def enter(self, date, start, end, comment):
		self.browser.select_form(nr = 1)
		self.browser['tag'] = date
		self.browser['start'] = start
		self.browser['ende'] = end
		self._select_control_by_label('Allgemein (Team 101)')
		self.browser['kommentar'] = comment
		print 'saving %(tag)s %(start)s - %(ende)s: %(kommentar)s...' % self.browser
		self.browser.submit()
		response = self.browser.response().read()
		if response.find('errorlist') != -1:
			for line in response.split('\n'):
				if 'errorlist' in line:
					print >> sys.stderr, line.strip()
			raise Exception('error while saving!')

	def _select_control_by_label(self, label):
		self.browser.find_control('taetigkeit').get(label = 'Allgemein (Team 101)').selected = True

class ZE:
	def __init__(self):
		import mechanize
		import cookielib

		# Browser
		self.browser = mechanize.Browser()
		# self.browser.set_debug_http(True)

		# Cookie Jar
		cj = cookielib.LWPCookieJar()
		self.browser.set_cookiejar(cj)
		self.browser.set_handle_robots(False)

		self.base_url = 'https://ze.it-agile.de'
		self.browser.open(self.base_url)
		assert 'Zeiterfassung - Login' == self.browser.title()
	def login(self, username, password):
		self.username = username
		self.browser.select_form(nr = 0) # check for name
		self.browser['username'] = username
		self.browser['password'] = password

		self.browser.submit()
		return self
	def worktime_for(self, year, month):
		url = '%(base)s/%(year)s/%(month)s/%(username)s' % {
																'base' : self.base_url,
																'year' : year,
																'month' : month,
																'username' : self.username
																}
		self.browser.open(url)
		return WorkTimePage(self.browser, year, month)


def main():
	username = 'cd'
	password = getpass.getpass('password for [%s]: ' % username)
	worktime = ZE().login(username, password).worktime_for(2013, 05)
	worktime.enter_complete_month_rowe()

if __name__ == '__main__':
	main()
