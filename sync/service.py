from clockodo.entity import ClockodoDay
from clockodo.entry import ClockodoEntryService
from clockodo.mapper import ClockodoDayMapper
from gcal.entity import CalendarEvent
from gcal.service import GoogleCalendarEventProcessor, GoogleCalendarService
from shared.store import ClockodoDayStoreService


class CalendarSyncService(object):

    def __init__(self, google_calendar_event_processor: GoogleCalendarEventProcessor,
                 clockodo_service: ClockodoEntryService, clockodo_mapper: ClockodoDayMapper):
        self.clockodo_mapper = clockodo_mapper
        self.google_calendar_event_processor = google_calendar_event_processor
        self.clockodo_service = clockodo_service
        self.store_service = ClockodoDayStoreService()

    def sync_month(self, year: int, month: int):
        self._delete_entries(year, month)
        self._insert_or_update_entries(year, month)

    def _delete_entries(self, year: int, month: int):
        self.clockodo_service.delete_entries(year, month)

    def _insert_or_update_entries(self, year: int, month: int):

        for calendar_event in self.google_calendar_event_processor.calendar_events_in_month(year, month):
            clockodo_day = self.clockodo_mapper.to_clockodo_day(calendar_event)
            inserted_clockodo_day = self.clockodo_service.enter(clockodo_day)
            self.store_service.store(inserted_clockodo_day, calendar_event)
