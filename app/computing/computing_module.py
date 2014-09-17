__author__ = 'Miguel'
__date__ = '10/09/2014'

from application.wixFetcher.app.util.observation_util import ObservationUtil


class ComputingModule(object):

    def __init__(self, log):
        self._log = log

    def validate_observations(self, observations):
        raw_observations = self._classify_observations_by_computation_type(observations, "raw")
        # Asuming raw == imputed
        normalized_observations = self._classify_observations_by_computation_type(observations, "normalized")
        ranked_observations = self._classify_observations_by_computation_type(observations, "ranked")
        scored_observations = self._classify_observations_by_computation_type(observations, "scored")
        grouped_observations = self._classify_observations_by_computation_type(observations, "grouped")

        if len(normalized_observations) > 0:
            for observation in raw_observations:
                normalized_version = self._find_equivalent_version(observation, normalized_observations)
                if normalized_version is not None:
                    calculated_normalized_value = self._normalize_observation_value(observation)
                    if calculated_normalized_value != normalized_version.value:
                        self._log.warning("The normalized value calculated for the observation " + observation.id
                                          + " does not match with the value of its normalized version, "
                                          + normalized_version.id)
        else:
            self._log.warning("There are no normalized observations")

    def _find_equivalent_version(self, observation, computed_observations):
        for computed_observation in computed_observations:
            if ObservationUtil.are_equivalent_observations(observation, computed_observation):
                return observation
        self._log.warning("Observation " + observation.id + " has not equivalent computed version.")
        return None

    @staticmethod
    def _classify_observations_by_computation_type(observations, computation_type):
        filtered_observations = []
        for observation in observations:
            if observation.computation.type == computation_type:
                filtered_observations.append(observation)
        return filtered_observations

    @staticmethod
    def _normalize_observation_value(observation):
        return round((observation.value - observation.computation.mean) / observation.computation.std_deviation, 2)

    # """
    # This commented code is the first approach made for doing the computing process retrieving the values from the
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
