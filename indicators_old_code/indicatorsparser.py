__author__ = 'Dani'



class IndicatorsParser(object):

    SUBINDEXES_ROW = 0
    COMPONENTS_ROW = 1
    FIRST_INDICATORS_ROW = 3
    FIRST_INDICATORS_COLUMN = 1
    SECONDARY_INDICATORS_ROW_BEGIN = 3
    PRIMARY_INDICATORS_ROW_BEGIN = 9

    def __init__(self, log):
        self._log = log
        self._subindexes = []
        self._components = []
        self._indicators = []

    def parse_indicators_sheet(self, sheet):
        self._find_subindexes(sheet)
        self._find_components(sheet)
        self._find_indicators(sheet)

        self.print_info()

    def _find_subindexes(self, sheet):
        target_row = sheet.row(self.SUBINDEXES_ROW)
        tmp_subindex = None
        i = 1
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
        target_row = sheet.row(self.COMPONENTS_ROW)
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
        for irow in range(self.FIRST_INDICATORS_ROW, sheet.nrows):
            row = sheet.row(irow)
            icol = self.FIRST_INDICATORS_COLUMN
            while icol < sheet.ncols:
                cell = row[icol]
                if self._not_empty_cell(cell):
                    #beg
                    beg = icol
                    #Code
                    code = cell.value
                    #Name
                    icol += 1
                    cell = row[icol]
                    name = cell.value
                    #high_low
                    icol += 1
                    cell = row[icol]
                    high_low = cell.value
                    #weight
                    icol += 1
                    cell = row[icol]
                    weight = int(cell.value)
                    #end
                    end = icol
                    if irow < self.PRIMARY_INDICATORS_ROW_BEGIN:
                        category = "Secondary"
                    else:
                        category = "Primary"
                    self._indicators.append(LocatedIndicator(name=name,
                                                             code=code,
                                                             high_low=high_low,
                                                             weight=weight,
                                                             category=category,
                                                             beg=beg,
                                                             end=end))
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
            print indicator.code, ",,,,,", indicator.category, ",,,,,", indicator.name, "......", indicator.high_low, ".......", indicator.weight


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



class LocatedEntity(object):
    def __init__(self, name, beg, end=0):
        self.name = name
        self.beg = beg
        self.end = end


class LocatedIndicator(LocatedEntity):
    def __init__(self, name, code, high_low, weight, category, beg, end=None):
        LocatedEntity.__init__(self, name, beg, end)
        self.code = code
        self.category = category
        self.high_low = high_low
        self.weight = weight
