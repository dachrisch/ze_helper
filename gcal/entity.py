from datetime import datetime


class DayEntry(object):

    def __init__(self, start=datetime.now(), end=datetime.now(), summary="", description="", color_id=0):
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

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        key_values = ','.join(map(lambda item: f'{item[0]}->{item[1]}', self.__dict__.items()))
        return f'{self.__class__}({key_values})'
