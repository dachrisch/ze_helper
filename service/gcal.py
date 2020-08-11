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
        events = self.service.events().list(calendarId='primary', timeMin=from_date.isoformat() + 'Z',
                                            timeMax=to_date.isoformat() + 'Z', singleEvents=True,
                                            orderBy='startTime').execute().get('items', [])

        return list(map(lambda event: DayEntry.from_gcal(event),
                        filter(lambda event: 'displayName' not in event['organizer'] or event['organizer'][
                            'displayName'] != 'Südsterne Abwesenheiten', events)))
