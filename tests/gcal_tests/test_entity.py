import unittest
from datetime import datetime

from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping


class TestCalendarEvent(unittest.TestCase):
    def test_replace(self):
        now = datetime.now()
        calendar_event = CalendarEvent(now, now.replace(hour=1), 'Test summary', 'Test description', 1,
                                       PersistenceMapping(12), True)
        expected_calendar_event = CalendarEvent(now.replace(day=1), now.replace(day=1, hour=1), 'Test summary 2',
                                                'Test description 2', 2,
                                                PersistenceMapping(123), False)
        self._assert_property_replaced('start', expected_calendar_event, calendar_event)
        self._assert_property_replaced('end', expected_calendar_event, calendar_event)
        self._assert_property_replaced('summary', expected_calendar_event, calendar_event)
        self._assert_property_replaced('description', expected_calendar_event, calendar_event)
        self._assert_property_replaced('color_id', expected_calendar_event, calendar_event)
        self._assert_property_replaced('persistence_mapping', expected_calendar_event, calendar_event)
        self._assert_property_replaced('busy', expected_calendar_event, calendar_event)
        self.assertEqual(expected_calendar_event,
                         calendar_event.replace(expected_calendar_event.start, expected_calendar_event.end,
                                                expected_calendar_event.summary, expected_calendar_event.description,
                                                expected_calendar_event.color_id,
                                                expected_calendar_event.persistence_mapping,
                                                expected_calendar_event.busy))

    def _assert_property_replaced(self, name: str, expected_calendar_event: CalendarEvent,
                                  calendar_event: CalendarEvent):
        kwargs = {name: getattr(expected_calendar_event, name)}
        replaced_event = calendar_event.replace(**kwargs)
        self.assertEqual(getattr(expected_calendar_event, name),
                         getattr(replaced_event, name))

        for unchanged_name in filter(lambda present_name: present_name != name and not present_name.startswith('_'),
                                     calendar_event.__dict__):
            self.assertEqual(getattr(calendar_event, unchanged_name), getattr(replaced_event, unchanged_name),
                             f'attribute [{unchanged_name}] unexpectedly changed')
