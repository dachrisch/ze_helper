import unittest

from clockodo.connector import ResolutionError
from clockodo.entity import ClockodoIdMapping
from clockodo.mapper import ClockodoDayMapper, ClockodoDay
from clockodo.resolution import ClockodoUrlResolutionService, ClockodoDefaultResolutionService, \
    ClockodoColorIdResolutionService, ClockodoResolutionChain
from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping
from tests.clockodo_tests.clockodo_mock import ClockodoApiConnectorMock


class TestClockodoResolution(unittest.TestCase):
    def test_default_maps_to_internal(self):
        entry = CalendarEvent()
        self.assertEqual(ClockodoDay(entry.start, entry.end, entry.summary, ClockodoIdMapping(1, 1, 1, 0)),
                         ClockodoDayMapper(ClockodoDefaultResolutionService(
                             ClockodoApiConnectorMock())).to_clockodo_day(entry))

    def test_mapping_stores_no_calendar_id_in_comment(self):
        persistence_mapping = PersistenceMapping('1234')
        test_summary = 'Test Summary'
        entry = CalendarEvent(summary=test_summary, persistence_mapping=persistence_mapping, color_id=1)
        clockodo_day = ClockodoDayMapper(
            ClockodoDefaultResolutionService(ClockodoApiConnectorMock())).to_clockodo_day(entry)
        self.assertEqual(test_summary, clockodo_day.comment)


class TestClockodoMapping(unittest.TestCase):
    def setUp(self) -> None:
        api_connector_mock = ClockodoApiConnectorMock()
        self.mapper = ClockodoDayMapper(ClockodoResolutionChain(api_connector_mock))

    def test_maps_from_url(self):
        entry = CalendarEvent(
            description='clockodo://my.clockodo.com/de/reports/?restrCstPrj%5B0%5D=1462125-1325527&restrService%5B0%5D=572638')
        self.assertEqual(ClockodoIdMapping(1462125, 1325527, 572638, 1),
                         self.mapper.to_clockodo_day(entry).id_mapping)
    def test_maps_from_url_with_link(self):
        entry = CalendarEvent(
            description='clockodo://<a href="http://my.clockodo.com/de/reports/?since=2021-05-01&until=2021-05-31&order=services&sort=alph-asc&?restrCstPrj%5B0%5D=1462125-1325527&restrService%5B0%5D=572638" id="ow4894" __is_owner="true">my.clockodo.com/de/reports/?since=2021-05-01&amp;until=2021-05-31&amp;order=services&amp;sort=alph-asc&amp;restrCstPrj%5B0%5D=1462125-1325527&amp;restrService%5B0%5D=572638</a>')
        self.assertEqual(ClockodoIdMapping(1462125, 1325527, 572638, 1),
                         self.mapper.to_clockodo_day(entry).id_mapping)

    def test_maps_from_url_with_multiple_html_tags(self):
        entry = CalendarEvent(
            description='clockodo://<a href="http://my.clockodo.com/de/reports/?since=2021-05-01&until=2021-05-31&order=services&sort=alph-asc&?restrCstPrj%5B0%5D=1462125-1325527&restrService%5B0%5D=572638" id="ow4894" __is_owner="true">my.clockodo.com/de/reports/?since=2021-05-01&amp;until=2021-05-31&amp;order=services&amp;sort=alph-asc&amp;restrCstPrj%5B0%5D=1462125-1325527&amp;restrService%5B0%5D=572638</a><br>should not be in url')

        self.assertEqual(ClockodoIdMapping(1462125, 1325527, 572638, 1),
                         self.mapper.to_clockodo_day(entry).id_mapping)

    def test_maps_from_color_id(self):
        entry = CalendarEvent(color_id=1)
        self.assertEqual(ClockodoIdMapping(1462125, 1325527, 572638, 0),
                         self.mapper.to_clockodo_day(entry).id_mapping)

    def test_maps_default_if_no_color_or_url(self):
        entry = CalendarEvent()
        self.assertEqual(ClockodoIdMapping(1, 1, 1, 0),
                         self.mapper.to_clockodo_day(entry).id_mapping)


class TestClockodoUrlResolution(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = ClockodoUrlResolutionService()

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

    def test_decode_mapping_from_url_not_billable(self):
        entry = CalendarEvent(
            description='clockodo://my.clockodo.com/de/reports/?restrCstPrj%5B0%5D=1462125-1325527&restrService%5B0%5D=572638&billable=0')

        self.assertEqual(ClockodoIdMapping(1462125, 1325527, 572638, 0), self.resolver.resolve_from_event(entry))
