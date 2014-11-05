import xlrd

from utility.time import utc_now
from application.wixFetcher.app.computation.utils import *
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.area_repository import AreaRepository
from infrastructure.mongo_repos.observation_repository import ObservationRepository
from webindex.domain.model.observation.observation import *
from application.wixFetcher.app.parsers.utils import build_label_for_observation, build_observation_uri
from webindex.domain.model.observation.year import Year
from webindex.domain.model.observation.computation import *


__author__ = 'Miguel'


class ComputationParser(object):
    def __init__(self, log, config):
        self._log = log
        self._config = config
        self._indicator_repo = IndicatorRepository(self._config.get("CONNECTION", "MONGO_IP"))
        self._area_repo = AreaRepository(self._config.get("CONNECTION", "MONGO_IP"))
        self._observations_repo = ObservationRepository(self._config.get("CONNECTION", "MONGO_IP"))
        self._computations_sheet = xlrd.open_workbook(
            self._config.get("EXCEL", "COMPUTATIONS_FILE_NAME")).sheet_by_name(
            self._config.get("EXCEL", "COMPUTATIONS_SHEET_NAME"))

    def run(self):
        self._get_plain_observations_normalized_values()
        self._get_components_observations()
        self._get_subindexes_observations()
        self._get_index_observations()

    def _get_plain_observations_normalized_values(self):
        more_indicators = True
        i = 1
        indicators_row = int(self._config.get("EXCEL", "INDICATORS_START_ROW"))
        while more_indicators:
            if not self._computations_sheet.row(indicators_row)[i].value in ["", " ", None]:
                excel_indicator_code = str(self._computations_sheet.row(indicators_row)[i].value).replace(" ", "_")
                indicator_document = self._indicator_repo.find_indicators_by_code(excel_indicator_code)
                if not indicator_document["success"]:
                    self._log.warning(
                        "Computations parsing: Could not retrieve indicator {} from db".format(excel_indicator_code))
                else:
                    self._update_plain_observations(int(self._config.get("EXCEL", "NORMALIZED_VALUES_START_ROW")), i,
                                                    indicator_document["data"])
                i += 1
            else:
                more_indicators = False

    def _get_components_observations(self):
        components_document = self._indicator_repo.find_indicators_components()
        if not components_document["success"]:
            self._log.error("Computations parsing: Could not retrieve components from db")
            return
        more_components = True
        i = 1
        components_row = int(self._config.get("EXCEL", "COMPONENTS_START_ROW"))
        while more_components:
            if not self._computations_sheet.row(components_row)[i].value in ["", " ", None]:
                for component_document in components_document["data"]:
                    if is_same_component(component_document["name"],
                                         str(self._computations_sheet.row(components_row)[i].value)):
                        weight = float(
                            self._computations_sheet.row(int(self._config.get("EXCEL", "COMPONENTS_WEIGHTS_ROW")))[
                                i].value)
                        self._indicator_repo.update_indicator_weight(component_document["indicator"], weight)
                        self._insert_country_values(int(self._config.get("EXCEL", "COMPONENTS_VALUES_START_ROW")),
                                                    int(self._config.get("EXCEL",
                                                                         "COMPONENTS_SCORED_VALUES_START_ROW")),
                                                    i, component_document)
                i += 1
            else:
                more_components = False

    def _get_subindexes_observations(self):
        subindexes_document = self._indicator_repo.find_indicators_sub_indexes()
        if not subindexes_document["success"]:
            self._log("Computations parsing: Could not retrieve subindexes from db")
            return
        more_subindexes = True
        i = 1
        subindexes_row = int(self._config.get("EXCEL", "SUBINDEXES_START_ROW"))
        while more_subindexes:
            if not self._computations_sheet.row(subindexes_row)[i].value in ["", " ", "Overall Index-z-scores", None]:
                for subindex_document in subindexes_document["data"]:
                    if is_same_subindex(subindex_document["name"],
                                        str(self._computations_sheet.row(subindexes_row)[i].value)):
                        weight = float(
                            self._computations_sheet.row(int(self._config.get("EXCEL", "SUBINDEXES_WEIGHTS_ROW")))[
                                i].value)
                        self._indicator_repo.update_indicator_weight(subindex_document["indicator"], weight)
                        self._insert_country_values(int(self._config.get("EXCEL", "SUBINDEXES_VALUES_START_ROW")),
                                                    int(self._config.get("EXCEL",
                                                                         "SUBINDEXES_SCORED_VALUES_START_ROW")),
                                                    i, subindex_document)
                i += 1
            else:
                more_subindexes = False

    def _get_index_observations(self):
        indicator_document = self._indicator_repo.find_indicators_by_code("INDEX")
        if not indicator_document["success"]:
            self._log.error("Computations parsing: Could not retrieve INDEX indicator from db")
            return
        values_row = int(self._config.get("EXCEL", "INDEX_VALUES_START_ROW"))
        scored_values_column = int(self._config.get("EXCEL", "INDEX_SCORED_VALUES_COLUMN"))
        ranked_values_column = int(self._config.get("EXCEL", "INDEX_RANKED_VALUES_COLUMN"))
        self._insert_index_values(values_row, scored_values_column, ranked_values_column, indicator_document["data"])

    def _insert_index_values(self, start_row_value, scored_column, ranked_column,
                             indicator_document):
        countries_document = self._area_repo.find_countries("name")
        if not countries_document["success"]:
            self._log.error("Computations parsing: Could not retrieve countries from db")
            return
        i = start_row_value
        for country_document in countries_document["data"]:
            if is_same_country(country_document["name"], str(self._computations_sheet.row(i)[0].value)):
                scored_value = self._computations_sheet.row(i)[scored_column].value
                ranked_value = self._computations_sheet.row(i)[ranked_column].value
                if str(scored_value) not in ["", " ", None]:
                    if str(ranked_value) not in ["", " ", None]:
                        computation = Computation("ranked", float(ranked_value))
                    observation, observation_uri = self._create_obs_and_uri(indicator_document, country_document,
                                                                            scored_value, computation, "scored")

                    self._observations_repo.insert_observation(observation=observation,
                                                               observation_uri=observation_uri,
                                                               area_iso3_code=country_document["iso3"],
                                                               indicator_code=indicator_document["indicator"],
                                                               area_name=country_document["name"],
                                                               indicator_name=indicator_document["name"])
            else:
                for country_document_aux in countries_document["data"]:
                    if is_same_country(country_document_aux["name"],
                                       str(self._computations_sheet.row(i)[0].value)):
                        scored_value = self._computations_sheet.row(i)[scored_column].value
                        ranked_value = self._computations_sheet.row(i)[ranked_column].value
                        if str(scored_value) not in ["", " ", None]:
                            if str(ranked_value) not in ["", " ", None]:
                                computation = Computation("ranked", float(ranked_value))
                            observation, observation_uri = self._create_obs_and_uri(indicator_document,
                                                                                    country_document_aux, scored_value,
                                                                                    computation, "scored")
                            self._observations_repo.insert_observation(observation=observation,
                                                                       observation_uri=observation_uri,
                                                                       area_iso3_code=country_document_aux["iso3"],
                                                                       indicator_code=indicator_document["indicator"],
                                                                       area_name=country_document_aux["name"],
                                                                       indicator_name=indicator_document["name"])
            i += 1

    def _insert_country_values(self, start_row_value, start_row_scored, column, indicator_document):
        countries_document = self._area_repo.find_countries("name")
        if not countries_document["success"]:
            self._log("Computations parsing: Could not retrieve countries from db")
            return
        i = start_row_value
        j = start_row_scored
        for country_document in countries_document["data"]:
            if is_same_country(country_document["name"], str(self._computations_sheet.row(i)[0].value)):
                value = self._computations_sheet.row(i)[column].value
                scored_value = self._computations_sheet.row(j)[column].value
                if str(value) not in ["", " ", None]:
                    if str(scored_value) not in ["", " ", None]:
                        computation = Computation("scored", float(scored_value))
                    observation, observation_uri = self._create_obs_and_uri(indicator_document, country_document, value,
                                                                            computation, "normalized")

                    self._observations_repo.insert_observation(observation=observation,
                                                               observation_uri=observation_uri,
                                                               area_iso3_code=country_document["iso3"],
                                                               indicator_code=indicator_document["indicator"],
                                                               area_name=country_document["name"],
                                                               indicator_name=indicator_document["name"])
            else:
                for country_document_aux in countries_document["data"]:
                    if is_same_country(country_document_aux["name"],
                                       str(self._computations_sheet.row(i)[0].value)):
                        value = self._computations_sheet.row(i)[column].value
                        scored_value = self._computations_sheet.row(j)[column].value
                        if str(value) not in ["", " ", None]:
                            if str(scored_value) not in ["", " ", None]:
                                computation = Computation("scored", float(scored_value))
                            observation, observation_uri = self._create_obs_and_uri(indicator_document,
                                                                                    country_document_aux, value,
                                                                                    computation, "normalized")
                            self._observations_repo.insert_observation(observation=observation,
                                                                       observation_uri=observation_uri,
                                                                       area_iso3_code=country_document_aux["iso3"],
                                                                       indicator_code=indicator_document["indicator"],
                                                                       area_name=country_document_aux["name"],
                                                                       indicator_name=indicator_document["name"])
            i += 1
            j += 1

    def _update_plain_observations(self, start_row, column, indicator_document):
        countries_document = self._area_repo.find_countries("name")
        if not countries_document["success"]:
            self._log.error("Computations parsing: Could not retrieve countries from db")
            return
        i = start_row
        for country_document in countries_document["data"]:
            if is_same_country(country_document["name"], str(self._computations_sheet.row(i)[0].value)):
                value = self._computations_sheet.row(i)[column].value
                if str(value) not in ["", " ", None]:
                    self._observations_repo.normalize_plain_observation(country_document["iso3"],
                                                                        indicator_document["indicator"], "2014",
                                                                        float(value), "normalized")
            else:
                for country_document_aux in countries_document["data"]:
                    if is_same_country(country_document_aux["name"],
                                       str(self._computations_sheet.row(i)[0].value)):
                        value = self._computations_sheet.row(i)[column].value
                        if str(value) not in ["", " ", None]:
                            self._observations_repo.normalize_plain_observation(country_document_aux["iso3"],
                                                                                indicator_document["indicator"], "2014",
                                                                                float(value), "normalized")

            i += 1

    def _create_obs_and_uri(self, indicator_document, country_document, value, computation, obs_type):
        observation = create_observation(issued=utc_now(),
                                         publisher=None,
                                         data_set=None,
                                         obs_type=obs_type,  # Just for now
                                         label=build_label_for_observation(indicator_document["indicator"],
                                                                           country_document["name"],
                                                                           2014,
                                                                           obs_type),
                                         status=obs_type,
                                         ref_indicator=None,
                                         value=float(value),
                                         ref_area=None,
                                         ref_year=None, )
        if computation is not None:
            observation.add_computation(computation.comp_type, computation.value)
        observation._ref_year = Year(2014)
        observation_uri = build_observation_uri(self._config, indicator_document["indicator"], country_document["iso3"],
                                                2014)
        return observation, observation_uri