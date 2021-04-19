import base64
import hashlib
import json

import smaz as smaz

from shared.compare import ComparableMixin


class PersistenceMapping(ComparableMixin):
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


class StringCompressor(object):
    @staticmethod
    def compress(string: str) -> bytes:
        return smaz.compress(string)


class Base64StringConverter(object):
    @staticmethod
    def encode(bytes_string: bytes) -> str:
        return base64.b64encode(bytes_string).decode('utf-8')


class MD5SumStringConverter(object):
    @staticmethod
    def encode(bytes_string: bytes) -> str:
        return hashlib.md5(bytes_string).hexdigest()


class PersistenceMappingConverter(object):
    @staticmethod
    def to_secure_string(persistence_mapping: PersistenceMapping):
        persistence_string = persistence_mapping.to_json_str()
        compressed = StringCompressor.compress(persistence_string)
        encoded_persistence = Base64StringConverter.encode(compressed)
        md5_hash = MD5SumStringConverter.encode(compressed)
        return f'{encoded_persistence}, {md5_hash}'
