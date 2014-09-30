__author__ = 'Miguel'

from application.wixFetcher.app.util.observation_util import ObservationUtil
from webindex.domain.model.indicator.indicator import Indicator
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.area_repository import AreaRepository
from infrastructure.mongo_repos.observation_repository import ObservationRepository
import numpy


class ComputationModule(object):

    def __init__(self, log):
        self._log = log
        self._indicator_repo = IndicatorRepository("http://localhost:27017/")
        self._area_repo = AreaRepository("http://localhost:27017/")
        self._observation_repo = ObservationRepository("http://localhost:27017/")

    def validate_observations(self):
        subindexes_query = self._indicator_repo.find_indicators_sub_indexes()
        countries_query = self._area_repo.find_countries("name")
        if subindexes_query["success"]:
            subindexes = subindexes_query["data"]
        else:
            self._log.error("Unable to retrieve indicators data: " + subindexes_query["error"])
            raise RuntimeError()
        if countries_query["success"]:
            countries = countries_query["data"]
        else:
            self._log.error("Unable to retrieve countries data: " + subindexes_query["error"])
            raise RuntimeError()

        for subindex in subindexes:
            subindex_components = subindex["children"]
            print subindex["type"] + "   " + subindex["name"]
            for component in subindex_components:
                component_indicators = component["children"]
                print "\t" + component["type"] + "    " + component["name"]
                for country in countries:
                    for indicator in component_indicators:
                        sum = 0
                        for country in countries:
                            observation = self._observation_repo.find_observations(indicator["indicator"],
                                                                               country["iso3"],
                                                                               u"2008")
                            sum += observation["value"]
                        mean = sum / len(countries)
                        stdev = numpy.std()
                        #normalized_value
                        #check normalization
                        #get weighed values
                        #sum weighed values
                    #take mean = sum / len(countries)
                    #check mean (indicators)
                    #take max and min
                #take range
                #take components' default weights




        '''
        for observation in observations:
            # We take the computations
            for computation in observation.computations:
                if computation.type == "raw":
                    raw_computation = computation
                elif computation.type == "normalized":
                    normalized_computation = computation
                elif computation.type == "grouped":
                    grouped_computation = computation
                elif computation.type == "scored":
                    scored_computation = computation
                elif computation.type == "ranked":
                    ranked_computation = computation
                else:
                    # Invalid computation type
                    raise ValueError("An unknown computation type {} has been found".format(computation.type))

            # Step #1: Check normalization
            if normalized_computation is not None:
                calculated_normalized_value = self._normalize_observation_value(observation, raw_computation)
                if calculated_normalized_value != normalized_computation.value:
                    self._log.error("The calculated value for normalization does not match with the retrieved "
                                    "normalized value. Obs id: " + observation.id)
            else:
                self._log.warning("There is no normalized value for obs " + observation.id)

            # Step #2: Check aggregation (grouped data). Apply indicator weight, take mean of each component set
            if grouped_computation is not None:
                calculated_grouped_value = self._group_observation_value(observation, normalized_computation)
                if calculated_grouped_value != grouped_computation.value:
                    self._log.error("The calculated value for grouped data does not match with the retrieved "
                                    "grouped value. Obs id: " + observation.id)
        '''



    @staticmethod
    def _normalize_observation_value(observation, raw_computation):
        normalized_value = 0
        if observation.ref_indicator.high_low == "high":
            normalized_value = round((raw_computation.value - raw_computation.mean) / raw_computation.std_deviation, 2)
        elif observation.ref_indicator.high_low == "low":
            normalized_value = round((raw_computation.mean - raw_computation.value) / raw_computation.std_deviation, 2)
        return normalized_value

    @staticmethod
    def _group_observation_value(observation, normalized_computation):
        weighed_value = normalized_computation.value * ComputationModule._get_indicator_weight(observation.ref_indicator)
        return 0

    @staticmethod
    def _get_indicator_weight(indicator_id):
        # TODO: Llamar a mongo, construir el indicador y devolver el peso
        pass

    # """
    # This commented code is the first approach made for doing the computation process retrieving the values from the
    # Excel spreadsheet instead of doing it directly from the model built by the parser. Since it is better
    # to do it in the second way, this code will probably be removed.
    # """
    #
    # def __init__(self, log):
    #     self._log = log
    #     self._current_sheet_means = dict()
    #     self._current_sheet_stds = dict()
    #     self._calculated_zscores = []
    #
    # def validate(self, data_sheets):
    #     for sheet in data_sheets:
    #         self._initiate_sheet_values(sheet)
    #
    # def _initiate_sheet_values(self, sheet):
    #     row = 0
    #     while row < sheet.nrows:
    #         if ExcelUtil._is_empty_cell(str(sheet.row(row)[0].value)):
    #             break
    #         row += 1
    #     self._initiate_means(sheet, row + 1)
    #     self._initiate_stds(sheet, row + 3)
    #
    # def _initiate_means(self, sheet, row):
    #     '''
    #     Sets the indicator's values mean for each year of the current Excel sheet.
    #     :param sheet: the current Excel sheet
    #     :param row: the row where the mean values are located
    #     '''
    #     i = 1
    #     while i < sheet.ncols - 2:
    #         self._current_sheet_means[int(sheet.row(0)[i])] = sheet.row(row)[i]
    #
    # def _initiate_stds(self, sheet, row):
    #     '''
    #     Sets the indicator's values standard deviation for each year of the current Excel sheet.
    #     :param sheet: the current Excel sheet
    #     :param row: the row where the standard deviation values are located
    #     '''
    #     i = 1
    #     while i < sheet.ncols - 2:
    #         self._current_sheet_stds[int(sheet.row(0)[i])] = sheet.row(row)[i]
    #
    # def _normalize_value(self, value, year):
    #     return (value - self._current_sheet_means[year]) / self._current_sheet_stds[year]