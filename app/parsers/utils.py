__author__ = 'Dani'


def initialize_country_dict(db_countries):
    """
    It returns a dictionary of the form [name] ==> [code_iso3] containing all the countries
    stored in the received mongo areas repository

    :param db_countries:
    :return:
    """
    result = {}
    country_dicts = db_countries.find_countries()['data']
    for a_dict in country_dicts:
        result[a_dict['name']] = a_dict['iso3']
    return result


def look_for_country_name_exception(original):
    if original in ['Republic of Korea', 'Republic Of Korea']:
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
    else:
        return None


def build_label_for_observation(indicator_code, country_name, year_value, status):
    return indicator_code + " " + status + " in " + country_name + " during " + str(year_value)


def _is_empty_value(value):
    if value in [None, "", " ", ".", "..", "...", "...."]:
        return True
    return None
