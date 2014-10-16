__author__ = 'Dani'

from ..extractor import Extractor
from .secondaryindicatorsparser import SecondaryIndicatorsParser
from .primaryindicatorsparser import PrimaryIndicatorsAndGroupsParser
from .secondaryobservationsparser import SecondaryObservationsParser
from .primaryobservationsparser import PrimaryObservationsParser
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.component_repository import ComponentRepository
from infrastructure.mongo_repos.subindex_repository import SubindexRepository
from infrastructure.mongo_repos.index_repository import IndexRepository
from infrastructure.mongo_repos.observation_repository import ObservationRepository
from infrastructure.mongo_repos.area_repository import AreaRepository
from infrastructure.mongo_repos.visualization_repository import VisualizationRepository


class Parser(object):


    def __init__(self, log, config):
        self._log = log
        self._config = config

    def run(self, book):
        self._log.info("########################################")  # Mark a new execution
        self._log.info("Parsing process started......")
        try:
            self._log.info("Connecting with databases")
            #Extracting sheets
            extractor = Extractor(self._log, book)
            sheets = extractor.get_data_sheets()
            indicators_db = IndicatorRepository(self._config.get("CONNECTION", "MONGO_IP"))
            components_db = ComponentRepository(self._config.get("CONNECTION", "MONGO_IP"))
            subindexes_db = SubindexRepository(self._config.get("CONNECTION", "MONGO_IP"))
            indexes_db = IndexRepository(self._config.get("CONNECTION", "MONGO_IP"))
            observations_db = ObservationRepository(self._config.get("CONNECTION", "MONGO_IP"))
            areas_db = AreaRepository(self._config.get("CONNECTION", "MONGO_IP"))
            visualizations_db = VisualizationRepository(self._config.get("CONNECTION", "MONGO_IP"))

            self._log.info("Successfully connected to databases")


            # Parsing indicatros
            self._log.info("Parsing secondary indicators... ")
            secondary_indicators_parser = SecondaryIndicatorsParser(log=self._log,
                                                                    config=self._config,
                                                                    db=indicators_db)
            secondary_indicators_parser.\
                parse_indicators_sheet(sheets[self._config.getint("PARSER",
                                                                  "_SECONDARY_INDICATOR_METADATA_SHEET")],
                                       sheets[self._config.getint("PARSER",
                                                                  "_PRIMARY_INDICATOR_METADATA_SHEET")])
            self._log.info("Secondary indicators parsed... ")

            self._log.info("Parsing primary indicators and groups... ")
            primary_indicators_parser = PrimaryIndicatorsAndGroupsParser(log=self._log,
                                                                         config=self._config,
                                                                         db_indicator=indicators_db,
                                                                         db_component=components_db,
                                                                         db_subindex=subindexes_db,
                                                                         db_index=indexes_db)
            primary_indicators_parser.\
                parse_indicators_sheet(sheets[self._config.getint("PARSER",
                                                                  "_PRIMARY_INDICATOR_METADATA_SHEET")])
            self._log.info("Primary indicators and groups parsed... ")

            # Parsing observations

            self._log.info("Parsing secondary observations... ")
            secondary_observations_parser = SecondaryObservationsParser(log=self._log,
                                                                        config=self._config,
                                                                        db_observations=observations_db,
                                                                        db_countries=areas_db,
                                                                        db_indicators=indicators_db,
                                                                        db_visualizations=visualizations_db)
            sec_indicators_count = 0
            for i in range(self._config.getint("PARSER", "_FIRST_OBSERVATIONS_SHEET"), len(sheets) - 2):
                secondary_observations_parser.parse_data_sheet(sheets[i])
                sec_indicators_count += 1

            self._log.info("Secondary indicators with observations: {}".format(sec_indicators_count))
            self._log.info("Secondary observations parsed... ")
            self._log.info("Parsing primary observations... ")
            primary_observations_parser = PrimaryObservationsParser(log=self._log,
                                                                    config=self._config,
                                                                    db_observations=observations_db,
                                                                    db_countries=areas_db,
                                                                    db_indicators=indicators_db,
                                                                    db_visualizations=visualizations_db)
            primary_observations_parser.parse_data_sheet(sheets[len(sheets) - 2])
            self._log.info("Primary observations parsed... ")
            self._log.info("Parsing process ended......")

        except BaseException as e:
            print "Parsing process finalized abruptly. Check logs"  # Put this print in some other place
            self._log.error("Parsing process finalized abruptly. Cause: {}".format(str(e)))

