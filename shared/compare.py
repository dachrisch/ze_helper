class ComparableMixin(object):

    def __repr__(self):
        key_values = ','.join(map(lambda item: f'{item[0]}->{item[1]}', self.__dict__.items()))
        return f'{self.__class__.__name__}({key_values})'

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class HashableMixin(ComparableMixin):

    def __hash__(self):
        return hash(tuple(map(lambda item: (item[0], item[1]), self.__dict__.items())))
