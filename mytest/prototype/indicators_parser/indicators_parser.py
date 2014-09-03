__author__ = 'Dani'

import xlrd


class LocatedEntity(object):
    def __init__(self, name, beg, end=0):
        self.name = name
        self.beg = beg
        self.end = end


class LocatedIndicator(LocatedEntity):
    def __init__(self, name, code, category, beg, end=None):
        LocatedEntity.__init__(self, name, beg, end)
        self.code = code
        self.category = category


class IndicatorsParser(object):

    SUBINDEXES_LINE = 1
    COMPONENTS_LINE = 2
    FIRST_INDICATORS_LINE = 4
    FIRST_INDICATORS_COLUMN = 1
    SECONDARY_INDICATORS_BEGIN = 3
    PRIMARY_INDICATROS_BEGIN = 14

    def __init__(self):
        self._subindexes = []
        self._components = []
        self._indicators = []

    def run(self):
        a_path = "prot_ind.xlsx"
        book = xlrd.open_workbook(a_path)
        sheet = book.sheet_by_index(0)
        self._find_subindexes(sheet)
        self._find_components(sheet)
        self._find_indicators(sheet)

        self.print_info()

    def _find_subindexes(self, sheet):
        target_row = sheet.row(self.SUBINDEXES_LINE)
        tmp_subindex = None
        i = 0
        while i < sheet.ncols:
            cell = target_row[i]
            if self._not_empty_cell(cell):
                if tmp_subindex is not None:
                    tmp_subindex.end = i - 1
                    self._subindexes.append(tmp_subindex)
                tmp_subindex = LocatedEntity(cell.value, i)
            i += 1
        tmp_subindex.end = sheet.ncols - 1
        self._subindexes.append(tmp_subindex)

    def _find_components(self, sheet):
        target_row = sheet.row(self.COMPONENTS_LINE)
        tmp_comp = None
        i = 0
        while i < sheet.ncols:
            cell = target_row[i]
            if self._not_empty_cell(cell):
                if tmp_comp is not None:
                    tmp_comp.end = i - 1
                    self._components.append(tmp_comp)
                tmp_comp = LocatedEntity(cell.value, i)
            i += 1
        tmp_comp.end = sheet.ncols - 1
        self._components.append(tmp_comp)


    def _find_indicators(self, sheet):
        for irow in range(self.FIRST_INDICATORS_LINE, sheet.nrows):
            row = sheet.row(irow)
            icol = self.FIRST_INDICATORS_COLUMN
            while icol < sheet.ncols:
                cell = row[icol]
                if self._not_empty_cell(cell):
                    beg = icol
                    code = cell.value
                    icol += 1
                    cell = row[icol]
                    name = cell.value
                    end = icol
                    if irow < self.PRIMARY_INDICATROS_BEGIN:
                        category = "secondary"
                    else:
                        category = "primary"
                    self._indicators.append(LocatedIndicator(name, code, category, beg, end))
                icol += 1


    def print_info(self):
        print "\n__________________ SUBINDEXES\n"
        for subindex in self._subindexes:
            print subindex.name

        print "\n___________________ COMPONENTS\n"
        for component in self._components:
            print component.name
        print "\n___________________ INDICATORS\n"
        for indicator in self._indicators:
            print indicator.code, ",,,,,", indicator.category, ",,,,,", indicator.name


        print "\n\n___________________ MAPPING\n"

        # Headings
        print "Indicator\t\tName of component\t\tName of subindex\t\tDescription"
        # Mapping itself
        for indicator in self._indicators:
            print indicator.code + "\t\t" + self._match_ind_with_component(indicator) + "\t\t" + self._match_ind_with_subindex(indicator) + "\t\t" + indicator.name


    def _match_ind_with_component(self, indicator):
        for comp in self._components:
            if indicator.beg >= comp.beg and indicator.end <= comp.end:
                return comp.name
        return "FAILURE"

    def _match_ind_with_subindex(self, indicator):
        for subindex in self._subindexes:
            if indicator.beg >= subindex.beg and indicator.end <= subindex.end:
                return subindex.name
        return "FAILURE"


    def _not_empty_cell(self, cell):
        if cell.value in [None, "", " "]:
            return False
        return True




IndicatorsParser().run()
