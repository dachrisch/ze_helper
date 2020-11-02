import logging
from datetime import datetime


class DayEntry(object):
    log = logging.getLogger(__name__)

    @classmethod
    def from_gcal(cls, event: dict):
        fromisoformat = datetime.fromisoformat(event['start']['dateTime'])
        date = fromisoformat.strftime('%d.%m.%Y')
        start = fromisoformat.strftime('%H:%M')
        end = datetime.fromisoformat(event['end']['dateTime']).strftime('%H:%M')
        label = 'laut Beschreibung (Intern)'
        if event['summary'] == 'Kurzarbeit':
            label = 'Kurzarbeit (Intern)'
        elif 'colorId' in event:
            if event['colorId'] == '4':
                label = 'Durchführung (Workshops/Schulungen Pauschalpreis)'
            elif event['colorId'] == '6':
                label = 'Vor-/Nachbereitung (Workshops/Schulungen Pauschalpreis)'
        elif event['summary'] == 'Krank':
            label = 'Krankheit (aufMUC-Zelle)'
        return DayEntry(date, start, end, event['summary'], label)

    def __init__(self, date: str, start: str, end: str, comment: str, label: str):
        self.label = label
        self.comment = comment
        self.end = end
        self.start = start
        self.date = date

    def __repr__(self):
        return f'{self.__class__.__name__}({self.date}[{self.start}]-[{self.end}], {self.label}, {self.comment})'
