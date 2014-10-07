__author__ = 'Dani'

from webindex.domain.model.indicator.indicator import create_indicator
from webindex.domain.model.component import create_component
from webindex.domain.model.subindex import create_sub_index
from webindex.domain.model.index import create_index
from utility.time import utc_now


class PrimaryIndicatorsAndGroupsParser(object):
    """
    Parse and incorpore to the database data about primary indicators,
    components, subindexes and index.

    """



    def __init__(self, log, config, db_indicator, db_component, db_subindex, db_index):
        self._log = log
        self._config = config
        self._db_indicator = db_indicator
        self._db_component = db_component
        self._db_subindex = db_subindex
        self._db_index = db_index
        self._subindexes = []
        self._components = []
        self._indicators = []

    def parse_indicators_sheet(self, sheet):
        self._find_subindexes(sheet)
        self._find_components(sheet)
        self._find_indicators(sheet)

        self._persist_indicators()
        self._persist_groups()

    def _persist_groups(self):
        """
        Introduce in the database information about components, index and subindexes
        :return:
        """

        for comp in self._components:
            model_comp = self._turn_located_comp_into_model_comp(comp)
            self._db_component.insert_component(model_comp,
                                                subindex_name=self._match_component_with_subindex(comp),
                                                index_name="INDEX")

        for subin in self._subindexes:
            model_subin = self._turn_located_subin_into_model_subin(subin)
            self._db_subindex.insert_subindex(model_subin,
                                              index_name="INDEX")

        self._db_index.insert_index(self._create_model_index_object())



    @staticmethod
    def _turn_located_comp_into_model_comp(located_comp):
        result = create_component(order=None,
                                  contributor=None,
                                  issued=utc_now(),
                                  label=located_comp.name,
                                  notation=None)
        return result

    @staticmethod
    def _turn_located_subin_into_model_subin(located_subin):
        result = create_sub_index(order=None,
                                  colour=None,
                                  label=located_subin.name,
                                  notation=None)
        return result

    @staticmethod
    def _create_model_index_object():
        result = create_index(order=None,
                              colour=None,
                              label="Index",
                              notation=None)
        return result



    def _persist_indicators(self):
        """

        :return:
        """
        for ind in self._indicators:
            model_indicator = self._turn_located_indicator_into_model_indicator(ind)
            self._db_indicator.insert_indicator(model_indicator,
                                                component_name=self._match_ind_with_component(ind),
                                                subindex_name=self._match_ind_with_subindex(ind),
                                                index_name="INDEX")



    def _turn_located_indicator_into_model_indicator(self, located_ind):
        result = create_indicator(_type="Primary",
                                  country_coverage=self._config.getint("PRIMARY_INDICATORS_PARSER", "COUNTRY_COVERAGE"),
                                  provider_link=None,
                                  republish=True,  # We may have to check this
                                  high_low=located_ind.high_low,
                                  label=located_ind.name,
                                  comment=None,
                                  notation=None,  # For rdf. Unedeed at this point
                                  interval_starts=self._config.getint("PRIMARY_INDICATORS_PARSER", "INTERVAL_STARTS"),
                                  interval_ends=self._config.getint("PRIMARY_INDICATORS_PARSER", "INTERVAL_ENDS"),
                                  code=located_ind.code,
                                  organization=None)  # We will add it, if needed, through a method
        return result

    def _find_subindexes(self, sheet):
        target_row = sheet.row(self._config.getint("PRIMARY_INDICATORS_PARSER", "SUBINDEXES_ROW"))
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
        target_row = sheet.row(self._config.getint("PRIMARY_INDICATORS_PARSER", "COMPONENTS_ROW"))
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
        for irow in range(self._config.getint("PRIMARY_INDICATORS_PARSER", "PRIMARY_INDICATORS_ROW_BEGIN"), sheet.nrows):
            row = sheet.row(irow)
            icol = self._config.getint("PRIMARY_INDICATORS_PARSER", "FIRST_INDICATORS_COLUMN")
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
                    if irow < self._config.getint("PRIMARY_INDICATORS_PARSER", "PRIMARY_INDICATORS_ROW_BEGIN"):
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


    # def print_info(self):
    #     print "\n__________________ SUBINDEXES\n"
    #     for subindex in self._subindexes:
    #         print subindex.name
    #
    #     print "\n___________________ COMPONENTS\n"
    #     for component in self._components:
    #         print component.name
    #     print "\n___________________ INDICATORS\n"
    #     for indicator in self._indicators:
    #         print indicator.code, ",,,,,", indicator.category, ",,,,,", indicator.name, "......", indicator.high_low, ".......", indicator.weight
    #
    #
    #     print "\n\n___________________ MAPPING\n"
    #
    #     # Headings
    #     print "Indicator\t\tName of component\t\tName of subindex\t\tDescription"
    #     # Mapping itself
    #     for indicator in self._indicators:
    #         print indicator.code + "\t\t" + self._match_ind_with_component(indicator) + "\t\t" + self._match_ind_with_subindex(indicator) + "\t\t" + indicator.name


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

    def _match_component_with_subindex(self, component):
        for subindex in self._subindexes:
            if component.beg >= subindex.beg and component.end <= component.end:
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
