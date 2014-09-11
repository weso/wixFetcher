__author__ = 'Miguel'
__date__ = '02/09/2014'

import sys


class Parser(object):

    YEAR_ROW = 0
    COUNTRY_COLUMN = 0

    def __init__(self, log):
        self._log = log

    def parse_data_sheet(self, sheet):
        '''
        Parses the rows of an Excel file retrieving the countries.

        :param sheet: the Excel sheet object with all the data
        :return: None (for now)
        '''
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
        '''
        Parses the indicator's values of a country for each year given the row of that country in the Excel file.

        :param sheet: the Excel sheet object with all the data
        :param row: the Excel row in which are the indicator's values of a country for each year
        :return: None (for now)
        '''
        i = 1
        while i < sheet.ncols - 2:
            # -2 because there's one more column due to the new countries note. Should be -1 in future cases.
            value = str(sheet.row(row)[i].value)
            if value in [None, "", " "]:
                break
            sys.stdout.write("\n    " + str(int(sheet.row(Parser.YEAR_ROW)[i].value)) + " -> " + value)
            i += 1