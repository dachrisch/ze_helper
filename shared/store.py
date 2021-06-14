from datetime import datetime
from typing import List, Dict

from clockodo.entity import ClockodoDay, ClockodoIdMapping
from gcal.entity import CalendarEvent
from shared.persistence import PersistenceMapping


class CalendarEventClockodoDayComparator(object):
    def __init__(self, calendar_event: CalendarEvent):
        self.calendar_event = calendar_event

    def is_similar(self, clockodo_day: ClockodoDay):
        start_date_string = self.calendar_event.start.strftime(ClockodoDay.DATE_FORMAT)
        end_date_string = self.calendar_event.end.strftime(ClockodoDay.DATE_FORMAT)
        return start_date_string == clockodo_day.start_date_str and end_date_string == clockodo_day.end_date_str and self.calendar_event.summary == clockodo_day.comment

    def find_matching(self, clockodo_days: List[ClockodoDay]):
        return next(filter(self.is_similar, clockodo_days))


class ClockodoDayStoreService(object):
    NOT_FOUND = ClockodoDay(datetime(1900, 1, 1), datetime(1900, 1, 1), 'not found', ClockodoIdMapping(-1, -1, -1))

    def __init__(self):
        self.calendar_id_to_clockodo: Dict[PersistenceMapping, List[ClockodoDay]] = {}

    def store(self, clockodo_day: ClockodoDay, calendar_event: CalendarEvent):
        if calendar_event.persistence_mapping in self.calendar_id_to_clockodo:
            self.calendar_id_to_clockodo[calendar_event.persistence_mapping].append(clockodo_day)
        else:
            self.calendar_id_to_clockodo[calendar_event.persistence_mapping] = [clockodo_day, ]

    def retrieve(self, calendar_event: CalendarEvent) -> ClockodoDay:
        clockodo_days = self.calendar_id_to_clockodo.get(calendar_event.persistence_mapping, (self.NOT_FOUND,))
        if len(clockodo_days) == 1:
            found_event = clockodo_days[0]
        else:
            found_event = CalendarEventClockodoDayComparator(calendar_event).find_matching(clockodo_days)
        return found_event
