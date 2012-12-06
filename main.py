#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Dec 6, 2012

@author: cda
'''
import calendar
import getpass

class WorkTimePage:
	def __init__(self, browser):
		self.browser = browser
		assert 'Zeiterfassung - Arbeitszeiten' == self.browser.title()

	@staticmethod
	def enumerate_workdays(year, month):
		return tuple(map(lambda day_and_weekday: day_and_weekday[0], 
						filter(lambda day_and_weekday: day_and_weekday[0] > 0 and day_and_weekday[1] not in (5, 6), 
						calendar.Calendar().itermonthdays2(year, month))))

	def enter_complete_month_rowe(self, year, month):
		for day in self.enumerate_workdays(year, month):
			self.enter_rowe('%02d.%02d.%04d' % (day, month, year))
	def enter_rowe(self, day):
		self.enter(day, '9', '17', 'ROWE')
	def enter(self, date, start, end, comment):
		self.browser.select_form(nr = 1)
		self.browser['tag'] = date
		self.browser['start'] = start
		self.browser['ende'] = end
		self.browser.find_control('taetigkeit').items[7].selected = True # different !
		self.browser['kommentar'] = comment
		print 'saving %(tag)s %(start)s - %(ende)s: %(kommentar)s...' % self.browser
		self.browser.submit()
		assert self.browser.response().read().find('wurde gespeichert') != -1


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
		self.browser.select_form(nr = 0) # check for name
		self.browser['username'] = username
		self.browser['password'] = password

		self.browser.submit()
		return WorkTimePage(self.browser)


def main():
	username = 'cd'
	password = getpass.getpass('password for [%s]: ' % username)
	worktime = ZE().login(username, password)
	worktime.enter_complete_month_rowe(2012, 12)

if __name__ == '__main__':
	main()