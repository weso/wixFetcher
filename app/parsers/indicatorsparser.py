__author__ = 'Dani'

from webindex.domain.model.indicator.indicator import create_indicator
from .utils import build_indicator_uri
from .utils import normalize_component_code_for_uri, normalize_subindex_code_for_uri
from webindex.domain.model.component import create_component
from webindex.domain.model.subindex import create_sub_index
from webindex.domain.model.index import create_index
from utility.time import utc_now


class IndicatorsParser(object):


    def __init__(self, log, db_indicator, db_component, db_subindex, db_index, config):
        self._log = log
        self._db = db_indicator
        self._db_component = db_component
        self._db_subindex = db_subindex
        self._db_index = db_index
        self._config = config
        self._indicators = []
        self._components = {}
        self._subindexes = {}

    def parse_indicators_sheet(self, sheet, sheet_weights_groups):
        """
        Do the parsing process, persist the indicators and return the number of indicator found.

        :param sheet:
        :return:
        """
        for i in range(self._config.getint("INDICATORS_PARSER", "FIRST_DATA_ROW"),
                       self._config.getint("INDICATORS_PARSER", "LAST_DATA_ROW") + 1):
            self._parse_indicator_row(sheet.row(i), sheet_weights_groups)

        self._log.info("Secondary indicators detected: {}".format(len(self._indicators)))
        for excell_ind in self._indicators:
            model_ind = self._turn_excell_ind_into_model_ind(excell_ind)
            self._db.insert_indicator(model_ind,
                                      indicator_uri=build_indicator_uri(self._config, excell_ind.code),
                                      component_name=excell_ind.component.name,
                                      subindex_name=excell_ind.component.subindex.name,
                                      index_name="INDEX",
                                      weight=excell_ind.weight)
        self._persist_groups()
        return len(self._indicators)



    def _persist_groups(self):
        """
        Introduce in the database information about components, index and subindexes
        :return:
        """

        for comp_key in self._components:
            comp = self._components[comp_key]
            model_comp = self._turn_excell_comp_into_model_comp(comp)
            self._db_component.insert_component(model_comp,
                                                component_uri=build_indicator_uri(self._config,
                                                                                  normalize_component_code_for_uri(comp.name)),
                                                subindex_name=comp.subindex.name,
                                                index_name="INDEX")

        for subin_key in self._subindexes:
            subin = self._subindexes[subin_key]
            model_subin = self._turn_excell_subin_into_model_subin(subin)
            self._db_subindex.insert_subindex(model_subin,
                                              subindex_uri=build_indicator_uri(self._config,
                                                                               normalize_subindex_code_for_uri(subin.name)),
                                              index_name="INDEX")

        self._db_index.insert_index(self._create_model_index_object(),
                                    index_uri=build_indicator_uri(self._config, "INDEX"))


    @staticmethod
    def _turn_excell_comp_into_model_comp(excell_comp):
        result = create_component(order=None,
                                  contributor=None,
                                  issued=utc_now(),
                                  label=excell_comp.name,
                                  notation=None)
        return result

    @staticmethod
    def _turn_excell_subin_into_model_subin(excell_subin):
        result = create_sub_index(order=None,
                                  colour=None,
                                  label=excell_subin.name,
                                  notation=None)
        return result

    @staticmethod
    def _create_model_index_object():
        result = create_index(order=None,
                              colour=None,
                              label="Index",
                              notation=None)
        return result



    def _turn_excell_ind_into_model_ind(self, excell_ind):
        result = create_indicator(_type="Secondary",
                                  country_coverage=self._config.getint("INDICATORS_PARSER",
                                                                       "COUNTRY_COVERAGE"),
                                  provider_link=excell_ind.data_prov_link,
                                  republish=excell_ind.republish,  # We may have to check this
                                  high_low=excell_ind.high_low,
                                  label=excell_ind.name,
                                  comment=excell_ind.description,
                                  notation=None,  # For rdf. Unedeed at this point
                                  interval_starts=self._config.getint("INDICATORS_PARSER",
                                                                      "INTERVAL_STARTS"),
                                  interval_ends=self._config.getint("INDICATORS_PARSER",
                                                                    "INTERVAL_ENDS"),
                                  code=excell_ind.code,
                                  organization=None)  # We will add it, if needed, through a method
        if excell_ind.source is not None:
            result.add_organization(excell_ind.source)
        return result

    def _parse_indicator_row(self, row, sheet_group_weights):
        result = IndicatorExcell(code=self._look_for_code(row),
                                 name=self._look_for_name(row),
                                 description=self._look_for_description(row),
                                 source=self._look_for_source(row),
                                 weight=self._look_for_weight(row),
                                 type_of_indicator=self._look_for_type(row),
                                 data_prov_link=self._look_for_data_prov_link(row),
                                 latest_rep=self._look_for_latest_rep(row),
                                 high_low=self._look_for_high_low(row),
                                 republish=self._look_for_republish(row))
        self._process_components_and_subindexes(result, row, sheet_group_weights)
        self._indicators.append(result)


    def _process_components_and_subindexes(self, indicator, row, sheet_group_weights):
        subindex_name = self._normalize_subindex_name(row[self._config.getint("INDICATORS_PARSER",
                                                                              "SUBINDEX")].value)
        component_name = self._normalize_component_name(row[self._config.getint("INDICATORS_PARSER",
                                                                                "COMPONENT")].value)

        subindex = None
        component = None


        #Managing subindexes
        if subindex_name in self._subindexes:
            subindex = self._subindexes[subindex_name]
        else:
            subindex = SubIndexExcell(name=subindex_name,
                                      weight=self._look_for_group_weight(subindex_name, sheet_group_weights))
            self._subindexes[subindex_name] = subindex


        #Managing components
        if component_name in self._components:
            component = self._components[component_name]
        else:
            component = ComponentExcell(name=component_name,
                                        weight=self._look_for_group_weight(subindex_name, sheet_group_weights))
            subindex.add_component(component)
            self._components[component_name] = component

        #Linking indicator and component
        component.add_indicator(indicator)


    def _look_for_group_weight(self, name, sheet):
        name_col = self._config.getint("INDICATORS_PARSER", "GROUP_NAME_COLUMN")
        weight_col = self._config.getint("INDICATORS_PARSER", "GROUP_WEIGHT_COLUMN")

        for irow in range(0, sheet.nrows):
            if sheet.row(irow)[name_col].value.upper() == name.upper():
                try:
                    return float(sheet.row(irow)[weight_col].value)
                except BaseException as e:
                    self._log.error("Wrong weight for a grouped entity: {}".format(name))
                    raise ValueError("Wrong weight for a grouped entity: {}".format(name))
        self._log.error("Unable to detect weight for a grouped entity: {}".format(name))
        raise ValueError("Unable to detect weight for a grouped entity: {}".format(name))



    @staticmethod
    def _normalize_component_name(original):
        """
        It expects the name of a component and return the same name capitalized.
        Also, if it contains the character &, it will change it for "and".
        It will also erase the word "Relevant" if it appears
        This method has been taken apart thinking that this normalization may change.

        :param original:
        :return:
        """

        return original.replace("Relevant ", "")\
            .replace("relevant ", "")\
            .replace("&", "and")\
            .capitalize()


    @staticmethod
    def _normalize_subindex_name(original):
        """
        It expects the name of a subindex and return it capitalized.
        Also, if it finds the word "and" it will replace it by the char "&".
        This method has been taken apart thinking that this normalization may change.

        :param original:
        :return:
        """
        return original.replace("and", "&")\
            .replace("And", "&")\
            .capitalize()

    def _look_for_high_low(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "HIGH_LOW")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value

    def _look_for_type(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "TYPE")]
        if ExcellUtils.is_empty_cell(cell):
            raise ValueError("Unknown type of indicator: {}. It should be Primary or Secondary".format(cell.value))
        else:
            if cell.value.upper().replace(" ", "") == "PRIMARY":
                return "Primary"
            elif cell.value.upper().replace(" ", "") == "SECONDARY":
                return "Secondary"
            else:
                raise ValueError("Unknown type of indicator: {}. It should be Primary or Secondary".format(cell.value))

    def _look_for_weight(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "WEIGHT")]
        if ExcellUtils.is_empty_cell(cell):
            self._log.warning("Some missing wight in indicatrs. Assuming weight 1, but check excell file.")
        else:
            try:
                return float(cell.value)
            except BaseException:
                self._log.error("Error while parsing a weight. Unexpected value {}".format(cell.value))
                raise ValueError("Error while parsing a weight. Unexpected value {}".format(cell.value))


    def _look_for_latest_rep(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "LATEST_REPORT")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value


    def _look_for_data_prov_link(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "DATA_PROVIDER")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value


    def _look_for_source(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "SOURCE")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value


    def _look_for_description(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "DESCRIPTION")]
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
        cell = row[self._config.getint("INDICATORS_PARSER", "NAME")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value.capitalize()



    def _look_for_code(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "CODE")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return self._normalize_code(cell.value)

    def _look_for_republish(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "REPUBLISH")]
        if ExcellUtils.is_empty_cell(cell):
            self._log.warning("Missing republish indicator attribute. Assuming republish = yes in these cases cases")
            return True
        else:
            if cell.value.upper().replace(" ", "") == "YES":
                return True
            elif cell.value.upper().replace(" ", "") == "NO":
                return False
            else:
                self._log.error("Unrecognized republish att parsing indicator: {}".format(cell.value))
                raise ValueError("Unrecognized republish att parsing indicator: {}".format(cell.value))

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
                 latest_rep=None, type_of_indicator=None,
                 weight=None, high_low=None, republish=None):
        self.code = code
        self.name = name
        self.description = description
        self.source = source
        self.data_prov_link = data_prov_link
        self.latest_rep = latest_rep
        self.high_low = high_low
        self.type_of_indicator = type_of_indicator
        self.weight = weight
        self.republish = republish

        self.component = None


class ComponentExcell(object):
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight
        self.subindex = None
        self.indicators = []

    def add_indicator(self, indicator):
        self.indicators.append(indicator)
        indicator.component = self



class SubIndexExcell(object):
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight
        self.components = []

    def add_component(self, component):
        self.components.append(component)
        component.subindex = self



