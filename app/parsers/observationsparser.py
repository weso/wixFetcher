__author__ = 'Miguel'
__date__ = '02/09/2014'

import sys

from webindex.domain.model.observation.observation import create_observation
from utility.time import utc_now


class ObservationsParser(object):

    YEAR_ROW = 0
    COUNTRY_COLUMN = 0

    def __init__(self, log, db_observations, db_countries):
        self._log = log
        self._extra_calculator = None
        self._db_observations = db_observations
        self._country_list = self._initialize_country_list(db_countries)  # It will contain a dictionary of [name] --> [code]


    @staticmethod
    def _initialize_country_list(db_countries):
        result = {}
        country_dicts = db_countries.find_countries()['data']
        for a_dict in country_dicts:
            result[a_dict['name']] = a_dict['iso3']
        return result


    def parse_data_sheet(self, sheet):
        '''
        Parses the rows of an Excel file retrieving the countries.

        :param sheet: the Excel sheet object with all the data
        :return: None (for now)
        '''
        self._extra_calculator = ExtraCalculator(sheet)
        # sys.stdout.write("\n---------" + sheet.name + "---------\n")
        i = 1
        while i < sheet.nrows:
            country_name = sheet.col(self.COUNTRY_COLUMN)[i].value
            if country_name in [None, "", " "]:  # It means we have ended countries. Means and DVs come.
                break
            # sys.stdout.write("  " + country_name)

            self._parse_country_data(sheet, i, country_name, sheet.name)
            # sys.stdout.write("\n")
            i += 1
        # print "\n"

    def _parse_country_data(self, sheet, row, country_name, sheet_name):
        """
        Parses the indicator's values of a country for each year given the row of that country in the Excel file.
        Then introduce the obtained observations into the database

        :param sheet: the Excel sheet object with all the data
        :param row: the Excel row in which are the indicator's values of a country for each year
        :return: None (for now)
        """

        i = 1
        while i < sheet.ncols - 2:
            # -2 because there's one more column due to the new countries note. Should be -1 in future cases.
            obs_value = sheet.row(row)[i].value
            if obs_value in [None, "", " ", ".", "..", "...", "...."]:
                break
            year_value = int(sheet.row(ObservationsParser.YEAR_ROW)[i].value)
            # sys.stdout.write("\n    " + str(year_value) + " -> " + str(obs_value))
            model_obs = self._create_observation(obs_value, year_value, country_name, sheet_name)
            self._db_observations.insert_observation(model_obs)
            i += 1

    def _create_observation(self, obs_value, year_value, country_name, sheet_name):
        """
        This method creates observation object from all the received parameters

        :param obs_value: numeric value of the observation
        :param year_value: integer value containing the year which the observation is referring
        :param country_name: complete name of the country which the observation is referring
        :param sheet_name: contains the name of the original excell sheet. indicator code and type of computation can be obtained parsing it

        :return: The observation created
        """

        indicator_code, computation_type = self._obtain_indicator_code_and_computation_type_from_sheet_name(sheet_name)
        print "Observacion con valor", obs_value, "para el year", year_value, "de", indicator_code, " y tipo", computation_type, "con country", country_name
        observation = create_observation(issued=utc_now(),
                                         publisher=None, # Uneeded at this point
                                         data_set=None,
                                         obs_type="raw",  # Just for now
                                         label=self._build_label_for_observation(indicator_code,
                                                                                 country_name,
                                                                                 year_value,
                                                                                 computation_type),
                                         status=computation_type,  # really, uneeded at this point
                                         ref_indicator=indicator_code,  # Again, maybe this should point to indicator id,
                                                                        # but works nice for me. At this point i don't
                                                                        #know about ids, but codes.
                                         value=obs_value,
                                         ref_area=self._get_country_code_by_name(country_name),  # Maybe this
                                                                # is not correct, but perfectly works for me.
                                                                # Again, it may should be pointing to an ID
                                         ref_year=year_value)  # Maybe an entity, but works nice for my purposes.

        # self._add_propper_computation_to_observation(observation, computation_type)
        return observation


    def _get_country_code_by_name(self, country_name):
        if country_name not in self._country_list:
            possibly_correction = self._look_for_country_name_exception(country_name)
            if possibly_correction is None:
                self._log.warning("Unrecognized country")
                raise BaseException("Carefull here...")
            else:
                return self._get_country_code_by_name(possibly_correction)
        else:
            return self._country_list[country_name]

    @staticmethod
    def _look_for_country_name_exception(original):
        if original in ['Republic of Korea', 'Republic Of Korea']:
            return 'Korea (Rep. of)'
        elif original in ['Russia']:
            return "Russian Federation"
        elif original in ['Tanzania', "United Republic of Tanzania", "United Republique of Tanzania"]:
            return "United Republic Of Tanzania"
        elif original in ['United States', 'United States of America']:
            return 'United States Of America'
        elif original in ['United Kingdom', 'United Kingdom of Great Britain and Northern Ireland']:
            return 'United Kingdom Of Great Britain And Northern Ireland'
        elif original in ['Venezuela']:
            return 'Venezuela (Bolivarian Republic Of)'
        else:
            return None

    ####### THE NEXT METHOD LOOKS UNNECESARY AT THIS POINT, BUT MAY BE HELPFULL IN FUTURE

    # def _add_propper_computation_to_observation(self, observation, computation_type):
    #     if computation_type == "raw":
    #         observation.add_computation(_type="raw")
    #     elif computation_type == "ranked":
    #         observation.add_computation(_type="ranked",
    #                                     reason="",  # TODO: ??
    #                                     _slice=None,
    #                                     dimension=None)  # TODO: probably not None
    #     elif computation_type == "normalized":
    #         observation.add_computation(_type="normalized",
    #                                     mean=self._get_mean(observation),
    #                                     std_deviation=self._get_std_desv(observation),
    #                                     _slice=None)  # TODO: Probably incorrect
    #
    #     elif computation_type == "scored":
    #         observation.add_computation(_type="scored",
    #                                     value_max=self._get_value_max(observation),
    #                                     value_min=self._get_value_min(observation),
    #                                     slice=None)  # TODO: probably wrong
    #
    #     elif computation_type == "grouped":
    #         observation.add_computation(_type="grouped")
    #         # , ... )
    #         #TODO. As i see in the old version through wesby, there are more!



    @staticmethod
    def _build_label_for_observation(indicator_code, country_name, year_value, status):
        return indicator_code + " " + status + " in " + country_name + " during " + str(year_value)


    def _obtain_indicator_code_and_computation_type_from_sheet_name(self, sheet_name):
        """
        Receives the name of an excell sheet and extract form it two fields: indicator_code and computation_type

        :param sheet_name: the name of the excell sheet, expected to be formed by the two wanted fields
        :return: two results. firts, indicator code. Then, type of computation
        """
        array_data = sheet_name.split("_")
        indicator_code = array_data[0]
        for i in range(1, len(array_data) - 1):
            indicator_code += "_" + array_data[i]
        raw_computation_type = array_data[len(array_data) - 1]
        return indicator_code, self._normalize_computation_type(raw_computation_type)

    def _normalize_computation_type(self, raw_computation_type):
        """
        It receives a name that contains a computation type name, possibly in a non-standar format.
        Ir recognizes it and turn it in a normalized format

        :param raw_computation_type:
        :return: normalized name of computation type
        """

        if raw_computation_type in ["Imputed", "imputed"]:
            return "ranked"  #TODO: ensure this is the correct type to return.... not really sure about this.
        # if....

        #In case of not matching with any if...
        self._log.error("Unknown computation time extracted from sheet name: " + raw_computation_type + ".")
        return "Unknown"

    def _get_mean(self, observation):
        return self._extra_calculator.get_mean(observation.ref_year)

    def _get_std_desv(self, observation):
        return self._extra_calculator.get_std_deriv(observation.ref_year)

    def _get_value_min(self, observation):
        return self._extra_calculator.get_min(observation.ref_year)

    def _get_value_max(self, observation):
        return self._extra_calculator.get_max(observation.ref_year)


class ExtraCalculator(object):
    """
    It offers data obtained from the composition of several values in a column (for a concrete year)

    """

    ROW_OF_YEARS = 0
    ROW_START_COUNTRIES = 1
    ROW_END_COUNTRIES = 81
    ROW_OF_MEAN = 83
    ROW_OF_SD = 85

    def __init__(self, sheet):
        self._sheet = sheet
        self._means = {}
        self._std_dervis = {}
        self._mins = {}
        self._maxs = {}

    def get_mean(self, year):
        if not year in self._means:
            self._calculate_mean(year)
        return self._means[year]


    def get_std_deriv(self, year):
        if not year in self._std_dervis:
            self._calculate_std_deriv(year)
        return self._std_dervis[year]


    def get_min(self, year):
        if not year in self._mins:
            self._calculate_min_max(year)
        return self._mins


    def get_max(self, year):
        if not year in self._maxs:
            self._calculate_min_max(year)
        return self._maxs[year]


    def _calculate_min_max(self, year):
        column_index = self._detect_column_of_year(year)
        min_value = None
        max_value = None
        for i in range(self.ROW_START_COUNTRIES, self.ROW_END_COUNTRIES + 1):
            temp_value = self._sheet.row(i)[column_index].value
            if min is None or temp_value < min:
                min_value = temp_value
            if max is None or temp_value > max:
                max_value = temp_value
        self._mins[year] = min_value
        self._maxs[year] = max_value

    def _calculate_mean(self, year):
        column = self._detect_column_of_year(year)
        mean_value = self._sheet.row(self.ROW_OF_MEAN)[column]
        self._means[year] = mean_value

    def _calculate_std_deriv(self, year):
        column = self._detect_column_of_year(year)
        std_dev = self._sheet.row(self.ROW_OF_SD)[column]
        self._std_dervis[year] = std_dev


    def _detect_column_of_year(self, year):
        """
        It return the index of the column in which the data associated with the year received are placed

        :param year:
        :return:
        """

        for i in range(1, self._sheet.ncols):
            cell = self._sheet.row(self.ROW_OF_YEARS)[i]
            if cell.value == year:
                return i

        raise RuntimeError(" Trying to find a year not contained in a sheet. Year " + year + ", sheet " + self._sheet.name)


