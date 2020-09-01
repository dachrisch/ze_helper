import calendar
from datetime import datetime
from logging import getLogger

from mechanize import FormNotFoundError

from entity.day import DayEntry
from service.gcal import GoogleCalendarServiceBuilder, GoogleCalendarService


class WorkTimePage:
    def __init__(self, browser, year, month):
        self.browser = browser
        assert 'Zeiterfassung - Arbeitszeiten' == self.browser.title(), self.browser.title()
        self.year = year
        self.month = month
        self.google_calendar_service = GoogleCalendarService(GoogleCalendarServiceBuilder())

    def enter_from_gcal(self):
        getLogger(self.__class__.__name__).info('creating day entries from gcal...')
        first_day = datetime(self.year, self.month, 1)
        last_day = datetime(self.year, self.month, calendar.monthrange(self.year, self.month)[1])
        for event in self.google_calendar_service.events_in_range(first_day, last_day):
            self.enter(event)

    def enter(self, event: DayEntry):
        self.browser.select_form(nr=1)
        self.browser['tag'] = event.date
        self.browser['start'] = event.start
        self.browser['ende'] = event.end
        self._select_control_by_label(event.label)
        self.browser['kommentar'] = event.comment[:100]

        getLogger(self.__class__.__name__).info(
            f'saving {event.label}: {event.date} {event.start} - {event.end}: {event.comment}...')
        self.browser.submit()
        self._validate_response()

    def delete_entries(self):
        getLogger(self.__class__.__name__).info('cleaning up existing entries...')

        def is_delete_form(form):
            return 'action' in form.attrs and '/loeschen/' in form.attrs['action']

        try:
            while True:
                self.browser.select_form(predicate=is_delete_form)

                getLogger(self.__class__.__name__).info(
                    f'deleting {self.browser.form.controls[0]}...')

                self.browser.submit()
        except FormNotFoundError:
            # everything deleted
            pass

    def _validate_response(self):
        response = self.browser.response().read()
        if response.find(b'errorlist') != -1:
            for line in response.split(b'\n'):
                if b'errorlist' in line:
                    getLogger(self.__class__.__name__).error(line.strip())
            raise Exception('error while saving!')

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
