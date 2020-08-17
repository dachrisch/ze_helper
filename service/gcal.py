from datetime import datetime
from os import path

from google.oauth2 import service_account
from googleapiclient.discovery import build

from entity.day import DayEntry

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
        events = self._filter_vacation(events)
        events = self._split_overlapping(events)

        return events

    def _split_overlapping(self, events):
        date_counter = {}
        for event in events:
            if event.date not in date_counter:
                date_counter[event.date] = []
            date_counter[event.date].append(event)

        flattened_events = []
        for date, date_events in date_counter.items():
            flattened_events.extend(self._flatten(date_events))

        return flattened_events

    def _filter_vacation(self, events):
        return list(map(lambda event: DayEntry.from_gcal(event),
                        filter(lambda event: 'displayName' not in event['organizer'] or event['organizer'][
                            'displayName'] != 'Südsterne Abwesenheiten', events)))

    def _fetch_events_from_service(self, from_date, to_date):
        events = self.service.events().list(calendarId='primary', timeMin=from_date.isoformat() + 'Z',
                                            timeMax=to_date.isoformat() + 'Z', singleEvents=True,
                                            orderBy='startTime').execute().get('items', [])
        return events

    def _flatten(self, events: [DayEntry]):
        flattened_events = events
        if len(events) > 2:
            flattened_events = self._flatten(events[:2])
            flattened_events.extend(self._flatten(events[2:]))
        elif len(events) == 2:
            if events[0].end > events[1].start:
                before = DayEntry(events[0].date, events[0].start, events[1].start, events[0].comment, events[0].label)
                middle = events[1]
                after = DayEntry(events[0].date, events[1].end, events[0].end, events[0].comment, events[0].label)
                flattened_events = [before, middle, after]

        return flattened_events
