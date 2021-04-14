from datetime import datetime

from shared.compare import ComparableMixin
from shared.persistence import PersistenceMappingMixin


class CalendarEvent(ComparableMixin, PersistenceMappingMixin):

    def __init__(self, start=datetime.now(), end=datetime.now(), summary="", description="", color_id=0):
        super().__init__()
        self.start = start
        self.end = end
        self.summary = summary
        self._description = description
        self.color_id = color_id

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value[:20]

    @property
    def duration(self):
        return self.end - self.start
