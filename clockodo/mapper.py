from clockodo.entity import ClockodoDay
from clockodo.resolution import ClockodoResolutionService
from gcal.entity import CalendarEvent
from shared.compare import ComparableMixin


class MappedClockodoDay(ComparableMixin):
    def __init__(self,calendar_event: CalendarEvent, clockodo_day:ClockodoDay):
        self.calendar_event = calendar_event
        self.clockodo_day = clockodo_day

class ClockodoDayMapper(object):

    def __init__(self, resolution_service: ClockodoResolutionService):
        self.resolution_service = resolution_service

    def to_clockodo_day(self, calendar_event: CalendarEvent) -> MappedClockodoDay:

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
        return MappedClockodoDay(calendar_event, ClockodoDay(calendar_event.start, calendar_event.end, calendar_event.summary, mapping))

    def to_clockodo_days(self, calendar_events:[CalendarEvent])-> [MappedClockodoDay]:
        return tuple(map(lambda calendar_event: self.to_clockodo_day(calendar_event), calendar_events))
