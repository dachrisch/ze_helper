from abc import abstractmethod, ABC

from clockodo.entity import ClockodoIdMapping
from clockodo.connector import ClockodoApiConnector, ResolutionError
from gcal.entity import CalendarEvent


class ClockodoResolutionService(ABC):
    def __init__(self, api_connector: ClockodoApiConnector):
        self.api_connector = api_connector

    @abstractmethod
    def resolve_from_event(self, calendar_event: CalendarEvent):
        raise NotImplementedError


class ClockodoColorIdResolutionService(ClockodoResolutionService):
    def resolve_from_event(self, calendar_event: CalendarEvent):
        return self._resolve_from_color_id(calendar_event.color_id)

    def _resolve_from_color_id(self, color_id: int):
        # color id definitions https://lukeboyle.com/blog-posts/2016/04/google-calendar-api---color-id
        if color_id == 4:  # Flamingo
            mapping = self._resolve_for('Bayer AG',
                                       'Training Workshops for PM Mrz/Apr 2021 Bestellnr.  2950118870',
                                       'Workshop Vor-/Nachbereitung')
        elif color_id == 6:  # Tangerine
            mapping = self._resolve_for('Bayer AG',
                                       'Training Workshops for PM Mrz/Apr 2021 Bestellnr.  2950118870',
                                       'Workshop-Durchführung')
        elif color_id == 3:  # Grape
            mapping = self._resolve_for('AOK Systems GmbH', 'Coach the Coaches PO 10528/10721',
                                       'Coaching')
        elif color_id == 1:  # Lavender
            mapping = self._resolve_for('AOK Systems GmbH', 'Coach the Coaches PO 10528/10721',
                                       'Coaching')
            mapping.billable = 0
        elif color_id == 2:  # Sage
            mapping = self._resolve_for('Siemens Energy Global GmbH & Co. KG',
                                       'Scrum Inspektion März 2021 Bestellnummer 482Q/9770053445',
                                       'Workshop-Durchführung')
        elif color_id == 10:  # Basil
            mapping = self._resolve_for('Dräger',
                                       'Zielfindung Transformation Business Unit',
                                       'Coaching')
        else:
            mapping = self._resolve_for('it-agile GmbH', 'Interne Struktur und Organisation',
                                       'Interne Arbeitszeit')
        return mapping

    def _resolve_for(self, customer_name: str, project_name: str, service_name: str) -> ClockodoIdMapping:
        resolved_customer = next(
            filter(lambda customer: customer['name'] == customer_name, self.api_connector.retrieve('customers')),
            None)
        if not resolved_customer:
            raise ResolutionError(f'no mapping found for customer [{customer_name}]')
        customer_id = resolved_customer['id']
        billable = 1 if resolved_customer['billable_default'] else 0
        project_id = next(filter(lambda project: project['name'] == project_name, resolved_customer['projects']),
                          {'id': 0})['id']
        if not project_id:
            raise ResolutionError(f'no mapping found for project [{project_name}]')
        service_id = \
        next(filter(lambda service: service['name'] == service_name, self.api_connector.retrieve('services')),
             {'id': 0})['id']
        if not service_id:
            raise ResolutionError(f'no mapping found for service [{service_name}]')
        return ClockodoIdMapping(customer_id, project_id, service_id, billable)
