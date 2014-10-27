__author__ = 'Miguel'


class Index(object):

    def __init__(self):
        self._code = "INDEX"
        self._subindexes = []
        self._scored_values = dict()
        self._ranked_values = dict()

    def add_subindex(self, subindex):
        self._subindexes.append(subindex)

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def subindexes(self):
        return self._subindexes

    @property
    def scored_values(self):
        return self._scored_values

    @property
    def ranked_values(self):
        return self._ranked_values