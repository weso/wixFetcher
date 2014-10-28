import logging
import ConfigParser
import xlrd
from application.wixFetcher.app.computation.computation_parser import ComputationParser
from application.wixFetcher.app.computation.computation_validation import ComputationValidation
from application.wixFetcher.app.enrichment.enricher import Enricher
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.observation_repository import ObservationRepository
from infrastructure.mongo_repos.area_repository import AreaRepository
from infrastructure.mongo_repos.visualization_repository import VisualizationRepository
from infrastructure.mongo_repos.ranking_repository import RankingRepository
from application.wixFetcher.app.parsers.parser import Parser

__author__ = 'Miguel'


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wixfetcher.log', level=logging.INFO,
                        format=FORMAT)


def run():
    configure_log()
    log = logging.getLogger('wixfetcher')
    config = ConfigParser.RawConfigParser()
    config.read("configuration.ini")
    parser = Parser(log=log,
                    config=config)
    book = xlrd.open_workbook("data_file.xlsx")
    parser.run(book)

    comp_parser = ComputationParser(log, config)
    comp_parser.run()
    comp_validation = ComputationValidation(log, config)
    comp_validation.run()

    indicators_db = IndicatorRepository(config.get("CONNECTION", "MONGO_IP"))
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

    enricher.enrich_every_available_obs_with_previous_and_visualization()
    enricher.enrich_whole_ranking_repo()


if __name__ == '__main__':
    run()
    print '\nDone!'