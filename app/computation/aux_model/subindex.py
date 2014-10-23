__author__ = 'Miguel'


class Subindex(object):

    def __init__(self, code=None, weight=None):
        self._code = code
        self._weight = weight
        self._components = []

    def add_component(self, component):
        self._components.append(component)

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
    def components(self):
        return self._components