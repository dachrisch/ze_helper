from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from service.clockodo import ClockodoService
from service.clockodo.credentials import CredentialsProvider
from service.clockodo.entry import ClockodoEntryService
from service.clockodo.mapping import ClockodoDayMapper, ClockodoResolutionService
from service.gcal import GoogleCalendarServiceWrapper, GoogleCalendarService


class Credentials(DeclarativeContainer):
    credentials_provider = providers.Singleton(CredentialsProvider)


class Google(DeclarativeContainer):
    google_calendar_service = providers.Singleton(GoogleCalendarService)
    calendar_service_wrapper = providers.Factory(GoogleCalendarServiceWrapper, service=google_calendar_service)


class Clockodo(DeclarativeContainer):
    clockodo_service = providers.Factory(ClockodoService, credentials_provider=Credentials.credentials_provider)


class Mappings(DeclarativeContainer):
    resolution_service = providers.Factory(ClockodoResolutionService, clockodo_service=Clockodo.clockodo_service)
    day_entry_mapper = providers.Factory(ClockodoDayMapper, resolution_service=resolution_service)


class Services(DeclarativeContainer):
    entry_service = providers.Factory(ClockodoEntryService, clockodo_service=Clockodo.clockodo_service,
                                      day_entry_mapper=Mappings.day_entry_mapper,
                                      google_calendar_service=Google.calendar_service_wrapper)
