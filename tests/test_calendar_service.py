import json
import unittest
from datetime import datetime

from entity.day import DayEntry
from service.gcal import GoogleCalendarService, GoogleCalendarServiceBuilder


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
        return filter(lambda event: 'dateTime' in event['start'] and self.timeMin <= datetime.fromisoformat(
            event['start']['dateTime']).timestamp() and datetime.fromisoformat(
            event['end']['dateTime']).timestamp() <= self.timeMax,
                      self.calendar_events)


class GoogleCalendarServiceBuilderMock(GoogleCalendarServiceBuilder):
    def __init__(self):
        self.calendar_events = []

    def build(self):
        return CalendarServiceMock(self.calendar_events)

    def append(self, event_json):
        self.calendar_events.append(json.loads(event_json))


class CalendarServiceTest(unittest.TestCase):
    def test_customer_event(self):
        mock = GoogleCalendarServiceBuilderMock()
        mock.append("""{
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
""")
        calendar_service = GoogleCalendarService(mock)
        events = calendar_service.events_in_range(datetime(2020, 8, 1), datetime(2020, 8, 31))

        self.assertIsInstance(events[0], DayEntry)
        self._assert_event(events[0], '03.08.2020', '09:45', '11:45',
                           '"Online-Meeting-Moderation"-Aufbau vom 03. - 07. August 2020',
                           'Laut Beschreibung & fakturierbar (Extern)')

    def test_illness(self):
        mock = GoogleCalendarServiceBuilderMock()
        mock.append("""{
    "kind": "calendar#event",
    "summary": "Krank",
    "start": {
      "dateTime": "2020-08-03T10:00:00+02:00"
    },
    "end": {
      "dateTime": "2020-08-03T18:00:00+02:00"
    },
    "organizer": {
      "displayName": "Christian Dähn"
    }
  }
""")
        mock.append("""{
            "kind": "calendar#event",
            "summary": "Krank",
            "start": {
              "dateTime": "2020-08-04T10:00:00+02:00"
            },
            "end": {
              "dateTime": "2020-08-04T18:00:00+02:00"
            },
            "organizer": {
              "displayName": "Christian Dähn"
            }
          }
        """)
        mock.append("""{
            "kind": "calendar#event",
            "summary": "Krank",
            "start": {
              "dateTime": "2020-08-05T10:00:00+02:00"
            },
            "end": {
              "dateTime": "2020-08-05T18:00:00+02:00"
            },
            "organizer": {
              "displayName": "Christian Dähn"
            }
          }
        """)
        calendar_service = GoogleCalendarService(mock)
        events = calendar_service.events_in_range(datetime(2020, 8, 1), datetime(2020, 8, 31))

        self.assertEqual(3, len(events))

        self._assert_event(events[0], '03.08.2020', '10:00', '18:00',
                           'Krank',
                           'Krankheit (aufMUC-Zelle)')
        self._assert_event(events[1], '04.08.2020', '10:00', '18:00',
                           'Krank',
                           'Krankheit (aufMUC-Zelle)')
        self._assert_event(events[2], '05.08.2020', '10:00', '18:00',
                           'Krank',
                           'Krankheit (aufMUC-Zelle)')

    def test_internal_event(self):
        mock = GoogleCalendarServiceBuilderMock()
        mock.append("""{
    "kind": "calendar#event",
    "summary": "Büroumzug",
    "start": {
      "dateTime": "2020-08-03T12:00:00+02:00"
    },
    "end": {
      "dateTime": "2020-08-03T18:00:00+02:00"
    },
    "organizer": {
      "displayName": "Christian Dähn"
    }
  }
""")
        calendar_service = GoogleCalendarService(mock)
        events = calendar_service.events_in_range(datetime(2020, 8, 1), datetime(2020, 8, 31))

        self.assertIsInstance(events[0], DayEntry)
        self._assert_event(events[0], '03.08.2020', '12:00', '18:00', 'Büroumzug', 'laut Beschreibung (Intern)')

    def test_kurzarbeit_label(self):
        mock = GoogleCalendarServiceBuilderMock()
        mock.append("""{
            "kind": "calendar#event",
            "summary": "Kurzarbeit",
            "start": {
              "dateTime": "2020-08-31T10:00:00+02:00"
            },
            "end": {
              "dateTime": "2020-08-31T16:00:00+02:00"
            },
            "organizer": {
              "displayName": "Christian Dähn"
            }
          }
        """)
        calendar_service = GoogleCalendarService(mock)
        events = calendar_service.events_in_range(datetime(2020, 8, 1), datetime(2020, 8, 31))

        self.assertIsInstance(events[0], DayEntry)

        self._assert_event(events[0], '31.08.2020', '10:00', '16:00', 'Kurzarbeit', 'Kurzarbeit (Intern)')

    def test_overlapping_is_split(self):
        mock = GoogleCalendarServiceBuilderMock()
        mock.append("""{
                    "kind": "calendar#event",
                    "summary": "Kurzarbeit",
                    "start": {
                      "dateTime": "2020-08-29T10:00:00+02:00"
                    },
                    "end": {
                      "dateTime": "2020-08-29T16:00:00+02:00"
                    },
                    "organizer": {
                      "displayName": "Christian Dähn"
                    }
                  }
                """)
        mock.append("""{
                            "kind": "calendar#event",
                            "summary": "Overlapping-Work",
                            "start": {
                              "dateTime": "2020-08-29T12:00:00+02:00"
                            },
                            "end": {
                              "dateTime": "2020-08-29T14:00:00+02:00"
                            },
                            "organizer": {
                              "displayName": "Christian Dähn"
                            }
                          }
                        """)
        calendar_service = GoogleCalendarService(mock)
        events = calendar_service.events_in_range(datetime(2020, 8, 1), datetime(2020, 8, 31))

        self.assertEqual(3, len(events))

        self._assert_event(events[0], '29.08.2020', '10:00', '12:00', 'Kurzarbeit', 'Kurzarbeit (Intern)')
        self._assert_event(events[1], '29.08.2020', '12:00', '14:00', 'Overlapping-Work', 'laut Beschreibung (Intern)')
        self._assert_event(events[2], '29.08.2020', '14:00', '16:00', 'Kurzarbeit', 'Kurzarbeit (Intern)')

    def test_same_start_is_dropped(self):
        mock = GoogleCalendarServiceBuilderMock()
        mock.append("""{
                    "kind": "calendar#event",
                    "summary": "Unrelated",
                    "start": {
                      "dateTime": "2020-08-29T09:00:00+02:00"
                    },
                    "end": {
                      "dateTime": "2020-08-29T10:00:00+02:00"
                    },
                    "organizer": {
                      "displayName": "Christian Dähn"
                    }
                  }
                """)
        mock.append("""{
                    "kind": "calendar#event",
                    "summary": "Kurzarbeit",
                    "start": {
                      "dateTime": "2020-08-29T10:00:00+02:00"
                    },
                    "end": {
                      "dateTime": "2020-08-29T16:00:00+02:00"
                    },
                    "organizer": {
                      "displayName": "Christian Dähn"
                    }
                  }
                """)
        mock.append("""{
                            "kind": "calendar#event",
                            "summary": "Overlapping-Work",
                            "start": {
                              "dateTime": "2020-08-29T10:00:00+02:00"
                            },
                            "end": {
                              "dateTime": "2020-08-29T11:00:00+02:00"
                            },
                            "organizer": {
                              "displayName": "Christian Dähn"
                            }
                          }
                        """)
        calendar_service = GoogleCalendarService(mock)
        events = calendar_service.events_in_range(datetime(2020, 8, 1), datetime(2020, 8, 31))

        self.assertEqual(3, len(events))

        self._assert_event(events[1], '29.08.2020', '10:00', '11:00', 'Overlapping-Work', 'laut Beschreibung (Intern)')
        self._assert_event(events[2], '29.08.2020', '11:00', '16:00', 'Kurzarbeit', 'Kurzarbeit (Intern)')

    def test_multiple_overlapping_is_split(self):
        mock = GoogleCalendarServiceBuilderMock()
        mock.append("""{
                    "kind": "calendar#event",
                    "summary": "Kurzarbeit",
                    "start": {
                      "dateTime": "2020-08-29T10:00:00+02:00"
                    },
                    "end": {
                      "dateTime": "2020-08-29T16:00:00+02:00"
                    },
                    "organizer": {
                      "displayName": "Christian Dähn"
                    }
                  }
                """)
        mock.append("""{
                            "kind": "calendar#event",
                            "summary": "Overlapping-Work",
                            "start": {
                              "dateTime": "2020-08-29T12:00:00+02:00"
                            },
                            "end": {
                              "dateTime": "2020-08-29T13:00:00+02:00"
                            },
                            "organizer": {
                              "displayName": "Christian Dähn"
                            }
                          }
                        """)
        mock.append("""{
                            "kind": "calendar#event",
                            "summary": "Overlapping-Work",
                            "start": {
                              "dateTime": "2020-08-29T14:00:00+02:00"
                            },
                            "end": {
                              "dateTime": "2020-08-29T15:00:00+02:00"
                            },
                            "organizer": {
                              "displayName": "Christian Dähn"
                            }
                          }
                        """)
        calendar_service = GoogleCalendarService(mock)
        events = calendar_service.events_in_range(datetime(2020, 8, 1), datetime(2020, 8, 31))

        self.assertEqual(5, len(events))
        self._assert_event(events[0], '29.08.2020', '10:00', '12:00', 'Kurzarbeit', 'Kurzarbeit (Intern)')
        self._assert_event(events[1], '29.08.2020', '12:00', '13:00', 'Overlapping-Work', 'laut Beschreibung (Intern)')
        self._assert_event(events[2], '29.08.2020', '13:00', '14:00', 'Kurzarbeit', 'Kurzarbeit (Intern)')
        self._assert_event(events[3], '29.08.2020', '14:00', '15:00', 'Overlapping-Work', 'laut Beschreibung (Intern)')
        self._assert_event(events[4], '29.08.2020', '15:00', '16:00', 'Kurzarbeit', 'Kurzarbeit (Intern)')

    def _assert_event(self, event: DayEntry, date, start, end, summary, label):
        self.assertEqual(date, event.date)
        self.assertEqual(start, event.start)
        self.assertEqual(end, event.end)
        self.assertEqual(summary, event.comment)
        self.assertEqual(label, event.label)


if __name__ == '__main__':
    unittest.main()
