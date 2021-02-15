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

    def __str__(self):
        return f"({self.customer_id})[from={self.start_date_str}, to={self.end_date_str}, comment={self.comment}]"
