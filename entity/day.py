import logging
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime


class DayEntry(ABC):
    log = logging.getLogger(__name__)

    @classmethod
    def from_gcal(cls, event: dict):
        entry = None
        if 'date' in event['start'] and event['summary'] == 'Urlaub':
            entry = VacationDayEntry(event['start']['date'])
        else:
            fromisoformat = datetime.fromisoformat(event['start']['dateTime'])
            date = fromisoformat.strftime('%d.%m.%Y')
            start = fromisoformat.strftime('%H:%M')
            end = datetime.fromisoformat(event['end']['dateTime']).strftime('%H:%M')
            if event['summary'] == 'Kurzarbeit':
                entry = ShorttimeDayEntry(date, start, end)
            elif 'colorId' in event:
                if event['colorId'] == '4':
                    entry = WorkshopDayEntry(date, start, end, event['summary'])
                elif event['colorId'] == '6':
                    entry = WorkshopPrepDayEntry(date, start, end, event['summary'])
                elif event['colorId'] == '3':
                    entry = CustomerDayEntry(date, start, end, event['summary'])
                elif event['colorId'] == '1':
                    entry = NonBillableCustomerDayEntry(date, start, end, event['summary'])
                else:
                    raise Exception(f"unknown color id [{event['colorId']}]")
            elif event['summary'] == 'Krank':
                entry = IllnessDayEntry(date, start, end)
            else:
                entry = InternalDayEntry(date, start, end, event['summary'])
        return entry

    @abstractmethod
    def __init__(self, date: str, start: str, end: str, comment: str, label: str):
        self.label = label
        self.comment = comment
        self.end = end
        self.start = start
        self.date = date

    def clone(self):
        return deepcopy(self)

    @property
    def timediff(self):
        return datetime.strptime(self.end, '%H:%M') - datetime.strptime(self.start, '%H:%M')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.date}[{self.start}]-[{self.end}], {self.label}, {self.comment})'


class VacationDayEntry(DayEntry):
    def __init__(self, date: str):
        super().__init__(date, date, date, 'Urlaub', 'Urlaub')


class ShorttimeDayEntry(DayEntry):
    def __init__(self, date: str, start: str, end: str):
        super().__init__(date, start, end, 'Kurzarbeit', 'Kurzarbeit (Intern)')


class WorkshopDayEntry(DayEntry):
    def __init__(self, date: str, start: str, end: str, comment: str):
        super().__init__(date, start, end, comment, 'Durchführung (Workshops/Schulungen Pauschalpreis)')


class WorkshopPrepDayEntry(DayEntry):
    def __init__(self, date: str, start: str, end: str, comment: str):
        super().__init__(date, start, end, comment, 'Vor-/Nachbereitung (Workshops/Schulungen Pauschalpreis)')


class CustomerDayEntry(DayEntry):
    def __init__(self, date: str, start: str, end: str, comment: str):
        super().__init__(date, start, end, comment, 'Laut Beschreibung & fakturierbar (Extern)')


class NonBillableCustomerDayEntry(DayEntry):
    def __init__(self, date: str, start: str, end: str, comment: str):
        super().__init__(date, start, end, comment, 'Laut Beschreibung & nicht-fakturierbar (Extern)')


class IllnessDayEntry(DayEntry):
    def __init__(self, date: str, start: str, end: str):
        super().__init__(date, start, end, 'Krank', 'Krankheit (aufMUC-Zelle)')


class InternalDayEntry(DayEntry):
    def __init__(self, date: str, start: str, end: str, comment: str):
        super().__init__(date, start, end, comment, 'laut Beschreibung (Intern)')
