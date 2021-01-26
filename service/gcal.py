from datetime import datetime
from os import path

from google.oauth2 import service_account
from googleapiclient.discovery import build

from entity.day import DayEntry
from entity.filter import filter_vacations, filter_breaks
from entity.splitting import split_overlapping

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendarServiceBuilder(object):
    @classmethod
    def build(cls):
        credentials = service_account.Credentials.from_service_account_file(
            path.join(path.join(path.expanduser('~'), '.credentials'), 'suedsterne-1328.json'),
            scopes=SCOPES).with_subject('cd@it-agile.de')

        return build('calendar', 'v3', credentials=credentials, cache_discovery=False)


class GoogleCalendarService(object):
    def __init__(self, service_builder: GoogleCalendarServiceBuilder):
        self.service = service_builder.build()

    def events_in_range(self, from_date: datetime, to_date: datetime) -> [DayEntry]:
        if to_date.hour == 0:
            to_date = to_date.replace(hour=23, minute=59, second=59)
        events = self._fetch_events_from_service(from_date, to_date)
        day_entries = self._to_day_entries(events)
        day_entries = filter_vacations(day_entries)
        day_entries = split_overlapping(day_entries)
        day_entries = filter_breaks(day_entries)
        return day_entries

    def _to_day_entries(self, events):
        return list(map(lambda event: DayEntry.from_gcal(event), events))

    def _fetch_events_from_service(self, from_date, to_date):
        events = self.service.events().list(calendarId='primary', timeMin=from_date.isoformat() + 'Z',
                                            timeMax=to_date.isoformat() + 'Z', singleEvents=True,
                                            orderBy='startTime').execute().get('items', [])
        return events
