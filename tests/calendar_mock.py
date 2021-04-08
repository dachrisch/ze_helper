import json
from datetime import datetime
from importlib import resources

from gcal.service import GoogleCalendarServiceBuilder


class CalendarServiceMock(object):
    def __init__(self, calendar_events):
        self.calendar_events = calendar_events

    def events(self):
        return self

    def list(self, calendarId, timeMin, timeMax, singleEvents, orderBy):
        self.timeMin = datetime.fromisoformat(timeMin[0:-1]).timestamp()
        self.timeMax = datetime.fromisoformat(timeMax[0:-1]).timestamp()
        return self

    def execute(self):
        return self

    def get(self, a, b):
        return list(filter(lambda event: self.event_with_time_in_range(event) or self.event_with_date_in_range(event),
                           self.calendar_events))

    def event_with_time_in_range(self, event: dict):
        return 'dateTime' in event['start'] and self.timeMin <= datetime.fromisoformat(
            event['start']['dateTime']).timestamp() and datetime.fromisoformat(
            event['end']['dateTime']).timestamp() <= self.timeMax

    def event_with_date_in_range(self, event: dict):
        return 'date' in event['start'] and self.timeMin <= datetime.fromisoformat(
            event['start']['date']).timestamp() and datetime.fromisoformat(
            event['end']['date']).timestamp() <= self.timeMax


class GoogleCalendarServiceBuilderMock(GoogleCalendarServiceBuilder):
    def __init__(self):
        with resources.open_text('tests', 'calendar_fixture.json5') as events:
            self.calendar_events = json.load(events)

    def build(self):
        return CalendarServiceMock(self.calendar_events)
