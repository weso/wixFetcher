from unittest import TestCase

__author__ = 'Miguel'
__date__ = '16/09/2014'

from webindex.domain.model.observation.observation import *


class TestComputingModule(TestCase):

    _first_execution = True

    def setUp(self):
        if self._first_execution:
            self._create_observations()
            self._first_execution = False

    def tearDown(self):
        pass

    def _create_observations(self):
        self._raw_observations = []
        self._normalized_observations = []
        self._scored_observations = []
        i = 0
        while i < 10:
            observation = create_observation(label="Observation " + str(i))
            self._raw_observations.append(observation)
            i += 1

    def test_validate_observations(self):
        self.fail()

    def test__normalize_value(self):
        self.fail()

    def test__compute_value(self):
        self.fail()