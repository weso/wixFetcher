__author__ = 'Miguel'
__date__ = '03/09/2014'


class ExcelUtil(object):

    @staticmethod
    def _is_empty_cell(value):
        if value in [None, "", " "]:
            return True
        return False