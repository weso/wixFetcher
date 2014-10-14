__author__ = 'Miguel'


class Component(object):

    def __init__(self, label=None, weight=None):
        self._label = label
        self._weight = weight
        self._indicators = []
        self._grouped_values = dict()

    def add_indicator(self, indicator):
        self._indicators.append(indicator)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value

    @property
    def indicators(self):
        return self._indicators

    @property
    def grouped_values(self):
        return self._grouped_values
