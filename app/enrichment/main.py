__author__ = 'Dani'

import ConfigParser

from application.wixFetcher.app.enrichment.enricher import Enricher
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.component_repository import ComponentRepository
from infrastructure.mongo_repos.subindex_repository import SubindexRepository
from infrastructure.mongo_repos.index_repository import IndexRepository
from infrastructure.mongo_repos.observation_repository import ObservationRepository
from infrastructure.mongo_repos.area_repository import AreaRepository
from infrastructure.mongo_repos.visualization_repository import VisualizationRepository
from infrastructure.mongo_repos.ranking_repository import RankingRepository


config = ConfigParser.RawConfigParser()
config.read("configuration.ini")


indicators_db = IndicatorRepository(config.get("CONNECTION", "MONGO_IP"))
components_db = ComponentRepository(config.get("CONNECTION", "MONGO_IP"))
subindexes_db = SubindexRepository(config.get("CONNECTION", "MONGO_IP"))
indexes_db = IndexRepository(config.get("CONNECTION", "MONGO_IP"))
observations_db = ObservationRepository(config.get("CONNECTION", "MONGO_IP"))
areas_db = AreaRepository(config.get("CONNECTION", "MONGO_IP"))
visualizations_db = VisualizationRepository(config.get("CONNECTION", "MONGO_IP"))
rankings_db = RankingRepository(config.get("CONNECTION", "MONGO_IP"))

enricher = Enricher(config=config,
                    db_countries=areas_db,
                    db_observations=observations_db,
                    db_indicators=indicators_db,
                    db_visualizations=visualizations_db,
                    db_rankings=rankings_db)

enricher.enrich_secondary_indicator_obs()
enricher.enrich_component_obs()
enricher.enrich_subindex_obs()
enricher.enrich_index_obs()
enricher.enrich_whole_ranking_repo()

