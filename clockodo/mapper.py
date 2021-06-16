from datetime import datetime
from typing import Dict, List

from clockodo.entity import ClockodoDay, ClockodoIdMapping
from clockodo.resolution import ClockodoResolutionService
from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping


class ClockodoDayMapper(object):

    def __init__(self, resolution_service: ClockodoResolutionService):
        self.resolution_service = resolution_service

    def to_clockodo_day(self, calendar_event: CalendarEvent) -> ClockodoDay:
        mapping = self.resolution_service.resolve_from_event(calendar_event)
        return ClockodoDay(calendar_event.start, calendar_event.end, calendar_event.summary, mapping)

    def to_clockodo_days(self, calendar_events: [CalendarEvent]) -> [ClockodoDay]:
        return tuple(map(lambda calendar_event: self.to_clockodo_day(calendar_event), calendar_events))


class ClockodoDayFromJsonMapper:
    def from_json(self, json_entry: Dict):
        start_date = datetime.fromisoformat(json_entry['time_since'])
        end_date = datetime.fromisoformat(json_entry['time_until'])
        clockodo_day = ClockodoDay(start_date, end_date, json_entry['text'], self._id_mapping_from_json(json_entry))
        clockodo_day.update_persistence_mapping(PersistenceMapping(json_entry['id']))
        return clockodo_day

    def from_json_list(self, json_entries: List[Dict]):
        return (self.from_json(entry) for entry in json_entries)

    def _id_mapping_from_json(self, json_entry: Dict):
        return ClockodoIdMapping(json_entry['customers_id'], json_entry['projects_id'],
                                 json_entry['services_id'], json_entry['billable'])
