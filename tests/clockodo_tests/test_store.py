import unittest
from datetime import datetime
from typing import List, Dict
from unittest import mock

from clockodo.entity import ClockodoDay, ClockodoIdMapping
from clockodo.entry import ClockodoEntryService
from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping
from shared.store import ClockodoDayStoreService
from tests.clockodo_tests.clockodo_mock import mocked_requests_get


class TestClockodoDayStoreService(unittest.TestCase):
    def test_store_single_event(self):
        calendar_event, clockodo_day = self._create_both_days(datetime(2021, 8, 1, 10), datetime(2021, 8, 2, 11),
                                                              'Test day')

        store_service = ClockodoDayStoreService()
        store_service.store(clockodo_day, calendar_event)
        self.assertEqual(clockodo_day, store_service.retrieve(calendar_event))

    def test_store_split_event_with_break(self):
        calendar_event_1, clockodo_day_1 = self._create_both_days(datetime(2021, 8, 1, 10), datetime(2021, 8, 2, 11),
                                                                  'Test day')
        calendar_event_2, clockodo_day_2 = self._create_both_days(datetime(2021, 8, 1, 12), datetime(2021, 8, 2, 13),
                                                                  'Test day')
        calendar_event_2.update_persistence_mapping(calendar_event_1.persistence_mapping)

        store_service = ClockodoDayStoreService()
        store_service.store(clockodo_day_1, calendar_event_1)
        store_service.store(clockodo_day_2, calendar_event_2)
        self.assertEqual(clockodo_day_1, store_service.retrieve(calendar_event_1))
        self.assertEqual(clockodo_day_2, store_service.retrieve(calendar_event_2))

    def test_retrieve_changed_single(self):
        store_service = ClockodoDayStoreService()
        calendar_event, clockodo_day = self._create_both_days(datetime(2021, 8, 1, 10), datetime(2021, 8, 2, 11),
                                                              'Test day')

        store_service.store(clockodo_day, calendar_event)

        new_calendar_event = calendar_event.replace(start=calendar_event.start.replace(hour=12),
                                                    end=calendar_event.end.replace(hour=13))
        self.assertEqual(clockodo_day, store_service.retrieve(new_calendar_event))

    def test_retrieve_new_single_event(self):
        store_service = ClockodoDayStoreService()
        calendar_event, _ = self._create_both_days(datetime(2021, 8, 1, 10), datetime(2021, 8, 2, 11),
                                                   'Test day')

        self.assertEqual(ClockodoDayStoreService.NOT_FOUND, store_service.retrieve(calendar_event))

    @mock.patch(f'{ClockodoEntryService.__module__}.requests.get', side_effect=mocked_requests_get)
    def txest_filter_stored_with_current_events(self, get_mock):
        calendar_event, clockodo_day = self._create_both_days(datetime(2021, 8, 1, 10), datetime(2021, 8, 2, 11),
                                                              'Test day')

        store_service = ClockodoDayStoreService()
        store_service.store(clockodo_day, calendar_event)

        class ClockodoDayMapper:
            def from_json(self, json_entry:Dict):
                start_date = datetime.fromisoformat(json_entry['time_since'])
                end_date = datetime.fromisoformat(json_entry['time_until'])
                return ClockodoDay(start_date, end_date, json_entry['text'], self._id_mapping_from_json(json_entry))

            def from_json_list(self, json_entries:List[Dict]):
                return (self.from_json(entry) for entry in json_entries)

            def _id_mapping_from_json(self, json_entry:Dict):
                return ClockodoIdMapping(json_entry['customers_id'],json_entry['projects_id'],json_entry['services_id'],json_entry['billable'])

        current_entries = ClockodoEntryService('test@here', 'None').current_entries(2021, 8)
        self.assertEqual({store_service.retrieve(calendar_event)},
                         set(ClockodoDayMapper().from_json_list(current_entries)))

    def _create_both_days(self, start_date, end_date, comment):
        clockodo_day = ClockodoDay(start_date, end_date, comment, ClockodoIdMapping(2, 3, 4))
        clockodo_day.update_persistence_mapping(PersistenceMapping(f'clockodo_{start_date}{end_date}'))
        calendar_event = CalendarEvent(start_date, end_date, comment,
                                       persistence_mapping=PersistenceMapping(f'gcal_{start_date}{end_date}'))
        return calendar_event, clockodo_day
