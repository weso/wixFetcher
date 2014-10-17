__author__ = 'Miguel'


class Index(object):

    def __init__(self):
        self._label = "Index"
        self._subindexes = []

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