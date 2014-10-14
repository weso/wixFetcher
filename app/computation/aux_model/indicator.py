__author__ = 'Miguel'


class Indicator(object):

    def __init__(self, code=None, label=None, _type=None, high_low=None, weight=None):
        self._code = code
        self._label = label
        self._type = _type
        self._high_low = high_low
        self._weight = weight
        self._means = dict()
        self._stdevs = dict()

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def high_low(self):
        return self._high_low

    @high_low.setter
    def high_low(self, value):
        self._high_low = value

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value

    @property
    def means(self):
        return self._means

    @means.setter
    def means(self, value):
        self._means = value

    @property
    def stdevs(self):
        return self._stdevs

    @stdevs.setter
    def stdevs(self, value):
        self._stdevs = value