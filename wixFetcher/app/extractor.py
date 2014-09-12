__author__ = 'Miguel'
__date__ = '02/09/2014'

import xlrd
import re


class Extractor(object):

    def __init__(self, log):
        self._log = log

    def get_data_sheets(self):
        '''
        Goes over the indicators' data file retrieving those sheets that are needed for its parsing.

        :return: the sheet collection needed
        '''
        book = xlrd.open_workbook('./data_file.xlsx')
        sheets = []
        for sheet in book.sheets():
            if self._is_needed_data_sheet(sheet.name):
                sheets.append(sheet)
                self._log.info("Sheet " + sheet.name + " retrieved")
        return sheets

    @staticmethod
    def _is_needed_data_sheet(sheet_name):
        '''
        Checks the name of the sheet against a regular expression to confirm if it's needed.
        :param sheet_name: the name of the sheet

        :return: True|False depending on the sheet is or not needed
        '''
        m = re.match("[\w\d\s]+-(imputed|(normali(s|z)ed))$", sheet_name, re.I)
        # Put regex in config file?
        if m:
            return True
        return False