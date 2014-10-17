__author__ = 'Dani'


def initialize_country_dict(db_countries):
    """
    It returns a dictionary of the form [name] ==> [code_iso3] containing all the countries
    stored in the received mongo areas repository

    :param db_countries:
    :return:
    """
    result = {}
    country_dicts = db_countries.find_countries(order=None)['data']
    for a_dict in country_dicts:
        result[a_dict['name']] = a_dict['iso3']
    return result


def initialize_indicator_dict(db_indicators):
    """
    It returns a dictionary of the form [code] ==> [name] containing data of every available
    indicator, component subindex or index in the system

    :param db_indicators:
    :return:
    """
    result = {}
    indicator_dicts = db_indicators.find_indicators_indicators()['data']
    for a_dict in indicator_dicts:
        result[a_dict['indicator']] = a_dict['name']
    return result



def look_for_country_name_exception(original):
    if original in ['Republic of Korea', 'Republic Of Korea', 'Korea, Rep.']:
        return 'Korea (Rep. of)'
    elif original in ['Russia']:
        return "Russian Federation"
    elif original in ['Tanzania', "United Republic of Tanzania", "United Republique of Tanzania"]:
        return "United Republic Of Tanzania"
    elif original in ['United States', 'United States of America', 'USA', 'US']:
        return 'United States Of America'
    elif original in ['United Kingdom', 'United Kingdom of Great Britain and Northern Ireland', 'UK']:
        return 'United Kingdom Of Great Britain And Northern Ireland'
    elif original in ['Venezuela', 'Venezuela, RB']:
        return 'Venezuela (Bolivarian Republic Of)'
    elif original in ['UAE']:
        return "United Arab Emirates"
    elif original in ['Egypt, Arab Rep.']:
        return "Egypt"
    elif original in ['Yemen, Rep.']:
        return 'Yemen'
    elif original in ['Viet nam']:
        return 'Viet Nam'
    else:
        return None


def build_label_for_observation(indicator_code, country_name, year_value, status):
    return indicator_code + " " + status + " in " + country_name + " during " + str(year_value)


def _is_empty_value(value):
    if value in [None, "", " ", ".", "..", "...", "...."]:
        return True
    return None


def build_indicator_uri(config, ind_code):
    return config.get("URI", "HOST") + "/indicators/" + normalize_code_for_uri(ind_code)


def build_observation_uri(config, ind_code, iso3_code, year):
    """
    Structure: {HOST}/observations/{IND_CODE}/{ISO3}/{YEAR}
    :param config:
    :param ind_code:
    :param iso3_code:
    :param year:
    :return:
    """
    return config.get("URI", "HOST") + "/observations/" \
        + normalize_code_for_uri(ind_code) + "/" \
        + normalize_code_for_uri(iso3_code) + "/" \
        + str(year)


def normalize_code_for_uri(original):
    result = original.upper().replace(" ", "_").replace("-", "_")
    while "__" in result:
        result = result.replace("__", "_")
    return result


def normalize_component_code_for_uri(original):
    return original.replace("Relevant ", "")\
        .replace("relevant ", "")\
        .replace("&", "and")


def normalize_subindex_code_for_uri(original):
    return original.replace("and", "&")\
        .replace("And", "&")


def deduce_previous_value_and_year(observations, year_target):
    """
    It receives an array of observations and a target year. and returns the value and the year of the
    observation which date is lower but as near as possible to "year_value". In case there are no older
    observetions, it returns a double None


    :param observation:
    :param year_target
    :return:
    """
    result_value = None
    result_year = None
    for obs in observations:
        numeric_obs_year = int(obs.ref_year.value)
        if numeric_obs_year < year_target:
            if result_value is None:
                result_value = obs.value
                result_year = numeric_obs_year
            elif numeric_obs_year > result_year:
                result_value = obs.value
                result_year = numeric_obs_year
            else:
                pass
    return result_value, result_year




