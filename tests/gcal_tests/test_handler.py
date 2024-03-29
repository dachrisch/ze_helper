import json
import unittest
from datetime import datetime, timezone, timedelta

from gcal.handler import HourlyCalendarEventHandler, DailyCalendarEventHandler, GCalHandlingException
from gcal.mapper import CalendarEventMapper


class CalendarJsonEntryFixtures(object):
    def __init__(self):
        self.hourly_json_entry = json.loads("""{
            "kind": "calendar#event",
            "id": "c1cq8kmuvisglepf374hkc1dfg_20200803T074500Z",
            "summary": "\\"Online-Meeting-Moderation\\"-Aufbau vom 03. - 07. August 2020",
            "colorId": "4",
            "start": {
              "dateTime": "2020-08-03T09:45:00+02:00"
            },
            "end": {
              "dateTime": "2020-08-03T11:45:00+02:00"
            },
            "description": "mapping information",
            "organizer": {
              "displayName": "Christian Dähn"
            }
          }
        """)
        self.day_json_entry = json.loads("""{
            "kind": "calendar#event",
            "summary": "Urlaub",
            "id": "c1cq8kmuvisglepf374hkc1dfg_20200803T074500Z",
            "start": {
              "date": "2020-08-03"
            },
            "end": {
              "date": "2020-08-05"
            },
            "organizer": {
              "displayName": "Christian Dähn"
            }
          }
        """)
        self.failing_json_entry = json.loads("""{
                "kind": "calendar#event",
                "summary": "\\"Online-Meeting-Moderation\\"-Aufbau vom 03. - 07. August 2020",
                "id": "c1cq8kmuvisglepf374hkc1dfg_20200803T074500Z",
                "colorId": "4",
                "start": {
                },
                "end": {
                  "dateTime": "2020-08-03T11:45:00+02:00"
                },
                "organizer": {
                  "displayName": "Christian Dähn"
                }
              }
            """)


class TestDayEntryHandler(unittest.TestCase):

    def setUp(self) -> None:
        self.fixtures = CalendarJsonEntryFixtures()

    def test_handle_single_hour_entry(self):
        self.assertTrue(HourlyCalendarEventHandler().accept(self.fixtures.hourly_json_entry))
        calendar_event = HourlyCalendarEventHandler().process(self.fixtures.hourly_json_entry)
        self.assertEqual(datetime(2020, 8, 3, 9, 45, tzinfo=timezone(timedelta(hours=2))), calendar_event.start)

    def test_handle_single_hour_free_entry(self):
        self.fixtures.hourly_json_entry['transparency'] = 'transparent'
        calendar_event = HourlyCalendarEventHandler().process(self.fixtures.hourly_json_entry)
        self.assertEqual(False, calendar_event.busy)

    def test_handle_multi_calendar_event(self):
        self.assertTrue(DailyCalendarEventHandler().accept(self.fixtures.day_json_entry))
        calendar_event = DailyCalendarEventHandler().process(self.fixtures.day_json_entry)
        self.assertEqual(datetime(2020, 8, 3, 0, 0, tzinfo=timezone(timedelta(hours=2))), calendar_event.start)
        self.assertEqual(datetime(2020, 8, 5, 23, 59, tzinfo=timezone(timedelta(hours=2))), calendar_event.end)
        self.assertEqual('Urlaub', calendar_event.summary)

    def test_handle_multi_day_free_event(self):
        free_day_event = self.fixtures.day_json_entry
        free_day_event['transparency'] = 'transparent'
        calendar_event = DailyCalendarEventHandler().process(free_day_event)
        self.assertEqual(calendar_event.busy, False)


class TestCalendarEventMapper(unittest.TestCase):

    def setUp(self) -> None:
        self.fixtures = CalendarJsonEntryFixtures()

    def test_can_map_hourly(self):
        self.assertEqual(HourlyCalendarEventHandler().process(self.fixtures.hourly_json_entry),
                         CalendarEventMapper().to_calendar_event(self.fixtures.hourly_json_entry))

    def test_can_map_daily(self):
        self.assertEqual(DailyCalendarEventHandler().process(self.fixtures.day_json_entry),
                         CalendarEventMapper().to_calendar_event(self.fixtures.day_json_entry))

    def test_map_will_fail_on_everything_else(self):
        with self.assertRaises(GCalHandlingException) as e:
            CalendarEventMapper().to_calendar_event(self.fixtures.failing_json_entry)
