__author__ = 'Dani'


import xlrd

class ParserEssay(object):

    def run(self):

        print "---------------- Detecting imputed sheets "
        a_path = "mybook.xlsx"
        book = xlrd.open_workbook(a_path)
        a_list_of_sheets = book.sheets()
        counter = 0
        imputed_sheets = []
        for a_sheet in a_list_of_sheets:
            if "-Imputed" in a_sheet.name:
                print a_sheet.name
                counter += 1
                imputed_sheets.append(a_sheet)
        print counter

        print "------------------ Playing with imputed sheets"
        for a_sheet in imputed_sheets:
            print "AVAILABLE DATES FOR", a_sheet.name, ":"
            titles = a_sheet.row(0)
            # print titles[0].value
            i = 1
            while i < a_sheet.ncols and self._not_empty_cell(titles[i]):
                print titles[i].value
                i += 1



        print "--------------------- A list of countries"
        # We will use only a single sheet for this example. everyone is supossed to be equal
        a_sheet_with_countries = imputed_sheets[0]
        list_of_country_names = []
        for i in range(1, a_sheet_with_countries.nrows):
            list_of_country_names.append(a_sheet_with_countries.row(i)[0].value)
        for country_name in list_of_country_names:
            print country_name

        print len(list_of_country_names), "found. 81 expected"



    def _not_empty_cell(self, cell):
        if cell.value in [None, "", " "]:
            return False
        return True

        # book.sheet_by_index(0).




ParserEssay().run()