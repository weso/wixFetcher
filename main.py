__author__ = 'Miguel'
__date__ = '02/09/2014'

import logging
from es.weso.wix_fetcher.importer import Importer
from es.weso.wix_fetcher.parser import Parser


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wixfetcher.log', level=logging.INFO,
                        format=FORMAT)


def run():
    configure_log()
    log = logging.getLogger('wixfetcher')
    importer = Importer(log)
    parser = Parser(log)
    try:
        data_sheets = importer.get_data_sheets()
    except BaseException as e:
        log.error("While accessing the Excel data file: " + e.message)
        raise RuntimeError
    for sheet in data_sheets:
        try:
            parser.parse_data_sheet(sheet)
        except BaseException as e:
            log.error("While parsing sheet \"" + sheet.name + "\": " + e.message)


if __name__ == '__main__':
    try:
        run()
        print 'Done!'
    except BaseException:
        print 'Execution finalized with errors. Check logs.'