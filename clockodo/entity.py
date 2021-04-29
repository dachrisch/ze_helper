from datetime import datetime

from shared.compare import HashableMixin
from shared.persistence import PersistenceMappingMixin


class ClockodoIdMapping(HashableMixin):
    def __init__(self, customer_id: int, project_id: int, service_id: int, billable: int = 1):
        self.billable = billable
        self.service_id = service_id
        self.project_id = project_id
        self.customer_id = customer_id


class ClockodoDay(HashableMixin, PersistenceMappingMixin):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, start_date: datetime, end_date: datetime, comment: str, id_mapping: ClockodoIdMapping):
        super().__init__()
        self.comment = comment
        self.id_mapping = id_mapping
        self.end_date_str = end_date.strftime(self.DATE_FORMAT)
        self.start_date_str = start_date.strftime(self.DATE_FORMAT)

    @property
    def billable(self):
        return self.id_mapping.billable

    @property
    def service_id(self):
        return self.id_mapping.service_id

    @property
    def customer_id(self):
        return self.id_mapping.customer_id

    @property
    def project_id(self):
        return self.id_mapping.project_id
