__author__ = 'Miguel'


class Component(object):

    def __init__(self, code=None, weight=None):
        self._code = code
        self._weight = weight
        self._indicators = []
        self._grouped_values = dict()

    def add_indicator(self, indicator):
        self._indicators.append(indicator)

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

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
