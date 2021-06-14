import unittest
from datetime import datetime

from clockodo.entity import ClockodoDay, ClockodoIdMapping
from clockodo.mapper import ClockodoDayFromJsonMapper
from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping
from shared.store import ClockodoDayStoreService


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

    def test_stored_day_same_as_mapped_day(self):
        calendar_event, clockodo_day = self._create_both_days(datetime(2021, 8, 1, 10), datetime(2021, 8, 2, 11),
                                                              'Test day')

        store_service = ClockodoDayStoreService()
        store_service.store(clockodo_day, calendar_event)

        self.assertEqual(store_service.retrieve(calendar_event),
                         ClockodoDayFromJsonMapper().from_json({
                             'time_since': calendar_event.start.isoformat(),
                             'time_until': calendar_event.end.isoformat(),
                             'customers_id': clockodo_day.id_mapping.customer_id,
                             'projects_id': clockodo_day.id_mapping.project_id,
                             'services_id': clockodo_day.id_mapping.service_id,
                             'billable': clockodo_day.billable,
                             'text': clockodo_day.comment,
                             'id': clockodo_day.persistence_mapping.source_id}))

    def _create_both_days(self, start_date, end_date, comment):
        clockodo_day = ClockodoDay(start_date, end_date, comment, ClockodoIdMapping(2, 3, 4))
        clockodo_day.update_persistence_mapping(PersistenceMapping(f'clockodo_{start_date}{end_date}'))
        calendar_event = CalendarEvent(start_date, end_date, comment,
                                       persistence_mapping=PersistenceMapping(f'gcal_{start_date}{end_date}'))
        return calendar_event, clockodo_day
