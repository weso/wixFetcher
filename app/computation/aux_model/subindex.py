__author__ = 'Miguel'


class Subindex(object):

    def __init__(self, label=None, weight=None):
        self._label = label
        self._weight = weight
        self._components = []

    def add_component(self, component):
        self._components.append(component)

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
    def components(self):
        return self._components