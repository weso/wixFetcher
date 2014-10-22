__author__ = 'Miguel'


class Observation(object):

    def __init__(self, indicator_code=None, area=None, year=None, value=None, normalized_value=None,
                 weighed_value=None):
        self._indicator_code = indicator_code
        self._area = area
        self._year = year
        self._value = value
        self._normalized_value = normalized_value
        self._weighed_value = weighed_value

    @property
    def indicator_code(self):
        return self._indicator_code

    @indicator_code.setter
    def indicator_code(self, value):
        self._indicator_code = value

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, value):
        self._area = value

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        self._year = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def normalized_value(self):
        return self._normalized_value

    @normalized_value.setter
    def normalized_value(self, value):
        self._normalized_value = value

    @property
    def weighed_value(self):
        return self._weighed_value

    @weighed_value.setter
    def weighed_value(self, value):
        self._weighed_value = value