__author__ = 'Miguel'

import xlrd
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
        self._get_imputed_observations()
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

    def _get_imputed_observations(self):
        observations_document = self._observations_repo.find_observations(None, None, u"2013")
        sheets = self._get_imputed_data_sheets()
        if observations_document["success"]:
            observations_document = observations_document["data"]
            for observation_document in observations_document:
                observation = Observation(observation_document["indicator"], observation_document["area"],
                                          observation_document["year"], observation_document["value"])
                self._observations[observation_document["_id"]] = observation
                print "\t" + "Normalizando observacion " + observation.indicator_code + " " + observation.area + " " + observation.year
                observation.normalized_value = self._normalize_observation_value(observation, sheets)
                if observation.normalized_value is not None:
                    observation.weighed_value = self._apply_weight_to_observation_value(observation)

    def _normalize_observation_value(self, observation, sheets):
        normalized_value = 0
        indicator_document = self._indicator_repo.find_indicators_by_code(observation.indicator_code)
        if indicator_document["success"]:
            indicator_document = indicator_document["data"]
            mean, stdev = self._get_obs_mean_and_stdev(observation, indicator_document["type"], sheets)
            if indicator_document["high_low"] == "high":
                normalized_value = round((observation.value - mean) / stdev, 2)
            elif indicator_document["high_low"] == "low":
                normalized_value = round((mean - observation.value) / stdev, 2)
            else:
                self._log.error("Observation high/low field invalid: " + indicator_document["high_low"])
            return normalized_value
        else:
            self._log.error("Retrieving observation code indicator " + observation.indicator_code)

    def _apply_weight_to_observation_value(self, observation):
        indicator_document = self._indicator_repo.find_indicators_by_code(observation.indicator_code)
        if indicator_document["success"]:
            indicator_document = indicator_document["data"]
            if indicator_document["weight"] is not None:
                weighed_value = indicator_document["weight"] * observation.normalized_value
            else:
                weighed_value = observation.normalized_value
            return weighed_value
        else:
            self._log.error("Retrieving observation code indicator " + observation.indicator_code)

    def _get_obs_mean_and_stdev(self, observation, indicator_type, sheets):
        found = False
        if indicator_type == "Primary":
            for sheet in sheets:
                if "PrimaryIndicators" in str(sheet.name).replace(" ", "_"):
                    found = True
                    break
            if not found:
                self._log.error("Observation's indicator code " + observation.indicator_code +
                                " does not match with any of the Excel spreadsheets")
                return
            i = 0
            while i < sheet.ncols - 1:
                if (observation.year + "." + observation.indicator_code) in str(int(sheet.row(0)[i+1].value)):
                    mean = float(sheet.row(sheet.nrows - 3)[i].value)
                    stdev = float(sheet.row(sheet.nrows - 1)[i].value)
                    return mean, stdev
                i += 1
        elif indicator_type == "Secondary":
            for sheet in sheets:
                if observation.indicator_code in str(sheet.name).replace(" ", "_"):
                    found = True
                    break
            if not found:
                self._log.error("Observation's indicator code " + observation.indicator_code +
                                " does not match with any of the Excel spreadsheets")
                return
            i = 0
            while i < sheet.ncols - 1:
                if str(int(sheet.row(0)[i+1].value)) == observation.year:
                    mean = float(sheet.row(sheet.nrows - 5)[i].value)
                    stdev = float(sheet.row(sheet.nrows - 3)[i].value)
                    return mean, stdev
                i += 1

    def _calculate_component_grouped_value(self):
        areas_document = self._areas_repo.find_countries("name")
        if areas_document["success"]:
            areas_document = areas_document["data"]
            components_document = self._indicator_repo.find_indicators_components()
            if components_document["success"]:
                components_document = components_document["data"]
                for area_document in areas_document:
                    for component_document in components_document:
                        indicators_document = self._indicator_repo.find_indicator_children(component_document["indicator"])
                        if indicators_document["success"]:
                            indicators_document = indicators_document["data"]
                            _sum = 0
                            for indicator_document in indicators_document:
                                observation_document = self._observations_repo.find_observations(indicator_document["indicator"],
                                                                                                  area_document["iso3"],
                                                                                                  "2013")
                                if observation_document["success"]:
                                    observation_document = observation_document["data"]
                                    observation = self._observations[observation_document["_id"]]
                                    _sum += observation.weighed_value
                        component_mean = _sum / len(indicators_document)
                        component = self._components[component_document["_id"]]
                        component.grouped_values[area_document["iso3"]] = component_mean


    @staticmethod
    def _get_imputed_data_sheets():
        sheets = xlrd.open_workbook("./data_file.xlsx").sheets()
        return_sheets = []
        for sheet in sheets:
            match = re.match("[\w\d\s_-]+(imputed)$", sheet.name, re.I)
            if match:
                return_sheets.append(sheet)
        return return_sheets

    @staticmethod
    def _get_computations_sheet():
        return xlrd.open_workbook("./computations.xlsx").sheet_by_name("IndexComputation 2013")