import json
from datetime import datetime
from importlib import resources

from gcal.service import GoogleCalendarServiceBuilder


class CalendarServiceListMock(object):

    def __init__(self, calendar_events, timeMin, timeMax):
        self.timeMax = timeMax
        self.timeMin = timeMin
        self.calendar_events = calendar_events

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


class CalendarServiceGetMock:
    def __init__(self, event):
        self.event = event

    def execute(self):
        return self.event


class CalendarServiceUpdateMock:
    def __init__(self, event:dict, body:dict):
        self.body = body
        self.event = event

    def execute(self):
        self.event.update(self.body)


class CalendarServiceMock(object):
    def __init__(self, calendar_events):
        self.calendar_events = calendar_events

    def events(self):
        return self

    def list(self, calendarId, timeMin, timeMax, singleEvents, orderBy):
        return CalendarServiceListMock(self.calendar_events, datetime.fromisoformat(timeMin[0:-1]).timestamp(),
                                       datetime.fromisoformat(timeMax[0:-1]).timestamp())


    def _event_by_id(self, eventId):
        return next(filter(lambda event: event['id'] == eventId, self.calendar_events), {})

    def patch(self, calendarId, eventId, body):
        return CalendarServiceUpdateMock(self._event_by_id(eventId), body)


class GoogleCalendarServiceBuilderMock(GoogleCalendarServiceBuilder):
    @classmethod
    def from_fixture(cls, fixture='calendar_fixture.json5'):
        with resources.open_text('tests', fixture) as events:
            calendar_events = json.load(events)
        return cls(calendar_events)

    def __init__(self, calendar_events):
        self.calendar_events = calendar_events

    def build(self):
        return CalendarServiceMock(self.calendar_events)
