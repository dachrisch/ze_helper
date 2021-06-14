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

        mapping = self._resolve(calendar_event)
        return ClockodoDay(calendar_event.start, calendar_event.end, calendar_event.summary, mapping)

    def _resolve(self, calendar_event):
        # color id definitions https://lukeboyle.com/blog-posts/2016/04/google-calendar-api---color-id
        if calendar_event.color_id == 4:  # Flamingo
            mapping = self.resolution_service.resolve_for('Bayer AG',
                                                          'Training Workshops for PM Mrz/Apr 2021 Bestellnr.  2950118870',
                                                          'Workshop Vor-/Nachbereitung')
        elif calendar_event.color_id == 6:  # Tangerine
            mapping = self.resolution_service.resolve_for('Bayer AG',
                                                          'Training Workshops for PM Mrz/Apr 2021 Bestellnr.  2950118870',
                                                          'Workshop-Durchführung')
        elif calendar_event.color_id == 3:  # Grape
            mapping = self.resolution_service.resolve_for('AOK Systems GmbH', 'Coach the Coaches PO 10528/10721',
                                                          'Coaching')
        elif calendar_event.color_id == 1:  # Lavender
            mapping = self.resolution_service.resolve_for('AOK Systems GmbH', 'Coach the Coaches PO 10528/10721',
                                                          'Coaching')
            mapping.billable = 0
        elif calendar_event.color_id == 2:  # Sage
            mapping = self.resolution_service.resolve_for('Siemens Energy Global GmbH & Co. KG',
                                                          'Scrum Inspektion März 2021 Bestellnummer 482Q/9770053445',
                                                          'Workshop-Durchführung')
        elif calendar_event.color_id == 10:  # Basil
            mapping = self.resolution_service.resolve_for('Dräger',
                                                          'Zielfindung Transformation Business Unit',
                                                          'Coaching')
        else:
            mapping = self.resolution_service.resolve_for('it-agile GmbH', 'Interne Struktur und Organisation',
                                                          'Interne Arbeitszeit')
        return mapping

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
