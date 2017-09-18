import unittest
import inspect
import os.path
import os
import json
from datetime import date
from datetime import datetime


from text_processor_class import RawTextProcess
from classes import Hearing, Attorney, Report

import main



class TestMain(unittest.TestCase):

    def test_download(self):
        main.downloadPDF()

    def test_get_page_one_raw_text(self):
        raw_text = main.getPageOneRawText()
        self.assertIsInstance(raw_text, str)

    def test_get_calendar_date(self):
        raw_text = "Superior Court of the District of ColumbiaCriminal DivisionCourt Calendar For08/30/2017Printed on : Aug 29, 2017"
        # raw_text = main.getPageOneRawText()
        calendar_date = main.getDownloadedCalendarDate(raw_text)
        self.assertIsInstance(calendar_date, date)

    def test_get_filename(self):
        date_of_calendar = date(2017, 8, 30)
        file_name = main.getFilename(date_of_calendar)
        self.assertEqual(file_name, "2017-08-30_calendar.pdf")

    def test_isNewFile(self):
        # Should be old
        self.assertFalse(main.isNewFile("2017-01-14_calendar.pdf"))
        # Should be new
        self.assertTrue(main.isNewFile("2030-01-12_calendar.pdf"))

    def test_getTotalRawText(self):
        total_raw_text = main.getTotalRawText()
        self.assertIsInstance(total_raw_text, str)

    def test_renameAndMove(self):
        new_path = main.renameFileAndMoveCOPYToCalendars("Testing.pdf")
        self.assertTrue(os.path.isfile(new_path))
        # Cleanup
        os.remove(new_path)


    def test_text_processor(self):
        pdf_file = ".\\calendars\\2017-01-10_calendar.pdf"
        assert (os.path.isfile(pdf_file))
        raw_text = main.getTotalRawText(pdf_file)

        processor = RawTextProcess(raw_text)
        processor.process_rawtext()



# class PrintString(unittest.TestCase):
#     os.chdir(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
#     pdf_file = ".\\calendars\\2017-03-24_calendar.pdf"
#     assert (os.path.isfile(pdf_file))
#     raw_text = main.getRawText(pdf_file)
#     # print(raw_text[:300])

#     def test_raw(self):
#         print("\nRAW:\n")
#         print(self.raw_text[:300])


# class ReportGenerator(unittest.TestCase):
#     os.chdir(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
#     pdf_file = ".\\calendars\\2017-03-01_calendar.pdf"
#     assert (os.path.isfile(pdf_file))
#     raw_text = main.getRawText(pdf_file)

#     processor = RawTextProcess(raw_text)

#     processor.process_rawtext()
    

#     def test_report(self):
#         all_reports = main.getAttorneyCaseReports(self.processor.HEARINGS)
#         print("All Reports: ", str(len(all_reports)))
#         for rep in all_reports:
#             print("# of Hearings: ", str(len(rep.hearings)))
#             for h in rep.hearings:
#                 print(h)


# class EmailGenerator(unittest.TestCase)
#     os.chdir(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
    
    
    

#     def test_email(self):
#         files = [
#             # '03-01',
#             # '03-02',
#             '03-03',
#             '03-04',
#             '03-05',
#             # '03-06',
#             # '03-07',
#             # '03-08',
#             # '03-09',
#             '03-10',
#         ]

#         for file in files:
#             try:
#                 pdf_file = ".\\calendars\\2017-" + file + "_calendar.pdf"
#                 if (os.path.isfile(pdf_file)):
#                     raw_text = main.getRawText(pdf_file)
                    

#                     processor = RawTextProcess(raw_text)
#                     processor.process_rawtext()
#                     calendarDate = processor.calendar_date
#                     all_reports = main.getAttorneyCaseReports(processor.hearings)


#                     main.sendAllEmails(all_reports, calendarDate)
#             except FileExistsError:
#                 print("File Does Not Exist.", file)



# class StringProcessor(unittest.TestCase):

#     def test_some(self):
#         string = "FORRISTAL-GARCIA, GENEVIEVE M01/10/2017 10:00 AM      Arraignment - Citation01 Driving Under the Influence of Alcohol or a Drug02 Operating a Vehicle While ImpairedENDPAGESuperior Court of the District of ColumbiaCriminal DivisionCourt Calendar For01/10/2017Printed on : Jan 10, 2017 10:26 AMCase NumberDefendantEventAttorneyCharges"
#         h = RawTextProcess("TEST")._process_strings(string)
#         self.assertEqual(h.hearing_type, "Arraignment - Citation", h)


# class TextProcessorTests(unittest.TestCase):

#     pdf_file = ".\\calendars\\2017-01-10_calendar.pdf"
#     assert (os.path.isfile(pdf_file))
#     total_raw_text = main.getTotalRawText(pdf_file)

#     processor = RawTextProcess(total_raw_text)
#     processor.process_rawtext()

#     def test_charges_are_in_order(self):
#         """
#         Test to see that all charges start with either 00, or 01
#         Where no charges are found, the charge is listed as 00
#         """
#         allhearing = self.processor.hearings

#         for index, h in enumerate(allhearing):

#         # for h in allhearing:
#             self.assertIn(h.charges[0][0:2], ['01', '00'], str(h) + str(allhearing[index - 1]))

#             if len(h.charges) > 1:
#                 self.assertEqual(h.charges[1][0:2], '02', h)

#             if len(h.charges) > 2:
#                 self.assertEqual(h.charges[2][0:2], '03', h)

#             if len(h.charges) > 3:
#                 self.assertEqual(h.charges[3][0:2], '04', h)

#             if len(h.charges) > 4:
#                 self.assertEqual(h.charges[4][0:2], '05', h)




# class CourtCalendarTest(unittest.TestCase):


#     os.chdir(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
#     pdf_file = ".\\calendars\\2017-03-22_calendar.pdf"
#     assert (os.path.isfile(pdf_file))
#     raw_text = main.getRawText(pdf_file)
#     # def test_get_raw(self):
#     #     os.chdir(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
#     #     pdf_file = ".\\calendars\\2017-02-27_calendar.pdf"
#     #     assert(os.path.isfile(pdf_file))
#     #
#     #     raw_text = main.getRawText(pdf_file)


#     # def test_get_by_Courtroom(self):
#     #     dict = main.splitTotalRawTextByCourtRoom(self.raw_text)
#     #     print(dict)
#     #     for k, v, in dict.items():
#     #         print(k)

#     # def test_split_by_Judge(self):
#     #     dict = main.splitTotalRawTextByCourtRoom(self.raw_text)
#     #     dict = main.splitByJudge(dict)
#     #
#     #     # for k, v, in dict.items():
#     #     #     print(k, v)
#     #     print(json.dumps(dict, indent=4, sort_keys=True))

#     def test_split_by_casenumber(self):
#         dict = main.splitTotalRawTextByCourtRoom(self.raw_text)
#         dict = main.splitByJudge(dict)
#         dict = main.splitByCaseNumber(dict)
#         dict = main.splitByHearingType(dict)

#         # print(dict)
#         # print(json.dumps(dict, indent=4, sort_keys=True))

#     # def test_process_strings(self):
#     #     string = "ALVARINGA, BENJAMIN 02/27/2017 09:30 AM      Non-Jury TrialCONWAY, BYRON01 Simple Assault02 Attempted Threats to Do Bodily Harm -Misd03 Simple Assault04 Attempted Poss Prohibited Weapon -Other Box Cutters"
#     #     result = main.processCaseNumberStrings(string)



#     # def test_split_by_hearing_dates(self):
#     #
#     #     string = "02/27/2017 10:00 AM      Sanction HearingBORECKI, SUSAN E.01 Poss of a Controlled Substance -Misd Cocaine02/27/2017 10:00 AM      Review HearingBORECKI, SUSAN E.01 Poss of a Controlled Substance -Misd Cocaine"
#     #
#     #     result = main.splitByHearingDatesAndReturnListOfHearings(string)
#     #
#     #     self.assertEqual(len(result), 2)





if __name__ == '__main__':
    unittest.main()
