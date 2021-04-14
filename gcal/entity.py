from datetime import datetime


class MappingInfo(object):
    def __init__(self, source_id, target_id):
        self.target_id = target_id
        self.source_id = source_id

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


    def __repr__(self):
        key_values = ','.join(map(lambda item: f'{item[0]}->{item[1]}', self.__dict__.items()))
        return f'{self.__class__}({key_values})'

NO_MAPPING_INFO = MappingInfo(-1, -1)


class CalendarEvent(object):

    def __init__(self, start=datetime.now(), end=datetime.now(), summary="", description="", color_id=0,
                 mapping_info=NO_MAPPING_INFO):
        self.start = start
        self.end = end
        self.summary = summary
        self._description = description
        self.color_id = color_id
        self.mapping_info = mapping_info

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value[:20]

    @property
    def duration(self):
        return self.end - self.start

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        key_values = ','.join(map(lambda item: f'{item[0]}->{item[1]}', self.__dict__.items()))
        return f'{self.__class__}({key_values})'

    def has_mapping_info(self):
        return self.mapping_info is not NO_MAPPING_INFO

    def update_mapping_info(self, mapping_info:MappingInfo):
        self.mapping_info=mapping_info
