import json
from unittest import TestCase

from dependency_injector import providers

from service.clockodo import ClockodoService
from service.clockodo.inject import Services, Google, Clockodo
from tests.calendar_mock import CalendarServiceMock


class TestClockodoMapping(TestCase):
    def test_map_from_entry(self):
        events = (json.loads("""{
    "kind": "calendar#event",
    "summary": "\\"Online-Meeting-Moderation\\"-Aufbau vom 03. - 07. August 2020",
    "colorId": "4",
    "start": {
      "dateTime": "2020-08-03T09:45:00+02:00"
    },
    "end": {
      "dateTime": "2020-08-03T11:45:00+02:00"
    },
    "organizer": {
      "displayName": "Christian Dähn"
    }
  }
"""),)
        service = ClockodoService(None)
        service.retrieve = lambda x: ['bla', ]
        Clockodo.clockodo_service.override(service)
        Google.google_calendar_service.override(providers.Factory(CalendarServiceMock, calendar_events=events))
        Services.entry_service().enter_events_from_gcal(2020, 8)
