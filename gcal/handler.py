from abc import ABC
from datetime import datetime, date, time

import pytz

from gcal.entity import CalendarEvent, PrivateProperties
from shared.persistence import PersistenceMapping


class GCalHandlingException(Exception):
    pass


class ExtendedPropertiesHandlerMixin(object):
    def has_private_properties(self, json_entry: dict) -> bool:
        return 'clockodo_id' in json_entry.get('extendedProperties', {}).get('private', {})

    def extract_private_properties(self, json_entry: dict) -> PrivateProperties:
        return PrivateProperties(json_entry['extendedProperties']['private'])


class CalendarEventHandler(ABC):
    def accept(self, json_entry: CalendarEvent) -> bool:
        raise NotImplementedError

    def process(self, json_entry: dict) -> CalendarEvent:
        raise NotImplementedError


class FailingCalendarEventHandler(CalendarEventHandler):

    def process(self, json_entry: dict) -> CalendarEvent:
        raise GCalHandlingException(f"can't handle event: {json_entry}")

    def accept(self, json_entry: dict) -> bool:
        return True


class HourlyCalendarEventHandler(CalendarEventHandler, ExtendedPropertiesHandlerMixin):
    def accept(self, json_entry: dict) -> bool:
        return 'dateTime' in json_entry.get('start') and 'dateTime' in json_entry.get(
            'end') and json_entry.get('summary')

    def process(self, json_entry: dict) -> CalendarEvent:
        entry = CalendarEvent()
        entry.start = datetime.fromisoformat(json_entry['start']['dateTime'])
        entry.end = datetime.fromisoformat(json_entry['end']['dateTime'])
        entry.summary = json_entry['summary']
        entry.color_id = int(json_entry.get('colorId', 0))
        entry.description = json_entry.get('description', '')
        entry.update_persistence_mapping(PersistenceMapping(json_entry['id']))
        if self.has_private_properties(json_entry):
            entry.private_properties =self.extract_private_properties(json_entry)
        return entry


class MultiCalendarEventHandler(CalendarEventHandler):
    def accept(self, json_entry: dict) -> bool:
        return 'date' in json_entry.get('start') and json_entry.get('summary')

    def process(self, json_entry: dict) -> CalendarEvent:
        entry = CalendarEvent(json_entry['id'])
        local_timezone = pytz.timezone('Europe/Berlin')
        entry.start = local_timezone.localize(
            datetime.combine(date.fromisoformat(json_entry['start']['date']), time(0, 0)))
        entry.end = local_timezone.localize(
            datetime.combine(date.fromisoformat(json_entry['end']['date']), time(23, 59)))
        entry.summary = json_entry['summary']
        return entry
