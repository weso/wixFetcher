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
                print subindex.label + "->" + str(subindex.weight)
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
                            print "\t" + component.label + "->" + str(component.weight)
                        elif match:
                            break
                    elif match:
                        component = Component(component_label, float(component_weight))
                        subindex.add_component(component)
                        print "\t" + component.label + "->" + str(component.weight)
                    j += 1
            i += 1

    @staticmethod
    def get_computations_sheet():
        return xlrd.open_workbook("./computations.xlsx").sheet_by_name("IndexComputation 2013")
