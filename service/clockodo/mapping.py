from datetime import datetime

from entity.day import ShorttimeDayEntry, CustomerDayEntry, InternalDayEntry, WorkshopPrepDayEntry, WorkshopDayEntry, \
    DayEntry
from service.clockodo import ClockodoDay
from service.clockodo.day import ClockodoIdMapping
from service.clockodo.entry import ClockodoService


class MappingError(ValueError):
    pass


class ClockodoResolutionService(object):

    def __init__(self, clockodo_service: ClockodoService):

        self.clockodo_service = clockodo_service

    def resolve_for(self, customer_name: str, project_name: str, service_name: str) -> ClockodoIdMapping:
        resolved_customer = next(
            filter(lambda customer: customer['name'] == customer_name, self.clockodo_service.retrieve('customers')),
            None)
        if not resolved_customer:
            raise MappingError(f'no mapping found for customer [{customer_name}]')
        customer_id = resolved_customer['id']
        billable = 1 if resolved_customer['billable_default'] else 0
        project_id = next(filter(lambda project: project['name'] == project_name, resolved_customer['projects']),
                          {'id': 0})['id']
        if not project_id:
            raise MappingError(f'no mapping found for project [{project_name}]')
        service_id = \
            next(filter(lambda service: service['name'] == service_name, self.clockodo_service.retrieve('services')),
                 {'id': 0})['id']
        if not service_id:
            raise MappingError(f'no mapping found for service [{service_name}]')
        return ClockodoIdMapping(customer_id, project_id, service_id, billable)


class ClockodoDayMapper(object):

    def __init__(self, resolution_service: ClockodoResolutionService):
        self.resolution_service = resolution_service

    def to_clockodo_day(self, event: DayEntry) -> ClockodoDay:
        date = datetime.strptime(event.date, '%d.%m.%Y')
        start_time = datetime.strptime(event.start, '%H:%M')
        end_time = datetime.strptime(event.end, '%H:%M')
        start_date = datetime(date.year, date.month, date.day, start_time.hour, start_time.minute, 0)
        end_date = datetime(date.year, date.month, date.day, end_time.hour, end_time.minute, 0)
        mapping = None
        if isinstance(event, WorkshopDayEntry):
            mapping = self.resolution_service.resolve_for('Bayer AG',
                                                          'PM-Trainings 9-13 Bst.-Nr.: 2950100643',
                                                          'Inhouse Schulung')
        elif isinstance(event, WorkshopPrepDayEntry):
            mapping = self.resolution_service.resolve_for('Bayer AG',
                                                          'PM-Trainings 9-13 Bst.-Nr.: 2950100643',
                                                          'Inhouse Schulung Vor-/ Nachbereitung')
        elif isinstance(event, InternalDayEntry):
            mapping = self.resolution_service.resolve_for('it-agile GmbH', 'Vertrieb', 'Interne Arbeitszeit')
        elif isinstance(event, CustomerDayEntry):
            mapping = self.resolution_service.resolve_for('AOK Systems GmbH', 'Coach the Coaches', 'Coaching')
        elif isinstance(event, ShorttimeDayEntry):
            mapping = self.resolution_service.resolve_for('it-agile GmbH', 'Kurzarbeit', 'Interne Arbeitszeit')
        else:
            raise Exception("don't know how to map [%s]" % event)

        return ClockodoDay(start_date, end_date, event.comment, mapping)

    def json_to_logging(self, json: dict):
        if 'services_name' in json:
            service = json['services_name']
        else:
            service = json['services_id']
        return f"({service})[from={json['time_since']}, duration={json['duration_time']}, text={json['text']}]"
