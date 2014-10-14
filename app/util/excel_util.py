__author__ = 'Miguel'

import xlrd
import re


class ExcelUtil(object):

    @staticmethod
    def is_empty_cell(value):
        if value in [None, "", " ", "..", "...", u'\u2026']:
            return True
        return False

    @staticmethod
    def get_ncols_from_cell(sheet, row_number, col_number):
        num_cols = 0
        while (num_cols + col_number) < sheet.ncols and \
                not ExcelUtil.is_empty_cell(sheet.row(row_number)[col_number + num_cols].value):
            num_cols += 1
        return num_cols

    @staticmethod
    def get_nrows_from_cell(sheet, col_number, row_number):
        num_rows = 0
        while (num_rows + row_number) < sheet.nrows and \
                not ExcelUtil.is_empty_cell(sheet.row(row_number + num_rows)[col_number].value):
            num_rows += 1
        return num_rows

    @staticmethod
    def is_same_value(value1, value2):
        if str(value1).lower() == str(value2).lower():
            return True
        elif re.match("(free)|(open)", value1, re.I) \
                and re.match("(free)|(open)", value2, re.I):
            return True
        elif re.match("communicat(io|oi)ns infrastructure", value1, re.I)\
                and re.match("communicat(io|oi)ns infrastructure", value2, re.I):
            return True
        elif re.match("economic( impact)?", value1, re.I)\
                and re.match("economic( impact)?", value2, re.I):
            return True
        elif re.match("political( impact)?", value1, re.I)\
                and re.match("political( impact)?", value2, re.I):
            return True
        elif re.match("social and environmental( impact)?", value1, re.I)\
                and re.match("social and environmental( impact)?", value2, re.I):
            return True
        return False
