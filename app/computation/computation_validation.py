from __future__ import division
__author__ = 'Miguel'


import xlrd
import numpy
import operator
from aux_model.index import Index
from aux_model.subindex import Subindex
from aux_model.component import Component
from aux_model.indicator import Indicator
from aux_model.observation import Observation
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.observation_repository import ObservationRepository
from infrastructure.mongo_repos.area_repository import AreaRepository


class ComputationValidation(object):
    def __init__(self, log):
        self._log = log
        self._indicator_repo = IndicatorRepository("localhost")
        self._observations_repo = ObservationRepository("localhost")
        self._areas_repo = AreaRepository("localhost")
        self._observations = dict()
        self._components = dict()
        self._subindexes = dict()

    def run(self):
        print "Inicializando indice"
        self._initialize_index()
        print "Cogiendo observaciones"
        self._get_imputed_observations(u"2013")
        print "\n\nAgrupando en componentes"
        self._calculate_component_grouped_value(u"2013")
        print "\n\nScoreando en componentes"
        self._calculate_component_scored_value(u"2013")
        print "\n\nAgrupando en subindices"
        self._calculate_subindex_grouped_value(u"2013")
        print "\n\nScoreando en subindices"
        self._calculate_subindex_scored_value(u"2013")
        print "\n\nCalculando indice"
        self._calculate_index(u"2013")

    def _initialize_index(self):
        self._index = Index()
        subindexes_document = self._indicator_repo.find_indicators_sub_indexes()
        if not subindexes_document["success"]:
            self._log.error("Could not retrieve subindexes from db")
            return
        print "INDEX"
        for subindex_document in subindexes_document["data"]:
            subindex = Subindex(subindex_document["indicator"], subindex_document["weight"])
            self._index.add_subindex(subindex)
            self._subindexes[subindex_document["_id"]] = subindex
            components_document = self._indicator_repo.find_indicators_components(subindex_document)
            print "\t" + subindex.code
            if not components_document["success"]:
                self._log("Could not retrieve components from db")
                return
            for component_document in components_document["data"]:
                component = Component(component_document["indicator"], component_document["weight"])
                subindex.add_component(component)
                self._components[component_document["_id"]] = component
                indicators_document = self._indicator_repo.find_indicators_indicators(component_document)
                if not indicators_document["success"]:
                    self._log("Could not retrieve indicators from db")
                    return
                print "\t\t" + component.code
                for indicator_document in indicators_document["data"]:
                    indicator = Indicator(indicator_document["indicator"], indicator_document["name"],
                                          indicator_document["type"], indicator_document["high_low"],
                                          indicator_document["weight"])
                    component.add_indicator(indicator)
                    print "\t\t\t" + indicator.code

    def _get_imputed_observations(self, year):
        indicators_document = self._indicator_repo.find_indicators_indicators()
        if not indicators_document["success"]:
            self._log.error("Could not get indicators from db")
            return
        indicators_document = indicators_document["data"]
        for indicator_document in indicators_document:
            observations_document = self._observations_repo.find_observations(indicator_document["indicator"],
                                                                              None, year)
            if not observations_document["success"]:
                self._log.error("Could not get observations of " + indicator_document["indicator"]
                                + " indicator from db for year " + year)
                return
            if len(observations_document["data"]) > 0:
                observations_document = observations_document["data"]
                mean, stdev = self._get_obs_mean_and_stdev(observations_document)
                print "\tIndicador " + indicator_document["indicator"] + ". " + str(len(observations_document)) + " observaciones"
                for observation_document in observations_document:
                    observation = Observation(observation_document["indicator"], observation_document["area"],
                                              observation_document["year"], observation_document["value"])
                    self._observations[observation_document["_id"]] = observation
                    print "\t\t" + "Normalizando observacion " + observation.indicator_code + " " + observation.area + " " + observation.year
                    observation.normalized_value = self._normalize_observation_value(observation, mean, stdev)
                    if (observation_document["normalized"] - 0.07) <= observation.normalized_value \
                            <= (observation_document["normalized"] + 0.07):
                        observation.normalized_value = observation_document["normalized"]
                    else:
                        print "MIERDAAAAA"
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

    @staticmethod
    def _get_obs_mean_and_stdev(observations_document):
        values = []
        for observation_document in observations_document:
            values.append(float(observation_document["value"]))
        mean = numpy.mean(values, 0)
        stdev = numpy.std(values, 0)
        print "\tMean: " + str(mean)
        print "\tSTD: " + str(stdev)
        return mean, stdev

    def _calculate_component_grouped_value(self, year):
        areas_document = self._areas_repo.find_countries("name")
        components_document = self._indicator_repo.find_indicators_components()
        if not areas_document["success"]:
            self._log.error("Could not retrieve areas from db")
            return
        if not components_document["success"]:
            self._log.error("Could not retrieve components from db")
            return
        areas_document = areas_document["data"]
        components_document = components_document["data"]
        for area_document in areas_document:
            print area_document["iso3"]
            for component_document in components_document:
                indicators_document = self._indicator_repo.find_indicator_children(component_document["indicator"])
                _sum = 0
                unused_count = 0
                for indicator_document in indicators_document:
                    observation_document = self._observations_repo.find_observations(
                        indicator_document["indicator"],
                        area_document["iso3"],
                        year)
                    if observation_document["success"] and len(observation_document["data"]) > 0:
                        observation_document = observation_document["data"][0]
                        observation = self._observations[observation_document["_id"]]
                        if observation.normalized_value != 0.0 or indicator_document["indicator"] == "S1":
                            _sum += observation.weighed_value
                        else:
                            unused_count += 1
                    elif len(observation_document["data"]) == 0:
                        unused_count += 1
                component_mean = _sum / (len(indicators_document) - unused_count)
                print "\t" + component_document["indicator"] + ": " + str(component_mean) + "   " + str(_sum) + "   " + str(len(indicators_document) - unused_count)
                component = self._components[component_document["_id"]]
                component.grouped_values[area_document["iso3"]] = component_mean

    def _calculate_component_scored_value(self, year):
        areas_document = self._areas_repo.find_countries("name")
        if not areas_document["success"]:
            self._log.error("Could not retrieve areas from db")
            return
        for component in self._components.values():
            _max = max(component.grouped_values.values())
            _min = min(component.grouped_values.values())
            _range = _max - _min
            print "\t" + component.code
            for area_document in areas_document["data"]:
                value = component.grouped_values[area_document["iso3"]]
                component.scored_values[area_document["iso3"]] = (value - _min) / _range * 100
                print "\t\t" + area_document["iso3"] + "   " + str(_max) + " " + str(_min) + " " + str(_range) + "    " + str((value - _min) / _range * 100)

    def _calculate_subindex_grouped_value(self, year):
        areas_document = self._areas_repo.find_countries("name")
        subindexes_document = self._indicator_repo.find_indicators_sub_indexes()
        if not areas_document["success"]:
            self._log.error("Could not retrieve areas from db")
            return
        if not subindexes_document["success"]:
            self._log.error("Could not retrieve components from db")
            return
        areas_document = areas_document["data"]
        subindexes_document = subindexes_document["data"]
        for area_document in areas_document:
            print area_document["iso3"]
            for subindex_document in subindexes_document:
                components_document = self._indicator_repo.find_indicator_children(subindex_document["indicator"])
                _sum = 0
                for component_document in components_document:
                    component = self._components[component_document["_id"]]
                    _sum += component.grouped_values[area_document["iso3"]] * component.weight
                subindex_mean = _sum
                print "\t" + subindex_document["indicator"] + ": " + str(subindex_mean)
                subindex = self._subindexes[subindex_document["_id"]]
                subindex.grouped_values[area_document["iso3"]] = subindex_mean

    def _calculate_subindex_scored_value(self, year):
        areas_document = self._areas_repo.find_countries("name")
        if not areas_document["success"]:
            self._log.error("Could not retrieve areas from db")
            return
        for subindex in self._subindexes.values():
            _max = max(subindex.grouped_values.values())
            _min = min(subindex.grouped_values.values())
            _range = _max - _min
            print "\t" + subindex.code
            for area_document in areas_document["data"]:
                value = subindex.grouped_values[area_document["iso3"]]
                subindex.scored_values[area_document["iso3"]] = (value - _min) / _range * 100
                print "\t\t" + area_document["iso3"] + "   " + str(_max) + " " + str(_min) + " " + str(_range) + "    " + str((value - _min) / _range * 100)

    def _calculate_index(self, year):
        areas_document = self._areas_repo.find_countries("name")
        subindexes = self._index.subindexes
        if not areas_document["success"]:
            self._log.error("Could not retrieve areas from db")
            return
        for area_document in areas_document["data"]:
            _sum = 0
            for subindex in subindexes:
                _sum += subindex.grouped_values[area_document["iso3"]] * subindex.weight
            self._index.scored_values[area_document["iso3"]] = _sum
        _max = max(self._index.scored_values.values())
        _min = min(self._index.scored_values.values())
        _range = _max - _min
        for area_document in areas_document["data"]:
            value = self._index.scored_values[area_document["iso3"]]
            self._index.scored_values[area_document["iso3"]] = (value - _min) / _range * 100
            print "\t\t" + area_document["iso3"] + "   " + str(_max) + " " + str(_min) + " " + str(_range) + "    " + str((value - _min) / _range * 100)

