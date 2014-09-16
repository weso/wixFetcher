__author__ = 'Miguel'
__date__ = '10/09/2014'


class ComputingModule(object):

    def __init__(self, log):
        self._log = log

    def validate_observations(self, observations):
        raw_observations = []
        normalized_observations = []
        ranked_observations = []
        scored_observations = []
        grouped_observations = []

        for observation in observations:
            if observation.computation.type == "raw":
                raw_observations.append(observation)
            elif observation.computation.type == "nomalized":
                normalized_observations.append(observation)
            elif observation.computation.type == "ranked":
                ranked_observations.append(observation)
            elif observation.computation.type == "scored":
                scored_observations.append(observation)
            elif observation.computation.type == "grouped":
                grouped_observations.append(observation)
            else:
                self._log.warning("Observation " + observation.id + " with unknown type of computation.");

        for observation in observations:
            normalized_value = self._normalize_value(observation)
            print(normalized_value)

    @staticmethod
    def _normalize_value(observation):
        return observation.value

    def _compute_value(self, observation):
        pass

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
