__author__ = 'Dani'

from webindex.domain.model.indicator.indicator import create_indicator
from application.wixFetcher.app.parsers.utils import build_indicator_uri
from application.wixFetcher.app.parsers.utils import normalize_component_code_for_uri, normalize_subindex_code_for_uri
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
            provider_name, provider_url = self._get_real_name_and_url_from_organization_parsed_name(excell_ind.data_provider)
            self._db.insert_indicator(model_ind,
                                      indicator_uri=build_indicator_uri(self._config, excell_ind.code),
                                      component_name=excell_ind.component.name,
                                      subindex_name=excell_ind.component.subindex.name,
                                      index_name="INDEX",
                                      weight=excell_ind.weight,
                                      provider_name=provider_name,
                                      provider_url=provider_url)
        self._persist_groups()
        return len(self._indicators)

    def _get_real_name_and_url_from_organization_parsed_name(self, parsed_name):
        if parsed_name.upper() == "WF":
            return self._config.get("PROVIDERS", "WF_NAME"), self._config.get("PROVIDERS", "WF_URL")
        elif parsed_name.upper() == "ITU":
            return "ITU (International Telecommunication Union)", "http://www.itu.int/"
        elif parsed_name.upper() == "WB":
            return "WB (World Bank)", "http://www.worldbank.org/"
        elif parsed_name == "Internet World Stats/Alexa/Facebook":
            return "IWS (Internet World Stats)", "http://www.internetworldstats.com/"
        elif parsed_name.upper() == "WEF":
            return "WEF (World Economy Forum)", "http://www.weforum.org/"
        elif parsed_name.upper() == "INSEAD":
            return "INSEAD, The Business School for the World", "http://www.insead.edu/"
        elif parsed_name.upper() == "UN":
            return "UN (United Nations)", "http://www.un.org/"
        elif parsed_name == "Packet Clearing House":
            return "PCH (Packet Clearing House)", "https://www.pch.net/"
        elif parsed_name == "Wireless Intelligence (GSMA)":
            return "GSMA Wireless Intelligence", "https://gsmaintelligence.com/"
        elif parsed_name.upper() == "UNESCO":
            return "UNESCO (United Nations Educational, Scientific and Cultural Organization)", "www.unesco.org"
        elif parsed_name.upper() == "RSF":
            return "RWB (Reporters Without Borders", "http://www.rsf.org/"
        elif parsed_name in ["FH", "Freedom House (FH)"]:
            return "FH (Freedom House)", "www.freedomhouse.org/"
        else:
            raise ValueError("Unable to recognize organization name: {}".format(parsed_name))



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
                                                index_name="INDEX",
                                                weight=comp.weight,
                                                provider_name=self._config.get("PROVIDERS", "WF_NAME"),
                                                provider_url=self._config.get("PROVIDERS", "WF_URL"))

        for subin_key in self._subindexes:
            subin = self._subindexes[subin_key]
            model_subin = self._turn_excell_subin_into_model_subin(subin)
            self._db_subindex.insert_subindex(model_subin,
                                              subindex_uri=build_indicator_uri(self._config,
                                                                               normalize_subindex_code_for_uri(subin.name)),
                                              index_name="INDEX",
                                              weight=subin.weight,
                                              provider_name=self._config.get("PROVIDERS", "WF_NAME"),
                                              provider_url=self._config.get("PROVIDERS", "WF_URL"))

        self._db_index.insert_index(self._create_model_index_object(self._config.get("OTHERS", "INDEX_DESCRIPTION")),
                                    index_uri=build_indicator_uri(self._config, "INDEX"),
                                    provider_name=self._config.get("PROVIDERS", "WF_NAME"),
                                    provider_url=self._config.get("PROVIDERS", "WF_URL"))


    @staticmethod
    def _turn_excell_comp_into_model_comp(excell_comp):
        result = create_component(order=None,
                                  contributor=None,
                                  issued=utc_now(),
                                  label=excell_comp.name,
                                  notation=None,
                                  comment=excell_comp.description)
        return result

    @staticmethod
    def _turn_excell_subin_into_model_subin(excell_subin):
        result = create_sub_index(order=None,
                                  colour=None,
                                  label=excell_subin.name,
                                  notation=None,
                                  comment=excell_subin.description)
        return result

    @staticmethod
    def _create_model_index_object(description):
        result = create_index(order=None,
                              colour=None,
                              label="Index",
                              notation=None,
                              comment=description)
        return result



    def _turn_excell_ind_into_model_ind(self, excell_ind):
        result = create_indicator(_type=excell_ind.type_of_indicator,
                                  country_coverage=self._config.getint("INDICATORS_PARSER",
                                                                       "COUNTRY_COVERAGE"),
                                  provider_link=excell_ind.data_provider,
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
                                 data_provider=self._look_for_data_prov_link(row),
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
                                      weight=self._look_for_group_weight(subindex_name, sheet_group_weights),
                                      description=self._look_for_group_description(subindex_name, sheet_group_weights))
            self._subindexes[subindex_name] = subindex


        #Managing components
        if component_name in self._components:
            component = self._components[component_name]
        else:
            component = ComponentExcell(name=component_name,
                                        weight=self._look_for_group_weight(subindex_name, sheet_group_weights),
                                        description=self._look_for_group_description(component_name, sheet_group_weights))
            subindex.add_component(component)
            self._components[component_name] = component

        #Linking indicator and component
        component.add_indicator(indicator)

    def _look_for_group_weight(self, name, sheet):
        name_col = self._config.getint("INDICATORS_PARSER", "GROUP_NAME_COLUMN")
        weight_col = self._config.getint("INDICATORS_PARSER", "GROUP_WEIGHT_COLUMN")

        for irow in range(0, sheet.nrows):
            if self._normalize_component_name(sheet.row(irow)[name_col].value).upper() == name.upper():
                try:
                    return float(sheet.row(irow)[weight_col].value)
                except BaseException as e:
                    self._log.error("Wrong weight for a grouped entity: {}".format(name))
                    raise ValueError("Wrong weight for a grouped entity: {}".format(name))
        self._log.error("Unable to detect weight for a grouped entity: {}".format(name))
        raise ValueError("Unable to detect weight for a grouped entity: {}".format(name))

    def _look_for_group_description(self, name, sheet):
        name_col = self._config.getint("INDICATORS_PARSER", "GROUP_NAME_COLUMN")
        description_col = self._config.getint("INDICATORS_PARSER", "GROUP_DESCRIPTION_COLUMN")

        for irow in range(0, sheet.nrows):
            if self._normalize_component_name(sheet.row(irow)[name_col].value).upper() == name.upper():
                try:
                    return str(sheet.row(irow)[description_col].value)
                except BaseException as e:
                    self._log.error("Wrong description for a grouped entity: {}".format(name))
                    raise ValueError("Wrong description for a grouped entity: {}".format(name))
        self._log.error("Unable to detect description for a grouped entity: {}".format(name))
        raise ValueError("Unable to detect description for a grouped entity: {}".format(name))

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

        return original.replace("&", "and").capitalize()


    @staticmethod
    def _normalize_subindex_name(original):
        """
        It expects the name of a subindex and return it capitalized.
        Also, if it finds the word "and" it will replace it by the char "&".
        This method has been taken apart thinking that this normalization may change.

        :param original:
        :return:
        """
        return original.replace("&", "and")\
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
            self._log.warning("Some missing weight in indicators. Assuming weight 1, but check excell file.")
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
        if original.endswith("."):
            return original
        else:
            return original + "."


    def _look_for_name(self, row):
        cell = row[self._config.getint("INDICATORS_PARSER", "NAME")]
        if ExcellUtils.is_empty_cell(cell):
            return None
        else:
            return cell.value



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
                 source=None, data_provider=None,
                 latest_rep=None, type_of_indicator=None,
                 weight=None, high_low=None, republish=None):
        self.code = code
        self.name = name
        self.description = description
        self.source = source
        self.data_provider = data_provider
        self.latest_rep = latest_rep
        self.high_low = high_low
        self.type_of_indicator = type_of_indicator
        self.weight = weight
        self.republish = republish

        self.component = None


class ComponentExcell(object):
    def __init__(self, name, weight, description=None):
        self.name = name
        self.weight = weight
        self.subindex = None
        self.description = description
        self.indicators = []

    def add_indicator(self, indicator):
        self.indicators.append(indicator)
        indicator.component = self



class SubIndexExcell(object):
    def __init__(self, name, weight, description=None):
        self.name = name
        self.weight = weight
        self.description = description
        self.components = []

    def add_component(self, component):
        self.components.append(component)
        component.subindex = self



