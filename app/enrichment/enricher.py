__author__ = 'Dani'


class Enricher(object):

    def __init__(self, config, db_observations, db_indicators, db_countries, db_visualizations, db_rankings):
        self._config = config
        self._db_observations = db_observations
        self._db_indicators = db_indicators
        self._db_countries = db_countries
        self._db_visualizations = db_visualizations
        self._db_rankings = db_rankings


    ##################################
    #  RANKING COLLECTION ENRICHMENT
    ##################################

    def enrich_internal_ranking_of_observations(self):
        indicators_list = self._get_indicator_codes("Primary") + \
                self._get_indicator_codes("Secondary") + \
                self._get_indicator_codes("Component") + \
                self._get_indicator_codes("Subindex")
        for year in range(2007, 2014):
            for indicator_code in indicators_list:
                observations = self._look_for_observations_of_same_year_and_indicator(year, indicator_code)
                self._actualize_ranking_of_observations_of_same_year_and_indicator(observations)


    def _actualize_ranking_of_observations_of_same_year_and_indicator(self, observations):
        sorted_obs = self._sort_observations_for_ranking(observations)
        previous_value = 99999  # A random value big enough to be higher than any possible value
                            # We will be using s-score or scored values, so the biggest number that
                            # could be found is 100
        previous_rank = 0
        array_pos = 0
        while array_pos < len(sorted_obs):
            target_obs = sorted_obs[array_pos]
            array_pos += 1  # Incrementing array_por for next ite
            current_value = target_obs['values'][0]
            if current_value < previous_value:
                previous_rank = array_pos  # If current is not higher we have a draw and we have to use the same rank
                                            # If it is higher, then rank should be updated with array_pos value

            self._actualize_internal_ranking_of_observation(target_obs, previous_rank)  # At this point, previous_rank
                                                                    # has been set to the correct value

    def _actualize_internal_ranking_of_observation(self, observation_dict, ranking):
        self._db_observations.normalize_plain_observation(area_iso3_code=observation_dict['area'],
                                                          indicator_code=observation_dict['indicator'],
                                                          year_literal=observation_dict['year'],
                                                          normalized_value=ranking,
                                                          computation_type='ranked')


    @staticmethod
    def _sort_observations_for_ranking(observations):
        """
        Return the received list of observation dicts ordered by value (descending)
        :param observations:
        :return:
        """
        return sorted(observations, key=lambda a_dict: a_dict['values'][0], reverse=True)



    def _look_for_observations_of_same_year_and_indicator(self, year, indicator_code):
        observation_dicts = self._db_observations.find_observations(year=str(year),
                                                                    indicator_code=indicator_code)['data']

        return observation_dicts



    ##################################
    #  RANKING COLLECTION ENRICHMENT
    ##################################


    def enrich_whole_ranking_repo(self):
        for year in range(2007, 2014):  # Interval [2007,2013]
            list_of_list = []
            for country_code in self._get_country_codes():
                print year, country_code
                list_of_obs = self._look_for_needed_observations_for_ranking_group(year, country_code)
                list_of_list.append(list_of_obs)
            self._db_rankings.insert_ranking(list_of_list)


    def _look_for_needed_observations_for_ranking_group(self, year, iso3_code):
        """
        It could look better to make a more precise query instead of retrieving more obs to filter it locally...
        But we are reducing from 5 to 1 the number of queries and gaining time.
        :param year:
        :param iso3_code:
        :return:
        """
        observation_dicts = self._db_observations.find_observations(year=str(year),
                                                                    area_code=iso3_code)['data']
        result = []
        for obs_dict in observation_dicts:
            if obs_dict['indicator'] in self._get_subindex_and_index_indicator_codes():
                result.append(obs_dict)
        if len(result) != 5:
            raise ValueError("Not coherent group of observations"
                             " found for building rankinf of {},{}. 5 expected, {} found".format(iso3_code,
                                                                                                 year,
                                                                                                 len(result)))
        return result

    def _get_subindex_and_index_indicator_codes(self):
        if '_subindex_and_index_list' not in self.__dict__:
            self._subindex_and_index_list = self._get_indicator_codes("Index") + \
                                            self._get_indicator_codes("Subindex")
        return self._subindex_and_index_list


    ###############################################
    #  PREVIOUS VALUE AND VISUALIZATION ENRICHMENT
    ###############################################

    def enrich_every_available_obs_with_previous_and_visualization(self):
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Secondary", "normalized")
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Primary", "normalized")
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Component", "scored")
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Subindex", "scored")
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Index", "scored")

    def enrich_secondary_indicator_obs_with_previous_and_visualization(self):
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Secondary", "normalized")
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Primary", "normalized")

    def enrich_component_obs_with_previous_and_visualization(self):
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Component", "scored")

    def enrich_subindex_obs_with_previous_and_visualization(self):
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Subindex", "scored")

    def enrich_index_obs_with_previous_and_visualization(self):
        self._enrich_a_level_of_indicator_obs_with_preious_and_visualization("Index", "scored")

    def _enrich_a_level_of_indicator_obs_with_preious_and_visualization(self, level, computation_type):
        print level, computation_type, "-------------------------------"
        indicator_codes = self._get_indicator_codes(level)
        country_codes = self._get_country_codes()
        for ind_code in indicator_codes:
            for iso_code in country_codes:
                print ind_code, iso_code
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
        if len(observation_dicts) > 0:
            self._db_visualizations.insert_built_visualization(array_values=values,
                                                               area_iso3_code=observation_dicts[0]['area'],
                                                               area_name=observation_dicts[0]['area_name'],
                                                               indicator_code=observation_dicts[0]['indicator'],
                                                               indicator_name=observation_dicts[0]['indicator_name'],
                                                               provider_name=observation_dicts[0]['provider_name'],
                                                               provider_url=observation_dicts[0]['provider_url'])

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
    #####################
    # COMMON UTIL METHODS
    #####################

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


    def _get_indicator_codes(self, _type=None):
        """
        When receiving None, it return all the available indicators

        :param _type:
        :return:
        """
        result = []
        indicator_dicts = self._db_indicators.find_indicators()['data']
        for a_dict in indicator_dicts:
            if _type is None or a_dict['type'] == _type:
                result.append(a_dict['indicator'])
        return result


    def _get_country_codes(self):
        result = []
        countries_dicts = self._db_countries.find_countries(None)['data']
        for a_dict in countries_dicts:
            result.append(a_dict["iso3"])
        return result


