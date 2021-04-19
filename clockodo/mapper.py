from clockodo.entity import ClockodoDay
from clockodo.resolution import ClockodoResolutionService
from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping, PersistenceMappingConverter


class ClockodoCommentMappingStore(object):
    def __init__(self, persistence_mapping: PersistenceMapping):
        self.persistence_mapping = persistence_mapping

    @classmethod
    def append_persistence_mapping(cls, persistence_mapping: PersistenceMapping):
        return cls(persistence_mapping)

    def to_comment(self, comment: str) -> str:
        return f'{comment}\n{PersistenceMappingConverter.to_secure_string(self.persistence_mapping)}'

    @classmethod
    def comment_with_persistence(cls, calendar_event: CalendarEvent):
        if calendar_event.has_persistence_mapping():
            return cls.append_persistence_mapping(calendar_event.persistence_mapping).to_comment(calendar_event.summary)
        else:
            return calendar_event.summary


class ClockodoDayMapper(object):

    def __init__(self, resolution_service: ClockodoResolutionService):
        self.resolution_service = resolution_service

    def to_clockodo_day(self, calendar_event: CalendarEvent) -> ClockodoDay:

        mapping = self._resolve(calendar_event)
        clockodo_comment = ClockodoCommentMappingStore.comment_with_persistence(calendar_event)
        return ClockodoDay(calendar_event.start, calendar_event.end, clockodo_comment, mapping)

    def _resolve(self, calendar_event):
        if calendar_event.color_id == 4:  # Flamingo
            mapping = self.resolution_service.resolve_for('HDI',
                                                          'Design Sprint Bestellung 4500200459',
                                                          'Workshop-Durchführung')
        elif calendar_event.color_id == 2:  # Sage
            mapping = self.resolution_service.resolve_for('Siemens Energy Global GmbH & Co. KG',
                                                          'Scrum Inspektion März 2021 Bestellnummer 482Q/9770053445',
                                                          'Workshop-Durchführung')
        elif calendar_event.color_id == 6:  # Tangerine
            mapping = self.resolution_service.resolve_for('HDI',
                                                          'Design Sprint Bestellung 4500200459',
                                                          'Workshop Vor-/Nachbereitung')
        elif calendar_event.color_id == 3:  # Grape
            mapping = self.resolution_service.resolve_for('AOK Systems GmbH', 'Coach the Coaches PO 10528/10721',
                                                          'Coaching')
        elif calendar_event.color_id == 1:  # Lavender
            mapping = self.resolution_service.resolve_for('AOK Systems GmbH', 'Coach the Coaches PO 10528/10721',
                                                          'Coaching')
            mapping.billable = 0
        else:
            mapping = self.resolution_service.resolve_for('it-agile GmbH', 'Vertrieb', 'Interne Arbeitszeit')
        return mapping

    def to_clockodo_days(self, calendar_events: [CalendarEvent]) -> [ClockodoDay]:
        return tuple(map(lambda calendar_event: self.to_clockodo_day(calendar_event), calendar_events))
