from abc import ABC, abstractmethod
from datetime import datetime, date, time
from typing import Dict

import pytz

from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping


class GCalHandlingException(Exception):
    pass


class CalendarEventHandler(ABC):
    def accept(self, json_entry: CalendarEvent) -> bool:
        raise NotImplementedError

    def process(self, json_entry: Dict) -> CalendarEvent:
        raise NotImplementedError


class FailingCalendarEventHandler(CalendarEventHandler):

    def process(self, json_entry: Dict) -> CalendarEvent:
        raise GCalHandlingException(f"can't handle event: {json_entry}")

    def accept(self, json_entry: Dict) -> bool:
        return True


class CalenderEventBuilder(ABC):
    @classmethod
    def from_json_hourly(cls, json_entry: Dict):
        return HourlyCalenderEventBuilder(json_entry)

    @classmethod
    def from_json_daily(cls, json_entry: Dict):
        return DailyCalenderEventBuilder(json_entry)

    def __init__(self, json_entry: Dict):
        self.json_entry = json_entry
        self.entry = CalendarEvent()

    def with_summary(self):
        self.entry.summary = self.json_entry['summary']
        self.entry.description = self.json_entry.get('description', '')

        return self

    def with_persistence(self):
        self.entry.update_persistence_mapping(PersistenceMapping(self.json_entry['id']))
        return self

    def with_color_id(self):
        self.entry.color_id = int(self.json_entry.get('colorId', 0))
        return self

    def with_busy_state(self):
        self.entry.busy = self.json_entry.get('transparency', 'opaque') == 'opaque'
        return self

    def build(self):
        return self.entry

    def with_date_time(self):
        self._process_date_time()
        return self

    @abstractmethod
    def _process_date_time(self):
        raise NotImplementedError


class HourlyCalenderEventBuilder(CalenderEventBuilder):
    def _process_date_time(self):
        self.entry.start = datetime.fromisoformat(self.json_entry['start']['dateTime'])
        self.entry.end = datetime.fromisoformat(self.json_entry['end']['dateTime'])


class DailyCalenderEventBuilder(CalenderEventBuilder):
    def _process_date_time(self):
        local_timezone = pytz.timezone('Europe/Berlin')
        self.entry.start = local_timezone.localize(
            datetime.combine(date.fromisoformat(self.json_entry['start']['date']), time(0, 0)))
        self.entry.end = local_timezone.localize(
            datetime.combine(date.fromisoformat(self.json_entry['end']['date']), time(23, 59)))


class HourlyCalendarEventHandler(CalendarEventHandler):
    def accept(self, json_entry: Dict) -> bool:
        return 'dateTime' in json_entry.get('start') and 'dateTime' in json_entry.get(
            'end') and json_entry.get('summary')

    def process(self, json_entry: Dict) -> CalendarEvent:
        return CalenderEventBuilder.from_json_hourly(
            json_entry).with_persistence().with_date_time().with_summary().with_color_id().with_busy_state().build()


class DailyCalendarEventHandler(CalendarEventHandler):
    def accept(self, json_entry: Dict) -> bool:
        return 'date' in json_entry.get('start') and json_entry.get('summary')

    def process(self, json_entry: Dict) -> CalendarEvent:
        return CalenderEventBuilder.from_json_daily(
            json_entry).with_persistence().with_summary().with_color_id().with_date_time().with_busy_state().build()
