import unittest

from clockodo.connector import ResolutionError
from clockodo.entity import ClockodoIdMapping
from clockodo.mapper import ClockodoDayMapper, ClockodoDay
from clockodo.resolution import ClockodoColorIdResolutionService, \
    ClockodoUrlResolutionService
from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping
from tests.clockodo_tests.clockodo_mock import ClockodoApiConnectorMock


class TestClockodoMapper(unittest.TestCase):
    def test_default_maps_to_internal(self):
        entry = CalendarEvent()
        self.assertEqual(ClockodoDay(entry.start, entry.end, entry.summary, ClockodoIdMapping(1, 1, 1, 0)),
                         ClockodoDayMapper(ClockodoColorIdResolutionService(
                             ClockodoApiConnectorMock())).to_clockodo_day(entry))

    def test_mapping_stores_no_calendar_id_in_comment(self):
        persistence_mapping = PersistenceMapping('1234')
        test_summary = 'Test Summary'
        entry = CalendarEvent(summary=test_summary, persistence_mapping=persistence_mapping)
        clockodo_day = ClockodoDayMapper(
            ClockodoColorIdResolutionService(ClockodoApiConnectorMock())).to_clockodo_day(entry)
        self.assertEqual(test_summary, clockodo_day.comment)


class TestClockodoUrlMapping(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = ClockodoUrlResolutionService(ClockodoApiConnectorMock())

    def test_no_url_in_description_raises(self):
        with self.assertRaises(ResolutionError):
            self.resolver.resolve_from_event(CalendarEvent(description='no url given'))

    def test_no_clockodo_url_raises(self):
        with self.assertRaisesRegex(ResolutionError, r'no URL with scheme \[clockodo\] found, just .*'):
            self.resolver.resolve_from_event(
                CalendarEvent(description='url given but not clockodo: http://somewhere.here/but/not/clockodo'))

    def test_no_parameters_raises(self):
        with self.assertRaisesRegex(ResolutionError,
                                    r'failed to find restrCstPrj\[0\] and restrService\[0\] parameter in url, just .*'):
            self.resolver.resolve_from_event(
                CalendarEvent(description='clockodo://somewhere.here/with/params?false_param=124&false_other=578'))

    def test_decode_mapping_from_url_default_billable(self):
        entry = CalendarEvent(
            description='clockodo://my.clockodo.com/de/reports/?restrCstPrj%5B0%5D=1462125-1325527&restrService%5B0%5D=572638')

        self.assertEqual(ClockodoIdMapping(1462125, 1325527, 572638, 1), self.resolver.resolve_from_event(entry))

    def test_decode_mapping_from_url_unbillable(self):
        entry = CalendarEvent(
            description='clockodo://my.clockodo.com/de/reports/?restrCstPrj%5B0%5D=1462125-1325527&restrService%5B0%5D=572638&billable=0')

        self.assertEqual(ClockodoIdMapping(1462125, 1325527, 572638, 0), self.resolver.resolve_from_event(entry))
