__author__ = 'Miguel'
__date__ = '02/09/2014'

import logging
import xlrd

from application.wixFetcher.app.parsers.parser import Parser


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wixfetcher.log', level=logging.INFO,
                        format=FORMAT)


def run():
    configure_log()
    log = logging.getLogger('wixfetcher')
    print "E"
    parser = Parser(log)
    print "A"
    book = xlrd.open_workbook("data_file.xlsx")
    print "YEYA"
    parser.run(book)
    print "b"
    # extractor = Extractor(log)
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



if __name__ == '__main__':
    # try:
    #     run()
    #     print '\nDone!'
    # except BaseException:
    #     print '\nExecution finalized with errors. Check logs.'
    run()
    print '\nDone!'