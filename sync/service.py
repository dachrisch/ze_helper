from clockodo.entity import ClockodoDay
from clockodo.entry import ClockodoEntryService
from clockodo.mapper import ClockodoDayMapper
from gcal.entity import CalendarEvent
from gcal.service import GoogleCalendarEventProcessor


class CalendarSyncService(object):

    def __init__(self, google_calendar_event_processor: GoogleCalendarEventProcessor,
                 clockodo_service: ClockodoEntryService,
                 clockodo_mapper: ClockodoDayMapper):
        self.clockodo_mapper = clockodo_mapper
        self.google_calendar_event_processor = google_calendar_event_processor
        self.clockodo_service = clockodo_service

    def sync_month(self, year: int, month: int):
        self._delete_entries(year, month)
        self._insert_entries(year, month)

    def _delete_entries(self, year: int, month: int):
        self.clockodo_service.delete_entries(year, month)

    def _insert_entries(self, year: int, month: int):
        self._insert(self._map(self._fetch(year, month)))

    def _fetch(self, year, month) -> [CalendarEvent]:
        return self.google_calendar_event_processor.calendar_events_in_month(year, month)

    def _map(self, calendar_events: [CalendarEvent]) -> [ClockodoDay]:
        return self.clockodo_mapper.to_clockodo_days(calendar_events)

    def _insert(self, clockodo_days: [ClockodoDay]):
        return self.clockodo_service.enter_calendar_events(clockodo_days)