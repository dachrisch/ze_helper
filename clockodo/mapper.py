from clockodo.entity import ClockodoDay
from clockodo.resolution import ClockodoResolutionService
from gcal.entity import DayEntry


class ClockodoDayMapper(object):

    def __init__(self, resolution_service: ClockodoResolutionService):
        self.resolution_service = resolution_service

    def to_clockodo_day(self, day_entry: DayEntry) -> ClockodoDay:

        if day_entry.color_id == 4:
            mapping = self.resolution_service.resolve_for('HDI',
                                                          'Design Sprint Bestellung 4500200459',
                                                          'Workshop-Durchführung')
        elif day_entry.color_id == 2:
            mapping = self.resolution_service.resolve_for('Siemens Energy Global GmbH & Co. KG',
                                                          'Scrum Inspektion März 2021 Bestellnummer 482Q/9770053445',
                                                          'Workshop-Durchführung')
        elif day_entry.color_id == 6:
            mapping = self.resolution_service.resolve_for('HDI',
                                                          'Design Sprint Bestellung 4500200459',
                                                          'Workshop Vor-/Nachbereitung')
        elif day_entry.color_id == 3:
            mapping = self.resolution_service.resolve_for('AOK Systems GmbH', 'Coach the Coaches PO 10528/10721',
                                                          'Coaching')
        elif day_entry.color_id == 1:
            mapping = self.resolution_service.resolve_for('AOK Systems GmbH', 'Coach the Coaches PO 10528/10721',
                                                          'Coaching')
            mapping.billable = 0
        else:
            mapping = self.resolution_service.resolve_for('it-agile GmbH', 'Vertrieb', 'Interne Arbeitszeit')
        return ClockodoDay(day_entry.start, day_entry.end, day_entry.summary, mapping)

    def json_to_logging(self, json: dict):
        if 'services_name' in json:
            service = json['services_name']
        else:
            service = json['services_id']
        return f"({service})[from={json['time_since']}, duration={json['duration_time']}, text={json['text']}]"
