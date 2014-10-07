__author__ = 'Dani'

from webindex.domain.model.indicator.indicator import create_indicator
from webindex.domain.model.component import create_component
from webindex.domain.model.subindex import create_sub_index


class SecondaryIndicatorsParser(object):






    def __init__(self, log, db, config):
        self._log = log
        self._db = db
        self._config = config
        self._indicators = []
        self._components = {}
        self._subindexes = {}

    def parse_indicators_sheet(self, sheet):
        for i in range(self._config.getint("SECONDARY_INDICATORS_PARSER", "FIRST_DATA_ROW"),
                       self._config.getint("SECONDARY_INDICATORS_PARSER", "LAST_DATA_ROW") + 1):
            self._parse_indicator_row(sheet.row(i))

        for excell_ind in self._indicators:
            model_ind = self._turn_excell_ind_into_model_ind(excell_ind)
            self._db.insert_indicator(model_ind,
                                      component_name=excell_ind.component.name,
                                      subindex_name=excell_ind.component.subindex.name,
                                      index_name="INDEX")


    def _turn_excell_ind_into_model_ind(self, excell_ind):
        result = create_indicator(_type="Secondary",
                                  country_coverage=self._config.getint("SECONDARY_INDICATORS_PARSER", "COUNTRY_COVERAGE"),
                                  provider_link=excell_ind.data_prov_link,
                                  republish=True,  # We may have to check this
                                  high_low=excell_ind.high_low,
                                  label=excell_ind.name,
                                  comment=excell_ind.description,
                                  notation=None,  # For rdf. Unedeed at this point
                                  interval_starts=self._config.getint("SECONDARY_INDICATORS_PARSER", "INTERVAL_STARTS"),
                                  interval_ends=self._config.getint("SECONDARY_INDICATORS_PARSER", "INTERVAL_ENDS"),
                                  code=excell_ind.code,
                                  organization=None)  # We will add it, if needed, through a method
        if excell_ind.source is not None:
            result.add_organization(excell_ind.source)
        return result

    def _parse_indicator_row(self, row):
        result = IndicatorExcell(code=self._look_for_code(row),
                                 name=self._look_for_name(row),
                                 description=self._look_for_description(row),
                                 source=self._look_for_source(row),  # TODO: sure this is the proper content?
                                 data_prov_link=self._look_for_data_prov_link(row),
                                 latest_rep=self._look_for_latest_rep(row),  # An URL
                                 min_range=self._look_for_min_range(row),  # String, could be unbounded
                                 max_range=self._look_for_max_range(row),  # String, could be unbounded
                                 high_low=self._look_for_high_low(row))
        self._process_components_and_subindexes(result, row)
        self._indicators.append(result)


    def _process_components_and_subindexes(self, indicator, row):
        subindex_name = self._normalize_grouped_entity_name(row[self._config.getint("SECONDARY_INDICATORS_PARSER",
                                                                                    "SUBINDEX")].value)
        component_name = self._normalize_grouped_entity_name(row[self._config.getint("SECONDARY_INDICATORS_PARSER",
                                                                                     "COMPONENT")].value)

        subindex = None
        component = None


        #Managing subindexes
        if subindex_name in self._subindexes:
            subindex = self._subindexes[subindex_name]
        else:
            subindex = SubIndexExcell(name=subindex_name)
            self._subindexes[subindex_name] = subindex


        #Managing components
        if component_name in self._components:
            component = self._components[component_name]
        else:
            component = ComponentExcell(name=component_name)
            subindex.add_component(component)
            self._components[component_name] = component

        #Linking indicator and component
        component.add_indicator(indicator)


    @staticmethod
    def _normalize_grouped_entity_name(original):
        """
        It expects the name of a component or a subindex and return the same name capitalized.
        This method has been taken apart thinking that this normalization may change.

        :param original:
        :return:
        """
        return original.capitalize()

    def _look_for_high_low(self, row):
        cell = row[self._config.getint("SECONDARY_INDICATORS_PARSER", "HIGH_LOW")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value

    def _look_for_max_range(self, row):
        cell = row[self._config.getint("SECONDARY_INDICATORS_PARSER", "DATA_RANGE")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return self._parse_max_range(cell.value)

    def _look_for_min_range(self, row):
        cell = row[self._config.getint("SECONDARY_INDICATORS_PARSER", "DATA_RANGE")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return self._parse_min_range(cell.value)


    def _parse_min_range(self, original_complete):
        return self._parse_some_range(original_complete, 0)


    def _parse_max_range(self, original_complete):
        return self._parse_some_range(original_complete, 1)

    def _parse_some_range(self, original_complete, position):
        """
        The operations to extract the min range and the max range are the same, but returning different
        parts of the string.
        position = 0 ---> the method returns min range
        position = 1 ---> the method return max range

        :param original_complete:
        :param position:
        :return:
        """
        if "-" in original_complete:
            return original_complete.split("-")[position]
        elif "," in original_complete:
            return original_complete.split(",")[position]
        else:
            self._log.warning("Unexpected format for range while parsing indicators (looking for min): "
                              + original_complete)
            return original_complete


    def _look_for_latest_rep(self, row):
        cell = row[self._config.getint("SECONDARY_INDICATORS_PARSER", "LATEST_REPORT")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value


    def _look_for_data_prov_link(self, row):
        cell = row[self._config.getint("SECONDARY_INDICATORS_PARSER", "DATA_PROVIDER")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value


    def _look_for_source(self, row):
        cell = row[self._config.getint("SECONDARY_INDICATORS_PARSER", "SOURCE")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value


    def _look_for_description(self, row):
        cell = row[self._config.getint("SECONDARY_INDICATORS_PARSER", "DESCRIPTION")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return self._normalize_description(cell.value)


    @staticmethod
    def _normalize_description(original):
        """
        It receives a text and return the same text ensuring the first character is capitalized
        and the last character is a dot.

        :param original:
        :return:
        """
        result = original.capitalize()
        if result.endswith("."):
            return result
        else:
            return result + "."


    def _look_for_name(self, row):
        cell = row[self._config.getint("SECONDARY_INDICATORS_PARSER", "NAME")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value.capitalize()



    def _look_for_code(self, row):
        cell = row[self._config.getint("SECONDARY_INDICATORS_PARSER", "CODE")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return self._normalize_code(cell.value)

    @staticmethod
    def _normalize_code(original):
        """
        It receives an indicator code and returns it uppercased and replacing all blanks by "_"

        :param original:
        :return:
        """
        return original.upper().replace(" ", "_")


class ExcellUtils(object):
    @staticmethod
    def is_empty_cell(cell):
        if cell.value in [None, "", " "]:
            return True
        return False


class IndicatorExcell(object):
    def __init__(self, code, name, description=None,
                 source=None, data_prov_link=None,
                 latest_rep=None, min_range=None,
                 max_range=None, high_low=None):
        self.code = code
        self.name = name
        self.description = description
        self.source = source
        self.data_prov_link = data_prov_link
        self.latest_rep = latest_rep
        self.min_range = min_range
        self.max_range = max_range
        self.high_low = high_low

        self.component = None


class ComponentExcell(object):
    def __init__(self, name):
        self.name = name

        self.subindex = None
        self.indicators = []

    def add_indicator(self, indicator):
        self.indicators.append(indicator)
        indicator.component = self



class SubIndexExcell(object):
    def __init__(self, name):
        self.name = name

        self.components = []

    def add_component(self, component):
        self.components.append(component)
        component.subindex = self



