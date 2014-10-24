__author__ = 'Dani'

from application.wixFetcher.app.parsers.utils import initialize_country_dict, random_float, build_observation_uri, deduce_previous_value_and_year
from webindex.domain.model.observation.observation import create_observation
from webindex.domain.model.observation.year import Year
from utility.time import utc_now


class Dumizer(object):

    def __init__(self, config, db_observations, db_indicators, db_countries, db_visualizations):
        self.config = config
        self.db_observations = db_observations
        self.db_indicators = db_indicators
        self.db_countries = db_countries
        self.db_visualizations = db_visualizations



    def introduce_fake_components(self):
        comp_dicts = self._get_indicator_dicts("Component")
        country_dicts = initialize_country_dict(db_countries=self.db_countries)
        for comp_code in comp_dicts:
            for country_name in country_dicts:
                observations = []
                for year in range(2007, 2013):
                    model_obs = self._create_comp_or_subindex_obs(year)
                    observations.append(model_obs)
                    previous_value, previous_year = deduce_previous_value_and_year(observations, year)
                    self.db_observations.insert_observation(observation=model_obs,
                                                            observation_uri=build_observation_uri(config=self.config,
                                                                                                  ind_code=comp_code,
                                                                                                  iso3_code=country_dicts[country_name],
                                                                                                  year=year),
                                                            area_iso3_code=country_dicts[country_name],
                                                            area_name=country_name,
                                                            indicator_code=comp_code,
                                                            indicator_name=comp_dicts[comp_code],
                                                            previous_value=previous_value,
                                                            year_of_previous_value=previous_year,
                                                            republish=True)
                # self.db_visualizations.insert_visualization(observations=observations,
                #                                             area_iso3_code=country_dicts[country_name],
                #                                             area_name=country_name,
                #                                             indicator_code=comp_code,
                #                                             indicator_name=comp_dicts[comp_code])



    def introduce_fake_subindex(self):
        subin_dicts = self._get_indicator_dicts("Subindex")
        country_dicts = initialize_country_dict(db_countries=self.db_countries)
        for subin_code in subin_dicts:
            for country_name in country_dicts:
                observations = []
                for year in range(2007, 2013):
                    model_obs = self._create_comp_or_subindex_obs(year)
                    observations.append(model_obs)
                    previous_value, previous_year = deduce_previous_value_and_year(observations, year)
                    self.db_observations.insert_observation(observation=model_obs,
                                                            observation_uri=build_observation_uri(config=self.config,
                                                                                                  ind_code=subin_code,
                                                                                                  iso3_code=country_dicts[country_name],
                                                                                                  year=year),
                                                            area_iso3_code=country_dicts[country_name],
                                                            area_name=country_name,
                                                            indicator_code=subin_code,
                                                            indicator_name=subin_dicts[subin_code],
                                                            previous_value=previous_value,
                                                            year_of_previous_value=previous_year,
                                                            republish=True)
                # self.db_visualizations.insert_visualization(observations=observations,
                #                                             area_iso3_code=country_dicts[country_name],
                #                                             area_name=country_name,
                #                                             indicator_code=subin_code,
                #                                             indicator_name=subin_dicts[subin_code])


    def introduce_fake_index(self):
        index_dicts = self._get_indicator_dicts("Index")
        country_dicts = initialize_country_dict(db_countries=self.db_countries)
        for index_code in index_dicts:
            for country_name in country_dicts:
                observations = []
                for year in range(2007, 2013):
                    model_obs = self._create_index_obs(year)
                    observations.append(model_obs)
                    previous_value, previous_year = deduce_previous_value_and_year(observations, year)
                    self.db_observations.insert_observation(observation=model_obs,
                                                            observation_uri=build_observation_uri(config=self.config,
                                                                                                  ind_code=index_code,
                                                                                                  iso3_code=country_dicts[country_name],
                                                                                                  year=year),
                                                            area_iso3_code=country_dicts[country_name],
                                                            area_name=country_name,
                                                            indicator_code=index_code,
                                                            indicator_name=index_dicts[index_code],
                                                            previous_value=previous_value,
                                                            year_of_previous_value=previous_year,
                                                            republish=True)
                # self.db_visualizations.insert_visualization(observations=observations,
                #                                             area_iso3_code=country_dicts[country_name],
                #                                             area_name=country_name,
                #                                             indicator_code=index_code,
                #                                             indicator_name=index_dicts[index_code])




    @staticmethod
    def _create_index_obs(year_value):   
        observation = create_observation(issued=utc_now(),
                                         publisher=None,
                                         data_set=None,
                                         obs_type="scored",
                                         label=None,
                                         status="scored",
                                         value=random_float(0, 100),
                                         ref_area=None,
                                         ref_year=None)
        observation.ref_year = Year(year_value)
        return observation

    @staticmethod
    def _create_comp_or_subindex_obs(year_value):
        observation = create_observation(issued=utc_now(),
                                         publisher=None,
                                         data_set=None,
                                         obs_type="normalized",
                                         label=None,
                                         status="normalized",
                                         value=random_float(-2, 2),
                                         ref_area=None,
                                         ref_year=None)
        observation.ref_year = Year(year_value)
        observation.add_computation("scored", random_float(0,100))
        return observation



    def _get_indicator_dicts(self, _type):
        result = {}
        indicator_dicts = self.db_indicators.find_indicators()['data']
        for a_dict in indicator_dicts:
            if a_dict["type"] == _type:
                result[a_dict["indicator"]] = a_dict["name"]
        return result






