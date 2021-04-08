from abc import ABC
from datetime import datetime, date, time

import pytz

from gcal.entity import DayEntry


class GCalHandlingException(Exception):
    pass


class DayEntryHandler(ABC):
    def accept(self, json_entry: DayEntry) -> bool:
        raise NotImplementedError

    def process(self, json_entry: dict) -> DayEntry:
        raise NotImplementedError


class FailingDayEntryHandler(DayEntryHandler):

    def process(self, json_entry: dict) -> DayEntry:
        raise GCalHandlingException(f"can't handle event: {json_entry}")

    def accept(self, json_entry: dict) -> bool:
        return True


class HourlyDayEntryHandler(DayEntryHandler):
    def accept(self, json_entry: dict) -> bool:
        return 'dateTime' in json_entry.get('start') and 'dateTime' in json_entry.get(
            'end') and json_entry.get('summary')

    def process(self, json_entry: dict) -> DayEntry:
        entry = DayEntry()
        entry.start = datetime.fromisoformat(json_entry['start']['dateTime'])
        entry.end = datetime.fromisoformat(json_entry['end']['dateTime'])
        entry.summary = json_entry['summary']
        entry.color_id = int(json_entry.get('colorId', 0))
        entry.description = json_entry.get('description', '')
        return entry


class MultiDayEntryHandler(DayEntryHandler):
    def accept(self, json_entry: dict) -> bool:
        return 'date' in json_entry.get('start') and json_entry.get('summary')

    def process(self, json_entry: dict) -> DayEntry:
        entry = DayEntry()
        local_timezone = pytz.timezone('Europe/Berlin')
        entry.start = local_timezone.localize(
            datetime.combine(date.fromisoformat(json_entry['start']['date']), time(0, 0)))
        entry.end = local_timezone.localize(
            datetime.combine(date.fromisoformat(json_entry['end']['date']), time(23, 59)))
        entry.summary = json_entry['summary']
        return entry
