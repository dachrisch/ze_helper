from abc import abstractmethod, ABC
from urllib import parse

from urlextract import URLExtract

from clockodo.connector import ClockodoApiConnector, ResolutionError
from clockodo.entity import ClockodoIdMapping
from gcal.entity import CalendarEvent


class ClockodoResolutionService(ABC):
    def __init__(self, api_connector: ClockodoApiConnector):
        self.api_connector = api_connector

    @abstractmethod
    def resolve_from_event(self, calendar_event: CalendarEvent) -> ClockodoIdMapping:
        raise NotImplementedError


class ClockodoColorIdResolutionService(ClockodoResolutionService):
    def resolve_from_event(self, calendar_event: CalendarEvent) -> ClockodoIdMapping:
        return self._resolve_from_color_id(calendar_event.color_id)

    def _resolve_from_color_id(self, color_id: int) -> ClockodoIdMapping:
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
            filter(lambda customer: customer['name'] == customer_name, self.api_connector.api_get_all('customers')),
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
            next(filter(lambda service: service['name'] == service_name, self.api_connector.api_get_all('services')),
                 {'id': 0})['id']
        if not service_id:
            raise ResolutionError(f'no mapping found for service [{service_name}]')
        return ClockodoIdMapping(customer_id, project_id, service_id, billable)


class ClockodoUrlResolutionService(ClockodoResolutionService):
    project_id_parameter: str = 'restrCstPrj[0]'
    service_id_parameter: str = 'restrService[0]'

    def __init__(self, api_connector: ClockodoApiConnector):
        super().__init__(api_connector)
        self.extractor = URLExtract()

    def resolve_from_event(self, calendar_event: CalendarEvent) -> ClockodoIdMapping:
        if not self.extractor.has_urls(calendar_event.description):
            raise ResolutionError(f'no URLs found in description of event[{calendar_event}]')

        clockodo_url = next(filter(lambda url: url.scheme == 'clockodo',
                                   map(lambda url_string: parse.urlparse(url_string),
                                       self.extractor.find_urls(calendar_event.description))), None)

        if not clockodo_url:
            raise ResolutionError(
                f'no URL with scheme [clockodo] found, just {self.extractor.find_urls(calendar_event.description)}')

        parsed_parameters = parse.parse_qs(clockodo_url.query, strict_parsing=True)
        if not (self.project_id_parameter in parsed_parameters and self.service_id_parameter in parsed_parameters):
            raise ResolutionError(
                f'failed to find {self.project_id_parameter} and {self.service_id_parameter} parameter in url, just {parsed_parameters}')

        # noinspection PyTypeChecker
        customer_id, project_id = parsed_parameters[self.project_id_parameter][0].split('-')
        # noinspection PyTypeChecker
        service_id = parsed_parameters[self.service_id_parameter][0]

        # noinspection PyTypeChecker
        billable = 'billable' not in parsed_parameters or int(parsed_parameters['billable'][0])
        return ClockodoIdMapping(int(customer_id), int(project_id), int(service_id), billable)
