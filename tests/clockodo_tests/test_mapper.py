import unittest

from clockodo.entity import ClockodoIdMapping
from clockodo.mapper import ClockodoDayMapper, ClockodoDay
from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping
from tests.clockodo_tests.clockodo_mock import ClockodoResolutionServiceMock


class TestClockodoMapper(unittest.TestCase):
    def test_default_maps_to_internal(self):
        entry = CalendarEvent()
        self.assertEqual(ClockodoDay(entry.start, entry.end, entry.summary, ClockodoIdMapping(1, 1, 1, 0)),
                         ClockodoDayMapper(ClockodoResolutionServiceMock()).to_clockodo_day(entry))

    def test_mapping_stores_no_calendar_id_in_comment(self):
        persistence_mapping = PersistenceMapping('1234')
        test_summary = 'Test Summary'
        entry = CalendarEvent(summary=test_summary, persistence_mapping=persistence_mapping)
        clockodo_day = ClockodoDayMapper(ClockodoResolutionServiceMock()).to_clockodo_day(entry)
        self.assertEqual(test_summary, clockodo_day.comment)

    def xtest_json_structure_in_comment(self):
        id_mapping = {'customer': 123, 'service': 456, 'project': 789}
        import base64, json
        encoded_mapping = base64.urlsafe_b64encode(json.dumps(id_mapping).encode()).decode()
        self.assertEqual('eyJjdXN0b21lciI6IDEyMywgInNlcnZpY2UiOiA0NTYsICJwcm9qZWN0IjogNzg5fQ==',
                         encoded_mapping)

        entry = CalendarEvent(summary=f'clockodo://{encoded_mapping}')
        self.assertEqual(ClockodoIdMapping(123, 789, 456),
                         ClockodoDayMapper(ClockodoResolutionServiceMock()).to_clockodo_day(entry).id_mapping)
