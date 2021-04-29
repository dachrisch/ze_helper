import base64
import hashlib
import json

import smaz as smaz

from shared.compare import ComparableMixin, HashableMixin


class PersistenceMapping(HashableMixin):
    def __init__(self, source_id):
        self.source_id = source_id

    def to_json_str(self):
        return json.dumps({'source_id': self.source_id})


NO_MAPPING = PersistenceMapping(-1)


class PersistenceMappingMixin(object):
    def __init__(self, persistence_mapping=NO_MAPPING):
        self.persistence_mapping = persistence_mapping

    def has_persistence_mapping(self):
        return self.persistence_mapping is not NO_MAPPING

    def update_persistence_mapping(self, persistence_mapping: PersistenceMapping):
        self.persistence_mapping = persistence_mapping

