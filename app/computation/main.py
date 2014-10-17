__author__ = 'Miguel'

import logging

from application.wixFetcher.app.computation.computation_module import ComputationModule


def configure_log():
    _format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wix_computation.log', level=logging.INFO,
                        format=_format)


def run():
        configure_log()
        log = logging.getLogger('wix_computation')
        comp_module = ComputationModule(log)
        comp_module.run()

if __name__ == '__main__':
    run()
    print "Fin :)"