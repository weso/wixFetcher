__author__ = 'Dani'


class Enricher(object):

    def __init__(self, config, db_observations, db_indicators, db_countries, db_visualizations):
        self._config = config
        self._db_observations = db_observations
        self._db_indicators = db_indicators
        self._db_countries = db_countries
        self._db_visualizations = db_visualizations


    def enrich_every_available_obs(self):
        self._enrich_a_level_of_indicator_obs("Secondary", "normalized")
        self._enrich_a_level_of_indicator_obs("Component", "scored")
        self._enrich_a_level_of_indicator_obs("Subindex", "scored")
        self._enrich_a_level_of_indicator_obs("Index", "scored")

    def enrich_secondary_indicator_obs(self):
        self._enrich_a_level_of_indicator_obs("Secondary", "normalized")

    def enrich_component_obs(self):
        self._enrich_a_level_of_indicator_obs("Component", "scored")

    def enrich_subindex_obs(self):
        self._enrich_a_level_of_indicator_obs("Subindex", "scored")

    def enrich_index_obs(self):
        self._enrich_a_level_of_indicator_obs("Index", "scored")

    def _enrich_a_level_of_indicator_obs(self, level, computation_type):
        print level, computation_type
        indicator_codes = self._get_indicator_codes(level)
        country_codes = self._get_country_codes()
        for ind_code in indicator_codes:
            for iso_code in country_codes:
                observation_dicts = self._db_observations.find_observations(indicator_code=ind_code,
                                                                            area_code=iso_code)['data']
                self._enrich_observations_of_same_iso_and_ind(observation_dicts, computation_type)


    def _enrich_observations_of_same_iso_and_ind(self, observation_dicts, computation_type):
        self._enrich_iso_ind_observations_with_previous_value(observation_dicts, computation_type)
        self._enrich_iso_ind_observations_generating_visualization(observation_dicts, computation_type)

    def _enrich_iso_ind_observations_generating_visualization(self, observation_dicts, computation_type):
        first_year, last_year = self._db_visualizations.get_first_and_last_year()
        values = []
        for year in range(first_year, last_year + 1):
            value = self._look_for_a_value_for_a_year(year, observation_dicts, computation_type)
            if value is not None:
                value = round(value, 2)
            values.append(value)
        self._db_visualizations


    @staticmethod
    def _look_for_a_value_for_a_year(year_target, observations, desired_type):
        for obs in observations:
            year_obs = obs['year']
            if str(year_obs) == str(year_target):
                if desired_type is None:
                    return obs['value']
                elif desired_type in ['scored', 'normalized']:
                    return obs[desired_type]
                else:
                    raise ValueError("Unknown computation {} asked for an obs".format(desired_type))
        return None  # No observation found for target_year in this list



    def _enrich_iso_ind_observations_with_previous_value(self, observation_dicts, computation_type):
        for obs_dict in observation_dicts:
            previous_dict = self._look_for_previous_dict(observation_dicts, int(obs_dict['year']))
            if previous_dict is not None:
                self._enrich_observation_from_it_previous_observation(obs_dict, previous_dict, computation_type)


    def _enrich_observation_from_it_previous_observation(self, target_dict, old_dict, computation_type):
        current_value = self._look_for_value(target_dict, computation_type)
        previous_value = self._look_for_value(old_dict, computation_type)
        tendency = 0
        if current_value < previous_value:
            tendency = -1
        elif current_value > previous_value:
            tendency = 1
        self._db_observations.update_previous_value_object(indicator_code=target_dict['indicator'],
                                                           area_code=target_dict["area"],
                                                           current_year=target_dict['year'],
                                                           previous_year=old_dict['year'],
                                                           previous_value=previous_value,
                                                           tendency=tendency)


    @staticmethod
    def _look_for_value(obs_dict, computation_type):
        if obs_dict[computation_type] is not None:
            return obs_dict[computation_type]
        return obs_dict['value']  # If the previous is null



    @staticmethod
    def _look_for_previous_dict(observation_dicts, year):
        result = None
        for obs in observation_dicts:
            tmp_year = int(obs['year'])
            if tmp_year < year:
                if result is None:
                    result = obs
                elif int(result['year']) < tmp_year:
                    result = obs
        return result


    def _get_indicator_codes(self, type):
        result = []
        indicator_dicts = self._db_indicators.find_indicators()['data']
        for a_dict in indicator_dicts:
            if a_dict['type'] == type:
                result.append(a_dict['indicator'])
        return result

    def _get_country_codes(self):
        result = []
        countries_dicts = self._db_countries.find_countries(None)['data']
        for a_dict in countries_dicts:
            result.append(a_dict["iso3"])
        return result


