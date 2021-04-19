from datetime import datetime

from shared.compare import ComparableMixin
from shared.persistence import PersistenceMappingMixin, PersistenceMapping, NO_MAPPING


class PrivateProperties(ComparableMixin):
    CLOCKODO_ID = 'clockodo_id'

    def __init__(self, private_properties: dict = {}):
        self.clockodo_id = private_properties.get(self.CLOCKODO_ID)

    def to_json(self):
        return {'private': {'clockodo_mapping':{'direct': {self.CLOCKODO_ID: self.clockodo_id}}}}

    @classmethod
    def from_mapping(cls, persistence_mapping: PersistenceMapping):
        return cls({cls.CLOCKODO_ID: persistence_mapping.source_id})


NO_PRIVATE_PROPERTIES = PrivateProperties()


class CalendarEvent(ComparableMixin, PersistenceMappingMixin):

    def __init__(self, start=datetime.now(), end=datetime.now(), summary='', description='', color_id=0,
                 private_properties=NO_PRIVATE_PROPERTIES, persistence_mapping=NO_MAPPING):
        super().__init__(persistence_mapping)
        self.start = start
        self.end = end
        self.summary = summary
        self._description = description
        self.color_id = color_id
        self.private_properties = private_properties

    def replace(self, start=None, end=None, summary=None, description=None, color_id=None, private_properties=None,
                persistence_mapping=None):
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
        if private_properties is None:
            private_properties = self.private_properties
        if persistence_mapping is None:
            persistence_mapping = self.persistence_mapping

        return type(self)(start, end, summary, description, color_id, private_properties, persistence_mapping)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value[:20]

    @property
    def duration(self):
        return self.end - self.start
