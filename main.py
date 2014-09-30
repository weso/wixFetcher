__author__ = 'Miguel'
__date__ = '02/09/2014'

import logging

from application.wixFetcher.app.parser import Parser
from application.wixFetcher.app.extractor import Extractor
from application.wixFetcher.app.computation.computation_module import ComputationModule


def configure_log():
    _format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wix_fetcher.log', level=logging.INFO,
                        format=_format)


def run():
        configure_log()
        log = logging.getLogger('wix_fetcher')
        # extractor = Extractor(log)
        # parser = Parser(log)
        # try:
        #     data_sheets = extractor.get_data_sheets()
        # except BaseException as e:
        #     log.error("While accessing the Excel data file: " + e.message + "\n")
        # for sheet in data_sheets:
        #     try:
        #         parser.parse_data_sheet(sheet)
        #     except BaseException as e:
        #         log.error("While parsing sheet \"" + sheet.name + "\": " + e.message + "\n")
        comp_module = ComputationModule(log)
        comp_module.validate_observations()

if __name__ == '__main__':
    run()