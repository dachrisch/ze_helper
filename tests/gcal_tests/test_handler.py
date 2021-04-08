import json
import unittest
from datetime import datetime, timezone, timedelta

from gcal.handler import HourlyDayEntryHandler, MultiDayEntryHandler, GCalHandlingException
from gcal.mapper import GoogleCalendarMapper


class TestDayEntryHandler(unittest.TestCase):

    def setUp(self) -> None:
        self.hourly_json_entry = json.loads("""{
            "kind": "calendar#event",
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

    def test_handle_single_hour_entry(self):
        self.assertTrue(HourlyDayEntryHandler().accept(self.hourly_json_entry))
        day_entry = HourlyDayEntryHandler().process(self.hourly_json_entry)
        self.assertEqual(datetime(2020, 8, 3, 9, 45, tzinfo=timezone(timedelta(hours=2))), day_entry.start)
        self.assertEqual(datetime(2020, 8, 3, 11, 45, tzinfo=timezone(timedelta(hours=2))), day_entry.end)
        self.assertEqual('"Online-Meeting-Moderation"-Aufbau vom 03. - 07. August 2020', day_entry.summary)
        self.assertEqual(4, day_entry.color_id)
        self.assertEqual("mapping information", day_entry.description)

    def test_handle_multi_day_entry(self):
        self.assertTrue(MultiDayEntryHandler().accept(self.day_json_entry))
        day_entry = MultiDayEntryHandler().process(self.day_json_entry)
        self.assertEqual(datetime(2020, 8, 3, 0, 0, tzinfo=timezone(timedelta(hours=2))), day_entry.start)
        self.assertEqual(datetime(2020, 8, 5, 23, 59, tzinfo=timezone(timedelta(hours=2))), day_entry.end)
        self.assertEqual('Urlaub', day_entry.summary)

    def test_can_map_hourly(self):
        self.assertEqual(HourlyDayEntryHandler().process(self.hourly_json_entry),
                         GoogleCalendarMapper().to_day_entry(self.hourly_json_entry))

    def test_can_map_daily(self):
        self.assertEqual(MultiDayEntryHandler().process(self.day_json_entry),
                         GoogleCalendarMapper().to_day_entry(self.day_json_entry))

    def test_map_will_fail_on_everything_else(self):
        with self.assertRaises(GCalHandlingException) as e:
            GoogleCalendarMapper().to_day_entry(self.failing_json_entry)
