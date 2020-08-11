from datetime import datetime


class DayEntry(object):
    @classmethod
    def from_gcal(cls, event: dict):
        fromisoformat = datetime.fromisoformat(event['start']['dateTime'])
        date = fromisoformat.strftime('%d.%m.%Y')
        start = fromisoformat.strftime('%H:%M')
        end = datetime.fromisoformat(event['end']['dateTime']).strftime('%H:%M')
        return DayEntry(date, start, end, event['summary'], 'laut Beschreibung (Intern)')

    def __init__(self, date: str, start: str, end: str, comment: str, label: str):
        self.label = label
        self.comment = comment
        self.end = end
        self.start = start
        self.date = date
