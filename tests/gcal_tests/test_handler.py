import json
import unittest
from datetime import datetime, timezone, timedelta

from gcal.entity import MappingInfo
from gcal.handler import HourlyCalendarEventHandler, MultiCalendarEventHandler, GCalHandlingException, \
    MappingInfoEventHandlerMixin
from gcal.mapper import CalendarEventMapper


class TestDayEntryHandler(unittest.TestCase):

    def setUp(self) -> None:
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
        self.assertTrue(HourlyCalendarEventHandler().accept(self.hourly_json_entry))
        calendar_event = HourlyCalendarEventHandler().process(self.hourly_json_entry)
        self.assertEqual(datetime(2020, 8, 3, 9, 45, tzinfo=timezone(timedelta(hours=2))), calendar_event.start)
        self.assertEqual(datetime(2020, 8, 3, 11, 45, tzinfo=timezone(timedelta(hours=2))), calendar_event.end)
        self.assertEqual('"Online-Meeting-Moderation"-Aufbau vom 03. - 07. August 2020', calendar_event.summary)
        self.assertEqual(4, calendar_event.color_id)
        self.assertEqual("mapping information", calendar_event.description)

    def test_handle_multi_calendar_event(self):
        self.assertTrue(MultiCalendarEventHandler().accept(self.day_json_entry))
        calendar_event = MultiCalendarEventHandler().process(self.day_json_entry)
        self.assertEqual(datetime(2020, 8, 3, 0, 0, tzinfo=timezone(timedelta(hours=2))), calendar_event.start)
        self.assertEqual(datetime(2020, 8, 5, 23, 59, tzinfo=timezone(timedelta(hours=2))), calendar_event.end)
        self.assertEqual('Urlaub', calendar_event.summary)

    def test_can_map_hourly(self):
        self.assertEqual(HourlyCalendarEventHandler().process(self.hourly_json_entry),
                         CalendarEventMapper().to_calendar_event(self.hourly_json_entry))

    def test_can_map_daily(self):
        self.assertEqual(MultiCalendarEventHandler().process(self.day_json_entry),
                         CalendarEventMapper().to_calendar_event(self.day_json_entry))

    def test_map_will_fail_on_everything_else(self):
        with self.assertRaises(GCalHandlingException) as e:
            CalendarEventMapper().to_calendar_event(self.failing_json_entry)

    def test_handle_entry_with_mapping_info(self):
        mapping_info = json.loads("""{
                    "id": "c1cq8kmuvisglepf374hkc1dfg_20200803T074500Z",
                    "extendedProperties": {
                      "private": {
                        "clockodo_id" : "123456789"
                      }
                    }
                  }
                """)

        self.assertEqual(True, MappingInfoEventHandlerMixin().has_mapping_info(mapping_info))
        self.assertEqual(False, MappingInfoEventHandlerMixin().has_mapping_info({}))
        self.assertEqual(False, MappingInfoEventHandlerMixin().has_mapping_info({'extendedProperties': {'shared': {}}}))
        self.assertEqual(False,
                         MappingInfoEventHandlerMixin().has_mapping_info(
                             {'extendedProperties': {'private': {'other': 'key'}}}))

        self.assertEqual(MappingInfo('c1cq8kmuvisglepf374hkc1dfg_20200803T074500Z', '123456789'),
                         MappingInfoEventHandlerMixin().extract_mapping_info(mapping_info))

    def test_handle_hourly_entry_with_mapping_info(self):
        self.hourly_json_entry['extendedProperties'] = {'private': {'clockodo_id': '123456789'}}
        calendar_event = HourlyCalendarEventHandler().process(self.hourly_json_entry)
        self.assertEqual(True, calendar_event.has_mapping_info())
