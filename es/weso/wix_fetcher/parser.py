__author__ = 'Miguel'
__date__ = '02/09/2014'

import xlrd
import sys


class Parser(object):

    YEAR_ROW = 0
    COUNTRY_COLUMN = 0

    def __init__(self, log):
        self._log = log

    def parse_data_sheet(self, sheet):
        sys.stdout.write("\n---------" + sheet.name + "---------\n")
        i = 1
        while i < sheet.nrows:
            value = sheet.col(self.COUNTRY_COLUMN)[i].value
            if value in [None, "", " "]:
                break
            sys.stdout.write("  " + value)
            self._get_country_data(sheet, i)
            sys.stdout.write("\n")
            i += 1
        print "\n"

    @staticmethod
    def _get_country_data(sheet, row):
        i = 1
        while i < sheet.ncols - 2:
            value = str(sheet.row(row)[i].value)
            if value in [None, "", " "]:
                break
            sys.stdout.write("\n    " + value)
            i += 1