__author__ = 'Miguel'

import xlrd
from ..util.excel_util import ExcelUtil
from aux_model.index import Index
from aux_model.subindex import Subindex
from aux_model.component import Component
from aux_model.indicator import Indicator


class ComputationModule(object):

    def __init__(self, log):
        self._log = log
        self._index = None

    def run(self):
        sheet = self.get_computations_sheet()
        self._initialize_index(sheet)

    def _initialize_index(self, sheet):
        self._index = Index()
        i = 0
        j = 0
        num_subindexes = ExcelUtil.get_ncols_from_cell(sheet, 360, 1)
        while i < num_subindexes:
            subindex_label = str(sheet.row(360)[i+1].value)
            subindex_weight = sheet.row(443)[i+1].value
            if "Weight" not in subindex_label:
                subindex = Subindex(subindex_label, float(subindex_weight))
                self._index.add_subindex(subindex)
                print subindex.label
                num_components = ExcelUtil.get_ncols_from_cell(sheet, 181, 1)
                match = False
                while j < num_components:
                    component_label = str(sheet.row(181)[j+1].value)
                    component_weight = sheet.row(270)[j+1].value
                    curr_subindex_name = str(sheet.row(180)[j+1].value)
                    if not ExcelUtil.is_empty_cell(curr_subindex_name):
                        if ExcelUtil.is_same_value(curr_subindex_name, subindex.label):
                            match = True
                            component = Component(component_label, float(component_weight))
                            subindex.add_component(component)
                            print "\t" + component.label
                        elif match:
                            break
                    elif match:
                        component = Component(component_label, float(component_weight))
                        subindex.add_component(component)
                        print "\t" + component.label
                    j += 1
            i += 1

        i = 0
        num_indicators = ExcelUtil.get_ncols_from_cell(sheet, 1, 1)
        while i < num_indicators:
            indicator_code = str(sheet.row(1)[i + 1].value).replace(" ", "_")
            indicator_label = str(sheet.row(2)[i + 1].value)
            indicator_type = str(sheet.row(3)[i + 1].value)
            indicator_component_label = str(sheet.row(4)[i + 1].value)
            indicator_subindex_label = str(sheet.row(5)[i + 1].value)
            indicator_weight = str(sheet.row(6)[i + 1].value)
            for subindex in self._index.subindexes:
                if ExcelUtil.is_same_value(subindex.label, indicator_subindex_label):
                    for component in subindex.components:
                        if ExcelUtil.is_same_value(component.label, indicator_component_label):
                            indicator = Indicator(indicator_code, indicator_label, indicator_type, "high",
                                                  indicator_weight)
                            component.add_indicator(indicator)
            i += 1

        print "\n\n\n"
        for subindex in self._index.subindexes:
            print subindex.label
            for component in subindex.components:
                print "\t" + component.label
                for indicator in component.indicators:
                    print "\t\t" + indicator.code



    @staticmethod
    def get_computations_sheet():
        return xlrd.open_workbook("./computations.xlsx").sheet_by_name("IndexComputation 2013")
