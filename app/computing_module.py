__author__ = 'Miguel'
__date__ = '10/09/2014'


class ComputingModule(object):

    def __init__(self, log):
        self._log = log
        self._current_sheet_means = dict()
        self.current_sheet_stds = dict()
        self._calculated_zscores = []

    def _initiate_sheet_values(self, sheet):
        pass

    def _impute_value(self, sheet, value):
        pass

    def _get_zscore(self, value):
        pass

    def _normalize_value(self, sheet, value):
        pass

    def _compute_value(self, sheet, value):
        pass