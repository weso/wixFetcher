__author__ = 'Miguel'

import xlrd
import numpy
import re
from ..util.excel_util import ExcelUtil
from ..util.utils import *
from aux_model.index import Index
from aux_model.subindex import Subindex
from aux_model.component import Component
from aux_model.indicator import Indicator
from aux_model.observation import Observation
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.observation_repository import ObservationRepository
from infrastructure.mongo_repos.area_repository import AreaRepository


class ComputationModule(object):
    def __init__(self, log):
        self._log = log
        self._indicator_repo = IndicatorRepository("localhost")
        self._observations_repo = ObservationRepository("localhost")
        self._areas_repo = AreaRepository("localhost")
        self._observations = dict()
        self._components = dict()

    def run(self):
        print "Inicializando indice"
        self._initialize_index()
        print "Cogiendo observaciones"
        self._get_imputed_observations(u"2014")  # TODO: Remember to change this (ask Hania)
        print "Agrupando en componentes"
        self._calculate_component_grouped_value()
        print "Fin :)"

    def _initialize_index(self):
        self._index = Index()
        subindexes = self._indicator_repo.find_indicators_sub_indexes()
        if subindexes["success"]:
            for subindex in subindexes["data"]:
                subindex_object = Subindex(subindex["indicator"])
                self._index.add_subindex(subindex_object)
                components = self._indicator_repo.find_indicators_components(subindex)
                for component in components["data"]:
                    component_object = Component(component["indicator"])
                    subindex_object.add_component(component_object)
                    self._components[component["_id"]] = component_object
                    indicators = self._indicator_repo.find_indicators_indicators(component)
                    for indicator in indicators["data"]:
                        indicator_object = Indicator(indicator["indicator"], indicator["name"], indicator["type"],
                                                     indicator["high_low"], indicator["weight"])
                        component_object.add_indicator(indicator_object)

    def _get_imputed_observations(self, year):
        indicators_document = self._indicator_repo.find_indicators_indicators()
        if not indicators_document["success"]:
            self._log.error("Could not get indicators from db")
            return
        indicators_document = indicators_document["data"]
        for indicator_document in indicators_document:
            year = u'2014'
            observations_document = self._observations_repo.find_observations(indicator_document["indicator"],
                                                                              None, year)
            if len(observations_document["data"]) == 0:
                year = u'2013'
                observations_document = self._observations_repo.find_observations(indicator_document["indicator"],
                                                                              None, year)
            if not observations_document["success"]:
                self._log.error("Could not get observations of " + indicator_document["indicator"]
                                + " indicator from db for year " + year)
                return
            if len(observations_document["data"]) > 0:
                mean, stdev = self._get_obs_mean_and_stdev(indicator_document["indicator"], year)
                observations_document = observations_document["data"]
                print "\tIndicador " + indicator_document["indicator"] + ". " + str(len(observations_document)) + " observaciones"
                for observation_document in observations_document:
                    observation = Observation(observation_document["indicator"], observation_document["area"],
                                              observation_document["year"], observation_document["value"])
                    self._observations[observation_document["_id"]] = observation
                    print "\t\t" + "Normalizando observacion " + observation.indicator_code + " " + observation.area + " " + observation.year
                    observation.normalized_value = self._normalize_observation_value(observation, mean, stdev)
                    if observation.normalized_value is not None:
                        observation.weighed_value = self._apply_weight_to_observation_value(observation)
                        print "\t\t\t" + str(observation.normalized_value) + "   " + str(observation.weighed_value)
            else:
                self._log.warning("There are no observations of " + indicator_document["indicator"]
                                  + " indicator for year " + year)

    def _normalize_observation_value(self, observation, mean, stdev):
        normalized_value = 0
        indicator_document = self._indicator_repo.find_indicators_by_code(observation.indicator_code)
        if not indicator_document["success"]:
            self._log.error("Could not get observation's indicator code " + observation.indicator_code)
            return
        indicator_document = indicator_document["data"]
        if indicator_document["high_low"] == "high":
            normalized_value = (observation.value - mean) / stdev
        elif indicator_document["high_low"] == "low":
            normalized_value = (mean - observation.value) / stdev
        else:
            self._log.error("Observation high/low field invalid: " + indicator_document["high_low"])
        return normalized_value

    def _apply_weight_to_observation_value(self, observation):
        indicator_document = self._indicator_repo.find_indicators_by_code(observation.indicator_code)
        if not indicator_document["success"]:
            self._log.error("Could not get observation's indicator code " + observation.indicator_code)
            return
        indicator_document = indicator_document["data"]
        weighed_value = indicator_document["weight"] * observation.normalized_value
        return weighed_value

    def _get_obs_mean_and_stdev(self, indicator_code, year):
        observations_document = self._observations_repo.find_observations(indicator_code, None, year)
        if not observations_document["success"]:
            self._log.error("Could not get observations of " + indicator_code + " indicator from db for year " + year)
            return
        observations_document = observations_document["data"]
        values = []
        for observation_document in observations_document:
            values.append(float(observation_document["value"]))
        mean = numpy.mean(values, 0)
        stdev = numpy.std(values, 0)
        print "\tMean: " + str(mean)
        print "\tSTD: " + str(stdev)
        return mean, stdev

    def _calculate_component_grouped_value(self):
        areas_document = self._areas_repo.find_countries("name")
        if areas_document["success"]:
            areas_document = areas_document["data"]
            components_document = self._indicator_repo.find_indicators_components()
            if components_document["success"]:
                components_document = components_document["data"]
                for area_document in areas_document:
                    for component_document in components_document:
                        indicators_document = self._indicator_repo.find_indicator_children(
                            component_document["indicator"])
                        _sum = 0
                        for indicator_document in indicators_document:
                            observation_document = self._observations_repo.find_observations(
                                indicator_document["indicator"],
                                area_document["iso3"],
                                "2013")
                            if observation_document["success"]:
                                observation_document = observation_document["data"][0]
                                observation = self._observations[observation_document["_id"]]
                                _sum += observation.weighed_value
                        component_mean = _sum / len(indicators_document)
                        component = self._components[component_document["_id"]]
                        component.grouped_values[area_document["iso3"]] = component_mean

    @staticmethod
    def _get_imputed_data_sheets():
        return xlrd.open_workbook("./data_file.xlsx").sheets()

    @staticmethod
    def _get_computations_sheet():
        return xlrd.open_workbook("./computations.xlsx").sheet_by_name("IndexComputation 2013")