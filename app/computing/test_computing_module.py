from unittest import TestCase
from webindex.domain.model.observation.observation import *
from application.wixFetcher.app.computing.computing_module import ComputingModule
from application.wixFetcher.app.util.observation_util import ObservationUtil
from utility.time import utc_now
import logging
from random import shuffle


__author__ = 'Miguel'
__date__ = '17/09/2014'


class TestComputingModule(TestCase):

    def setUp(self):
        self._create_observations()
        self._computing_module = ComputingModule(None)

    def tearDown(self):
        pass

    def _create_observations(self):
        self._raw_observations = []
        self._normalized_observations = []
        raw_values = [5.5, 6, 5, 3, 8.3, 5, 1, 2, 1]
        normalized_values = [1.04, 0.18, 0.58, -0.07, 0.9, 0.58, -0.96, -1.08, -1.16]
        means = [3.16, 5.43, 3.66]
        stds = [2.25, 3.18, 2.3]
        ref_indicators = ["ITU_O", "ITU_G", "ITU_A"]
        ref_areas = ["SPA", "FRA", "ENG"]
        ref_years = [2007, 2008, 2009]

        for ref_indicator in ref_indicators:
            j = 0
            for ref_area in ref_areas:
                k = 0
                for ref_year in ref_years:
                    raw_observation = create_observation(ref_area=ref_area, ref_indicator=ref_indicator,
                                                         ref_year=ref_year, value=raw_values[j])
                    raw_observation.add_computation(_type="raw", mean=means[k], std_deviation=stds[k])
                    self._raw_observations.append(raw_observation)
                    normalized_observation = create_observation(ref_area=ref_area, ref_indicator=ref_indicator,
                                                                ref_year=ref_year, value=normalized_values[j])
                    normalized_observation.add_computation(_type="normalized")
                    self._normalized_observations.append(normalized_observation)
                    j += 1
                    k += 1

    def test_validate_observations(self):
        pass

    def test__find_equivalent_version(self):
        i = 0
        while i < len(self._raw_observations):
            current = self._raw_observations[i]
            normalized_version = self._computing_module._find_equivalent_version(current, self._normalized_observations)
            self.assertTrue(ObservationUtil.are_equivalent_observations(current, normalized_version))
            i += 1

    def test__classify_observations_by_computation_type(self):
        observations = self._raw_observations + self._normalized_observations
        shuffle(observations)
        raw_observations = self._computing_module._classify_observations_by_computation_type(observations, "raw")
        normalized_observations = self._computing_module._classify_observations_by_computation_type(observations,
                                                                                                    "normalized")
        self.assertEqual(len(raw_observations), len(self._raw_observations))
        self.assertEqual(len(normalized_observations), len(self._normalized_observations))

        for observation in raw_observations:
            self.assertTrue(observation.computation.type == "raw")

        for observation in normalized_observations:
            self.assertTrue(observation.computation.type == "normalized")

    def test__normalize_observation_value(self):
        i = 0
        while i < len(self._raw_observations):
            self.assertEqual(self._computing_module._normalize_observation_value(self._raw_observations[i]),
                             self._normalized_observations[i].value)
            i += 1