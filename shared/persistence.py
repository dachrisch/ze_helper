from shared.compare import ComparableMixin


class PersistenceMapping(ComparableMixin):
    def __init__(self, source_id):
        self.source_id = source_id


NO_MAPPING = PersistenceMapping(-1)


class PersistenceMappingMixin(object):
    def __init__(self):
        self.persistence_mapping = NO_MAPPING

    def has_persistence_mapping(self):
        return self.persistence_mapping is not NO_MAPPING

    def update_persistence_mapping(self, persistence_mapping: PersistenceMapping):
        self.persistence_mapping = persistence_mapping
