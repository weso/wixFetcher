__author__ = 'Dani'


from .utils import initialize_country_dict, look_for_country_name_exception, build_label_for_observation, _is_empty_value
from webindex.domain.model.observation.observation import create_observation
from utility.time import utc_now


class PrimaryObservationsParser(object):



    def __init__(self, log, db_observations, db_countries, config):
        self._log = log
        self._config = config
        self._db_observations = db_observations
        self._country_dict = initialize_country_dict(db_countries)  # It will contain a dictionary of [name] --> [code]


    def parse_data_sheet(self, sheet):
        """
        It process the rows of the survey indicators in order to extract every available
        observation and persist it with the repository "db_observations"

        :param sheet: the excell sheet object with all the data
        :return:
        """
        self._log.info("Parsing sheet {}...".format(sheet.name))
        country_count = 0
        obs_count = 0
        indicator_year_by_column_dict = self._build_indicator_year_by_column_dict(sheet)
        irow = self._config.getint("PRIMARY_OBSERVATIONS_PARSER", '_FIRST_DATA_ROW_PRIMARY_OBSERVATIONS')
        while irow < sheet.nrows:
            try:
                country_name = self._parse_country_name(sheet, irow)
                if country_name is None:
                    break  # It means we have ended countries
                country_name += 1
                for icol in range(self._config.getint("PRIMARY_OBSERVATIONS_PARSER",
                                                      '_FIRST_DATA_COL_PRIMARY_OBSERVATIONS'),
                                  sheet.ncols):
                    model_obs = self._build_model_obs(sheet=sheet,
                                                      row=irow,
                                                      col=icol,
                                                      country_name=country_name,
                                                      indicator_year_dict=indicator_year_by_column_dict)
                    if model_obs is None:
                        self._log.warning("Unexpected empty value in primary observations: row {}, col {}."
                                          .format(irow + 1,
                                                  icol + 1))
                    else:
                        obs_count +=1
                        self._db_observations.insert_observation(observation=model_obs,
                                                                 area_iso3_code=self._get_country_code_by_name(country_name),
                                                                 indicator_code=indicator_year_by_column_dict[icol].indicator,
                                                                 year_literal=indicator_year_by_column_dict[icol].year)
            except ValueError as e:
                self._log.error("ERROR while parsing row {} of sheet {}: {}. "
                                "Parsing process will continue in the next row.".format(irow + 1,
                                                                                        sheet.name,
                                                                                        str(e)))
            irow += 1
        indicators_count = self._count_number_of_indicators_detected(indicator_year_by_column_dict)
        self._log.info("Parsing sheet {} ended... {} countries, {} indicators, {} observations".format(sheet.name,
                                                                                                       country_count,
                                                                                                       indicators_count,
                                                                                                       obs_count))
    @staticmethod
    def _count_number_of_indicators_detected(ind_dict):
        """
        It receives a dict that has as value IndicatorYear objects and count
        the number of different indicators names found in them.

        :param ind_dict:
        :return:
        """
        different_names = []
        for key in ind_dict:
            if ind_dict[key].indicator not in different_names:
                different_names.append(ind_dict[key])
        return len(different_names)

    @staticmethod
    def _build_model_obs(sheet, row, col, country_name, indicator_year_dict):
        """
        It receives an excell sheet, two coordinates to find a data and a
        dict with extra info, and returns a model observation with the
        information found.
        :param sheet
        :param row:
        :param col:
        :param country_name
        :param indicator_year_dict
        :return:
        """
        value = sheet.row(row)[col].value
        if _is_empty_value(value):
            return None
        else:
            return create_observation(issued=utc_now(),
                                      publisher="Webindex",
                                      data_set=None,
                                      obs_type="raw",
                                      label=build_label_for_observation(indicator_year_dict[col].indicator,
                                                                        country_name,
                                                                        indicator_year_dict[col].year,
                                                                        "raw"),
                                      status="raw",
                                      ref_indicator=None,
                                      value=sheet.row(row)[col].value,
                                      ref_area=None,
                                      ref_year=None
                                      )

    def _get_country_code_by_name(self, country_name):
        if country_name not in self._country_dict:
            possibly_correction = look_for_country_name_exception(country_name)
            if possibly_correction is None:
                self._log.error("Unrecognized country {}. Parsing process will continue anyway.")
                raise ValueError("Unrecognized country: {}".format(country_name))
            else:
                return self._get_country_code_by_name(possibly_correction)
        else:
            return self._country_dict[country_name]


    @staticmethod
    def _parse_country_name(sheet, row):
        result = sheet.row(row)[0].value
        if result in [None, "", " "]:
            return None
        return result

    def _build_indicator_year_by_column_dict(self, sheet):
        """
        It returns a dictionary of the form [integer] ==> [IndicatorYear] where IndicatorYear
        is an entity storing the code of and indicator and a concrete year and the integuer
        number represents the column index qhere it is placed in the excell sheet.

        :return:
        """
        result = {}
        for i in range(self._config.getint("PRIMARY_OBSERVATIONS_PARSER",
                                           '_FIRST_DATA_COL_PRIMARY_OBSERVATIONS'),
                       sheet.ncols):
            result[i] = self._parse_indicator_year(sheet.row(0)[i].value)
        return result

    @staticmethod
    def _parse_indicator_year(original_string):
        """
        It expects receiving a string such as "WI.XXXX.YYY", where XXXX is a year
        and YYY an indicator code. It returns an IndicatorYear object with those
        two values.
        """
        # TODO: assertions
        array_str = original_string.split(".")
        if len(array_str) != 3:
            raise ValueError("Primary observations: Unrecognized format of header: {} ".format(original_string))
        else:
            return IndicatorYear(indicator_code_string=array_str[2],
                                 year_string=array_str[1])


class IndicatorYear(object):
    """
    This is just an entity that stores toguether an indicator code and a year

    """
    def __init__(self, indicator_code_string, year_string):
        self.indicator = indicator_code_string
        self.year = year_string



