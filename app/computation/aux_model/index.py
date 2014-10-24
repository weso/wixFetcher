__author__ = 'Miguel'


class Index(object):

    def __init__(self):
        self._label = "INDEX"
        self._subindexes = []
        self._scored_values = dict()
        self._ranked_values = dict()

    def add_subindex(self, subindex):
        self._subindexes.append(subindex)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def subindexes(self):
        return self._subindexes

    @property
    def scored_values(self):
        return self._scored_values

    @property
    def ranked_values(self):
        return self._ranked_values