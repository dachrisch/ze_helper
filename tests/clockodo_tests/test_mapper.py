import unittest

from clockodo.entity import ClockodoIdMapping
from clockodo.mapper import ClockodoDayMapper, ClockodoDay, ClockodoCommentMappingStore
from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping, PersistenceMappingConverter
from tests.clockodo_tests.clockodo_mock import ClockodoResolutionServiceMock


class TestClockodoCommentMappingStore(unittest.TestCase):
    def test_append_base64_id_to_comment(self):
        test_comment = 'Test Comment'
        persistence_mapping = PersistenceMapping('1245')
        expected_comment = f'{test_comment}\n{PersistenceMappingConverter.to_secure_string(persistence_mapping)}'
        self.assertEqual(expected_comment, ClockodoCommentMappingStore.append_persistence_mapping(
            persistence_mapping).to_comment(test_comment))
        print(expected_comment)


class TestClockodoMapper(unittest.TestCase):
    def test_default_maps_to_internal(self):
        entry = CalendarEvent()
        self.assertEqual(ClockodoDay(entry.start, entry.end, entry.summary, ClockodoIdMapping(1, 1, 1, 0)),
                         ClockodoDayMapper(ClockodoResolutionServiceMock()).to_clockodo_day(entry))

    def test_mapping_stores_calendar_id(self):
        persistence_mapping = PersistenceMapping('1234')
        test_summary = 'Test Summary'
        entry = CalendarEvent(summary=test_summary, persistence_mapping=persistence_mapping)
        clockodo_day = ClockodoDayMapper(ClockodoResolutionServiceMock()).to_clockodo_day(entry)
        self.assertEqual(
            ClockodoCommentMappingStore.append_persistence_mapping(persistence_mapping).to_comment(test_summary),
            clockodo_day.comment)
