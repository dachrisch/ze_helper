import calendar
from datetime import datetime
from logging import getLogger

from mechanize import FormNotFoundError

from entity.day import DayEntry
from service.gcal import GoogleCalendarServiceBuilder, GoogleCalendarService


class ZeDayEntry(object):
    def __init__(self, day_entry: DayEntry):
        self.date = day_entry.date
        self.start = day_entry.start
        self.end = day_entry.end
        self.comment = day_entry.comment
        self.label = day_entry.label


class ZeDayMapper(object):
    def to_ze_day(self, day_entry: DayEntry):
        return ZeDayEntry(day_entry)


class WorkTimePage:
    def __init__(self, browser):
        self.browser = browser
        assert 'Zeiterfassung - Arbeitszeiten' == self.browser.title(), self.browser.title()

    def enter(self, event: ZeDayEntry):
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


class ZeEntryService:
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
        self.day_mapper = ZeDayMapper()
        self.google_calendar_service = GoogleCalendarService(GoogleCalendarServiceBuilder())

    def login(self, username, password):
        self.username = username
        self.browser.select_form(nr=0)  # check for name
        self.browser['username'] = username
        self.browser['password'] = password

        self.browser.submit()
        return self

    def _worktime_for(self, year, month):
        url = '%(base)s/%(year)s/%(month)s/%(username)s' % {
            'base': self.base_url,
            'year': year,
            'month': month,
            'username': self.username
        }
        self.browser.open(url)
        return WorkTimePage(self.browser)

    def enter_from_gcal(self, year, month):
        getLogger(self.__class__.__name__).info('creating day entries from gcal...')
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1])

        worktime_page = self._worktime_for(year, month)
        for event in self.google_calendar_service.events_in_range(first_day, last_day):
            worktime_page.enter(self.day_mapper.to_ze_day(event))

    def delete_entries(self, year, month):
        self._worktime_for(year, month).delete_entries()
