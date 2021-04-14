from datetime import datetime

from shared.compare import ComparableMixin
from shared.persistence import PersistenceMappingMixin, PersistenceMapping


class PrivateProperties(ComparableMixin):
    CLOCKODO_ID = 'clockodo_id'

    def __init__(self, private_properties: dict = {}):
        self.clockodo_id = private_properties.get(self.CLOCKODO_ID)

    def to_json(self):
        return {'private': {self.CLOCKODO_ID: self.clockodo_id}}

    @classmethod
    def from_mapping(cls, persistence_mapping: PersistenceMapping):
        return cls({cls.CLOCKODO_ID: persistence_mapping.source_id})


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
