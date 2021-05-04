from datetime import datetime

from shared.compare import HashableMixin
from shared.persistence import PersistenceMappingMixin, NO_MAPPING


class CalendarEvent(HashableMixin, PersistenceMappingMixin):

    def __init__(self, start=datetime.now(), end=datetime.now(), summary='', description='', color_id=0,
                 persistence_mapping=NO_MAPPING, busy=True):
        super().__init__(persistence_mapping)
        self.busy = busy
        self.start = start
        self.end = end
        self.summary = summary
        self._description = description
        self.color_id = color_id

    def replace(self, start=None, end=None, summary=None, description=None, color_id=None, persistence_mapping=None,
                busy=None):
        if start is None:
            start = self.start
        if end is None:
            end = self.end
        if summary is None:
            summary = self.summary
        if description is None:
            description = self.description
        if color_id is None:
            color_id = self.color_id
        if persistence_mapping is None:
            persistence_mapping = self.persistence_mapping
        if busy is None:
            busy = self.busy

        return type(self)(start, end, summary, description, color_id, persistence_mapping, busy)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value[:20]

    @property
    def duration(self):
        return self.end - self.start
