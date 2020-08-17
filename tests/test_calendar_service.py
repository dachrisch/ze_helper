import json
import unittest
from datetime import datetime
from importlib import resources

from entity.day import DayEntry
from service.gcal import GoogleCalendarService, GoogleCalendarServiceBuilder


class CalendarServiceMock(object):
    def events(self):
        return self

    def list(self, calendarId, timeMin, timeMax, singleEvents, orderBy):
        self.timeMin = datetime.fromisoformat(timeMin[0:-1]).timestamp()
        self.timeMax = datetime.fromisoformat(timeMax[0:-1]).timestamp()
        return self

    def execute(self):
        return self

    def get(self, a, b):
        with resources.open_text('tests', 'calendar_fixture.json5') as events:
            json_load = json.load(events)
            return filter(lambda event: 'dateTime' in event['start'] and self.timeMin <= datetime.fromisoformat(
                event['start']['dateTime']).timestamp() and datetime.fromisoformat(
                event['end']['dateTime']).timestamp() <= self.timeMax,
                          json_load)


class GoogleCalendarServiceBuilderMock(GoogleCalendarServiceBuilder):
    def build(self):
        return CalendarServiceMock()


class CalendarServiceTest(unittest.TestCase):
    def test_calendar_service(self):
        calendar_service = GoogleCalendarService(GoogleCalendarServiceBuilderMock())
        events = calendar_service.events_in_range(datetime(2020, 8, 1), datetime(2020, 8, 31))

        self.assertEqual(len(events), 24)

        self.assertIsInstance(events[0], DayEntry)

        self.assertEqual('03.08.2020', events[0].date)
        self.assertEqual('09:45', events[0].start)
        self.assertEqual('11:45', events[0].end)
        self.assertEqual('[Kunde] "Online-Meeting-Moderation"-Aufbau vom 03. - 07. August 2020', events[0].comment)
        self.assertEqual('Laut Beschreibung & fakturierbar (Extern)', events[0].label)

        self.assertIsInstance(events[1], DayEntry)

        self.assertEqual('03.08.2020', events[1].date)
        self.assertEqual('12:00', events[1].start)
        self.assertEqual('18:00', events[1].end)
        self.assertEqual('Büroumzug', events[1].comment)
        self.assertEqual('laut Beschreibung (Intern)', events[1].label)

    def test_kurzarbeit_label(self):
        calendar_service = GoogleCalendarService(GoogleCalendarServiceBuilderMock())
        events = calendar_service.events_in_range(datetime(2020, 8, 31), datetime(2020, 8, 31))
        self.assertEqual(len(events), 1)

        self.assertIsInstance(events[0], DayEntry)

        self.assertEqual('31.08.2020', events[0].date)
        self.assertEqual('10:00', events[0].start)
        self.assertEqual('16:00', events[0].end)
        self.assertEqual('Kurzarbeit', events[0].comment)
        self.assertEqual('Kurzarbeit (Intern)', events[0].label)

    def test_overlapping_is_split(self):
        calendar_service = GoogleCalendarService(GoogleCalendarServiceBuilderMock())
        events = calendar_service.events_in_range(datetime(2020, 8, 29), datetime(2020, 8, 29))
        self.assertEqual(len(events), 3)

        self.assertEqual('29.08.2020', events[0].date)
        self.assertEqual('10:00', events[0].start)
        self.assertEqual('12:00', events[0].end)
        self.assertEqual('Overlapping-Kurzarbeit', events[0].comment)
        self.assertEqual('laut Beschreibung (Intern)', events[0].label)

        self.assertEqual('29.08.2020', events[1].date)
        self.assertEqual('12:00', events[1].start)
        self.assertEqual('14:00', events[1].end)
        self.assertEqual('Overlapping-Work', events[1].comment)
        self.assertEqual('laut Beschreibung (Intern)', events[1].label)

        self.assertEqual('29.08.2020', events[2].date)
        self.assertEqual('14:00', events[2].start)
        self.assertEqual('16:00', events[2].end)
        self.assertEqual('Overlapping-Kurzarbeit', events[2].comment)
        self.assertEqual('laut Beschreibung (Intern)', events[2].label)

if __name__ == '__main__':
    unittest.main()
