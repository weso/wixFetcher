__author__ = 'Miguel'

import logging
import ConfigParser
from application.wixFetcher.app.computation.computation_validation import ComputationValidation
from application.wixFetcher.app.computation.computation_parser import ComputationParser


def configure_log():
    _format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wix_computation.log', level=logging.INFO,
                        format=_format)


def run():
        configure_log()
        log = logging.getLogger('wix_computation')
        config = ConfigParser.RawConfigParser()
        config.read("configuration.ini")
        comp_parser = ComputationParser(log, config)
        comp_parser.run()
        # comp_validation = ComputationValidation(log)
        # comp_validation.run()

if __name__ == '__main__':
    run()
    print "Done!"