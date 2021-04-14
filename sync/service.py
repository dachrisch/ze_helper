from clockodo.entity import ClockodoDay
from clockodo.entry import ClockodoEntryService
from clockodo.mapper import ClockodoDayMapper
from gcal.entity import CalendarEvent, PrivateProperties
from gcal.service import GoogleCalendarEventProcessor, GoogleCalendarService


class GoogleCalendarEventUpdaterService(object):
    def __init__(self, google_service: GoogleCalendarService):
        self.google_service = google_service

    def store_clockodo_link(self, calendar_event: CalendarEvent, clockodo_day: ClockodoDay):
        self.google_service.update_private_properties(calendar_event.persistence_mapping,
                                                      PrivateProperties.from_mapping(clockodo_day.persistence_mapping))


class CalendarSyncService(object):

    def __init__(self, google_calendar_event_processor: GoogleCalendarEventProcessor,
                 clockodo_service: ClockodoEntryService,
                 clockodo_mapper: ClockodoDayMapper,
                 google_calendar_event_updater: GoogleCalendarEventUpdaterService):
        self.clockodo_mapper = clockodo_mapper
        self.google_calendar_event_processor = google_calendar_event_processor
        self.clockodo_service = clockodo_service
        self.google_calendar_event_updater = google_calendar_event_updater

    def sync_month(self, year: int, month: int):
        self._delete_entries(year, month)
        self._insert_or_update_entries(year, month)

    def _delete_entries(self, year: int, month: int):
        self.clockodo_service.delete_entries(year, month)

    def _insert_or_update_entries(self, year: int, month: int):
        for calendar_event in self.google_calendar_event_processor.calendar_events_in_month(year, month):
            clockodo_day = self.clockodo_mapper.to_clockodo_day(calendar_event)
            inserted_clockodo_day = self.clockodo_service.enter(clockodo_day)
            self.google_calendar_event_updater.store_clockodo_link(calendar_event, inserted_clockodo_day)
