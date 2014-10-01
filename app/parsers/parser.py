__author__ = 'Dani'

from ..extractor import Extractor
from .secondaryindicatorsparser import SecondaryIndicatorsParser
from .primaryindicatorsparser import PrimaryIndicatorsAndGroupsParser
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.component_repository import ComponentRepository
from infrastructure.mongo_repos.subindex_repository import SubindexRepository
from infrastructure.mongo_repos.index_repository import IndexRepository


class Parser(object):

    _SECONDARY_INDICATOR_METADATA_SHEET = 1
    _PRIMARY_INDICATOR_METADATA_SHEET = 0


    def __init__(self, log):
        self._log = log

    def run(self, book):
        #Extracting sheets
        extractor = Extractor(self._log, book)
        sheets = extractor.get_data_sheets()
        indicators_db = IndicatorRepository('127.0.0.1')  # TODO: to a config file
        components_db = ComponentRepository('127.0.0.1')
        subindexes_db = SubindexRepository('127.0.0.1')
        indexes_db = IndexRepository('127.0.0.1')


        #Parsign indicatros
        secondary_indicators_parser = SecondaryIndicatorsParser(self._log, indicators_db)
        secondary_indicators_parser.parse_indicators_sheet(sheets[self._SECONDARY_INDICATOR_METADATA_SHEET])

        primary_indicators_parser = PrimaryIndicatorsAndGroupsParser(log=self._log,
                                                                     db_indicator=indicators_db,
                                                                     db_component=components_db,
                                                                     db_subindex=subindexes_db,
                                                                     db_index=indexes_db)
        primary_indicators_parser.parse_indicators_sheet(sheets[self._PRIMARY_INDICATOR_METADATA_SHEET])

        # observation



        #Parsing observations

        # parser = ObservationsParser(log)
        # try:
        #     data_sheets = extractor.get_data_sheets()
        #     for sheet in data_sheets:
        #         try:
        #             parser.parse_data_sheet(sheet)
        #         except BaseException as e:
        #             log.error("While parsing sheet \"" + sheet.name + "\": " + e.message + "\n")
        # except BaseException as e:
        #     log.error("While accessing the Excel data file: " + e.message + "\n")

