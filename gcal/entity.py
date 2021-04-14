from datetime import datetime

from shared.compare import ComparableMixin
from shared.persistence import PersistenceMappingMixin


class PrivateProperties(ComparableMixin):
    def __init__(self, private_properties: dict = {}):
        self.clockodo_id = private_properties.get('clockodo_id')


NO_PRIVATE_PROPERTIES = PrivateProperties()


class CalendarEvent(ComparableMixin, PersistenceMappingMixin):

    def __init__(self, start=datetime.now(), end=datetime.now(), summary='', description='', color_id=0,
                 private_properties=NO_PRIVATE_PROPERTIES):
        super().__init__()
        self.start = start
        self.end = end
        self.summary = summary
        self._description = description
        self.color_id = color_id
        self.private_properties = private_properties

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value[:20]

    @property
    def duration(self):
        return self.end - self.start
