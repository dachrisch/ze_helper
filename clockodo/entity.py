from datetime import datetime


class ClockodoIdMapping(object):
    def __init__(self, customer_id: int, project_id: int, service_id: int, billable: int = 1):
        self.billable = billable
        self.service_id = service_id
        self.project_id = project_id
        self.customer_id = customer_id


class ClockodoDay(object):
    def __init__(self, start_date: datetime, end_date: datetime, comment: str, mapping: ClockodoIdMapping):
        self.comment = comment
        self.billable = mapping.billable
        self.service_id = mapping.service_id
        self.customer_id = mapping.customer_id
        self.project_id = mapping.project_id
        self.end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        self.start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')

    def __repr__(self):
        key_values = ','.join(map(lambda item: f'{item[0]}->{item[1]}', self.__dict__.items()))
        return f'{self.__class__.__name__}({key_values})'

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False
