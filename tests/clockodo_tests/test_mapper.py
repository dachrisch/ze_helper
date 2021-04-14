import unittest

from clockodo.entity import ClockodoDay, ClockodoIdMapping
from clockodo.mapper import ClockodoDayMapper
from gcal.entity import CalendarEvent
from tests.clockodo_tests.clockodo_mock import ClockodoResolutionServiceMock


class TestClockodoMapper(unittest.TestCase):
    def test_default_maps_to_internal(self):
        entry = CalendarEvent()
        self.assertEqual(ClockodoDay(entry.start, entry.end, entry.summary, ClockodoIdMapping(1, 1, 1, 0)),
                         ClockodoDayMapper(ClockodoResolutionServiceMock()).to_clockodo_day(
                             entry))
