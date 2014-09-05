__author__ = 'Miguel'
__date__ = '02/09/2014'

import xlrd
import re


class Importer(object):

    def __init__(self, log):
        self._log = log

    def get_data_sheets(self):
        book = xlrd.open_workbook('./data_file.xlsx')
        sheets = []
        for sheet in book.sheets():
            if self._is_needed_data_sheet(sheet.name):
                sheets.append(sheet)
        self._log.info("Sheets retrieved")
        return sheets

    @staticmethod
    def _is_needed_data_sheet(sheet_name):
        m = re.match("[\w\d\s]+-(imputed|(normali(s|z)ed))$", sheet_name, re.I)
        if m:
            return True
        return False