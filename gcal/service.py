import io
from calendar import monthrange
from datetime import datetime
from os import path
from typing import Dict

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from gcal.entity import CalendarEvent
from gcal.mapper import CalendarEventMapper
from gcal.processor import WholeMonthProcessor

RW_SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarServiceBuilder(object):
    @classmethod
    def build(cls):
        credentials_dir = path.join(path.expanduser('~'), '.credentials')
        credentials_store = path.join(credentials_dir, 'store.json')

        if path.isfile(credentials_store):
            credentials = Credentials.from_authorized_user_file(credentials_store)
        else:
            client_secret_file = path.join(credentials_dir, 'client_secret.json')
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes=RW_SCOPES)
            credentials = flow.run_local_server()
            with io.open(credentials_store, 'w', encoding="utf-8") as json_file:
                json_file.write(credentials.to_json_str())
        return build('calendar', 'v3', credentials=credentials, cache_discovery=False)


class GoogleCalendarService(object):
    def __init__(self, service_builder: GoogleCalendarServiceBuilder):
        self.service = service_builder.build()

    def fetch_events_from_service(self, from_date: datetime, to_date: datetime) -> Dict:
        events = self.service.events().list(calendarId='primary', timeMin=from_date.isoformat() + 'Z',
                                            timeMax=to_date.isoformat() + 'Z', singleEvents=True,
                                            orderBy='startTime').execute().get('items', [])
        return events


class GoogleCalendarEventProcessor(object):
    def __init__(self, google_service: GoogleCalendarService, mapper: CalendarEventMapper,
                 processor: WholeMonthProcessor):
        self.mapper = mapper
        self.processor = processor
        self.google_service = google_service

    def calendar_events_in_month(self, year: int, month: int) -> [CalendarEvent]:
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)
        return self.processor.process(
            self.mapper.to_calendar_events(self.google_service.fetch_events_from_service(first_day, last_day)))
