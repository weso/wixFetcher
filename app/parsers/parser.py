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


class Parser(object):


    def __init__(self, log, config):
        self._log = log
        self._config = config

    def run(self, book):
        #Extracting sheets
        extractor = Extractor(self._log, book)
        sheets = extractor.get_data_sheets()
        indicators_db = IndicatorRepository(self._config.get("CONNECTION", "MONGO_IP"))
        components_db = ComponentRepository(self._config.get("CONNECTION", "MONGO_IP"))
        subindexes_db = SubindexRepository(self._config.get("CONNECTION", "MONGO_IP"))
        indexes_db = IndexRepository(self._config.get("CONNECTION", "MONGO_IP"))
        observations_db = ObservationRepository(self._config.get("CONNECTION", "MONGO_IP"))
        areas_db = AreaRepository(self._config.get("CONNECTION", "MONGO_IP"))


        # Parsign indicatros
        secondary_indicators_parser = SecondaryIndicatorsParser(log=self._log,
                                                                config=self._config,
                                                                db=indicators_db)
        secondary_indicators_parser.\
            parse_indicators_sheet(sheets[self._config.getint("PARSER", "_SECONDARY_INDICATOR_METADATA_SHEET")])

        primary_indicators_parser = PrimaryIndicatorsAndGroupsParser(log=self._log,
                                                                     config=self._config,
                                                                     db_indicator=indicators_db,
                                                                     db_component=components_db,
                                                                     db_subindex=subindexes_db,
                                                                     db_index=indexes_db)
        primary_indicators_parser.\
            parse_indicators_sheet(sheets[self._config.getint("PARSER", "_PRIMARY_INDICATOR_METADATA_SHEET")])

        # Parsing observations

        secondary_observations_parser = SecondaryObservationsParser(log=self._log,
                                                                    config=self._config,
                                                                    db_observations=observations_db,
                                                                    db_countries=areas_db)
        for i in range(self._config.getint("PARSER", "_FIRST_OBSERVATIONS_SHEET"), len(sheets) - 2):
            secondary_observations_parser.parse_data_sheet(sheets[i])

        primary_observations_parser = PrimaryObservationsParser(log=self._log,
                                                                config=self._config,
                                                                db_observations=observations_db,
                                                                db_countries=areas_db)
        primary_observations_parser.parse_data_sheet(sheets[len(sheets) - 2])

