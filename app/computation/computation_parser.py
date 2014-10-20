__author__ = 'Miguel'

from application.wixFetcher.app.computation.utils import *
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.area_repository import AreaRepository
from infrastructure.mongo_repos.observation_repository import ObservationRepository


class ComputationParser(object):

    def __init__(self, log, config):
        self._log = log
        self._config = config
        self._indicator_repo = IndicatorRepository(self._config.get("CONNECTION", "MONGO_IP"))
        self._area_repo = AreaRepository(self._config.get("CONNECTION", "MONGO_IP"))
        self._observations_repo = ObservationRepository(self._config.get("CONNECTION", "MONGO_IP"))

    def run(self):
        computations_sheet = get_sheet_by_name(self._config.get("EXCEL", "COMPUTATIONS_FILE_NAME"),
                                               self._config.get("EXCEL", "COMPUTATIONS_SHEET_NAME"))
        self._get_indicators_zscores(computations_sheet)
        self._get_components_zscores(computations_sheet)
        self._get_subindexes_zscores(computations_sheet)

    def _get_indicators_zscores(self, computations_sheet):
        more_indicators = True
        i = 1
        indicators_row = int(self._config.get("EXCEL", "INDICATORS_START_ROW"))
        while more_indicators:
            if not computations_sheet.row(indicators_row)[i].value in ["", " ", None]:
                indicator_code = str(computations_sheet.row(indicators_row)[i].value).replace(" ", "_")
                indicator_document = self._indicator_repo.find_indicators_by_code(indicator_code)
                if not indicator_document["success"]:
                    self._log.warning("Could not retrieve indicator " + indicator_code + " from db")
                else:
                    print indicator_code
                    self._insert_country_values(computations_sheet,
                                                int(self._config.get("EXCEL", "COUNTRIES_NORMALIZED_START_ROW")), i,
                                                indicator_document["data"])
                i += 1
            else:
                more_indicators = False

    def _get_components_zscores(self, computations_sheet):
        more_components = True
        i = 1
        components_row = int(self._config.get("EXCEL", "COMPONENTS_START_ROW"))
        components_document = self._indicator_repo.find_indicators_components()
        if not components_document["success"]:
            self._log.error("Could not retrieve components from db")
            return
        while more_components:
            if not computations_sheet.row(components_row)[i].value in ["", " ", None]:
                for component_document in components_document["data"]:
                    if is_same_component(component_document["name"],
                                         str(computations_sheet.row(components_row)[i].value)):
                        print component_document["name"]
                        self._insert_country_values(computations_sheet,
                                                    int(self._config.get("EXCEL", "COUNTRIES_COMPONENTS_START_ROW")),
                                                    i, component_document)
                i += 1
            else:
                more_components = False

    def _get_subindexes_zscores(self, computations_sheet):
        more_subindexes = True
        i = 1
        subindexes_row = int(self._config.get("EXCEL", "SUBINDEXES_START_ROW"))
        subindexes_document = self._indicator_repo.find_indicators_sub_indexes()
        if not subindexes_document["success"]:
            self._log("Could not retrieve subindexes from db")
            return
        while more_subindexes:
            if not computations_sheet.row(subindexes_row)[i].value in ["", " ", "Overall Index-z-scores", None]:
                for subindex_document in subindexes_document["data"]:
                    if is_same_subindex(subindex_document["name"],
                                        str(computations_sheet.row(subindexes_row)[i].value)):
                        print subindex_document["name"]
                        self._insert_country_values(computations_sheet,
                                                    int(self._config.get("EXCEL", "COUNTRIES_SUBINDEXES_START_ROW")),
                                                    i, subindex_document)
                i += 1
            else:
                more_subindexes = False

    def _insert_country_values(self, computations_sheet, start_row, column, indicator_document):
        countries_document = self._area_repo.find_countries("name")
        if not countries_document["success"]:
            self._log("Could not retrieve countries from db")
            return
        i = start_row
        for country_document in countries_document["data"]:
            if is_same_country(country_document["name"], str(computations_sheet.row(i)[0].value)):
                value = computations_sheet.row(i)[column].value
                if str(value) not in ["", " ", None]:
                    print "\t" + indicator_document["indicator"] + " " + country_document["iso3"] + " " + str(float(value))
                    self._observations_repo.insert_observation()
            else:
                for country_document_aux in countries_document["data"]:
                    if is_same_country(country_document_aux["name"],
                                       str(computations_sheet.row(i)[0].value)):
                        value = computations_sheet.row(i)[column].value
                        if str(value) not in ["", " ", None]:
                            print "\t" + indicator_document["indicator"] + " " + country_document_aux["iso3"] + " " + str(float(value))
                            self._observations_repo.insert_observation()
            i += 1