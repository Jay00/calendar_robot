#! python3
import os
import inspect
import requests


# Core Modules
import re
import logging
from datetime import datetime, date
import shutil

# Third Party Modules
import PyPDF2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Custom Modules
from classes import Attorney
from classes import Report
from classes import Hearing
from emails import sendAllEmails
from attorneys import getListOfAttorneys
from text_processor_class import RawTextProcess


TESTINGMODE = False

PROGRAM_DIRECTORY = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
TEMP_FILE = os.path.join(PROGRAM_DIRECTORY, 'temp', 'downloaded_calendar.pdf')
CALENDARS_DIRECTORY = os.path.join(PROGRAM_DIRECTORY, 'calendars')

def main():
    # Ensures the working directory is correct for the Task Scheduler which runs from a different directory
    os.chdir(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

    logging.basicConfig(
        filename='courtcalendarrobot.log',
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S %p'
    )
    logging.info("Robot Started")

    downloadPDF()

    page_one = getPageOneRawText()
    calendar_date = getDownloadedCalendarDate(page_one)

    new_file_name = getFilename(calendar_date)

    if isNewFile(new_file_name):
        print("File is New")
        total_raw_text = getTotalRawText()

        renameFileAndMoveCOPYToCalendars(new_file_name)

        text_processor = RawTextProcess(total_raw_text)
        text_processor.process_rawtext()
        reports = getAttorneyCaseReports(text_processor.hearings)

        sendAllEmails(reports, calendar_date)
        logging.info("Program Exited Successfully.")
    else:
        print("Calendar is Not New.  Program will exit.")
        exit()


def downloadPDF():
    try:
        res = requests.get('https://www.dccourts.gov/livexml/Attorney_Calendar_Internet.pdf')
        res.raise_for_status()
    except Exception as err:
        logging.warning("Failed to download PDF: ", err)
        print("Failed to download PDF: ", err)
        print("Program will exit because the download failed.")
        exit()

    # Save PDF to Temp File
    with open(TEMP_FILE, "wb") as newFile:
        # Chunk the file to hanld large files
        for chunk in res.iter_content(100000):
            newFile.write(chunk)
    newFile.close()

    print("Temp PDF downloaded.")


def getPageOneRawText():
    if not os.path.exists(TEMP_FILE):
        logging.critical("def testTempPDF FAILED:  The file name for var TEMP_FILE does not exist.")
        print("FILE DOES NOT EXIST:  The file name for var TEMP_FILE does not exist.")
        exit()

    with open(TEMP_FILE, 'rb') as pdfFileObj:
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        pageObj = pdfReader.getPage(0)  # Look on the first page for the calendar date
        first_page_rawtext = pageObj.extractText()  # Get the raw text from the PDF

    return first_page_rawtext


def getDownloadedCalendarDate(first_page_rawtext):
    dateRegex = re.compile(r'For(?P<month>\d\d)/(?P<day>\d\d)/(?P<year>\d\d\d\d)')  # Eg.  "For12/15/2016"
    mo = dateRegex.search(first_page_rawtext)

    if not mo:
        print("The Court Date was not Found in the PDF. The program was terminated.")
        logging.critical("The Date of the Calendar Could Not Be Found.")
        raise Exception("Unable to locate the 'For12/15/2016' regex.  Date of calendar could not be determined.")

    month = int(mo.group('month'))  # 12
    day = int(mo.group('day'))  # 15
    year = int(mo.group('year'))  # 2016

    dateOfCalendar = date(year, month, day)
    # print("Date of Calendar Found: ", str(dateOfCalendar))

    return dateOfCalendar


def getFilename(dateOfCalendar):
    fileName = dateOfCalendar.strftime("%Y-%m-%d") + '_calendar.pdf'
    # print("The new file name: ", fileName)

    return fileName


def isNewFile(file_name):

    full_path = os.path.join(CALENDARS_DIRECTORY, file_name)
    print(full_path)
    # Test if we already have this file
    if os.path.exists(full_path):
        # If we do exit the program
        # print("{file_name} has already been downloaded.")
        logging.info("The PDF Calendar is NOT new.  The program will exit.")
        return False
    else:
        # print(f"{file_name} is new.")
        logging.info(f"New PDF Calendar downloaded: {file_name}")
        return True


def getTotalRawText(calendarPDFFileName=TEMP_FILE):
    # pdfFileObj = open(".\\calendars\\2016-12-16_calendar.pdf", 'rb')
    pdfFileObj = open(calendarPDFFileName, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    totalRawText = str()

    for x in range(0, pdfReader.numPages):
        # print("Extracting Text from Page: ", x)
        pageObj = pdfReader.getPage(x)
        raw = pageObj.extractText().encode("ascii", "ignore")
        # print(raw)
        rawText = raw.decode("ascii")
        # print(rawText)
        totalRawText = totalRawText + rawText + "ENDPAGE"

    pdfFileObj.close()

    return totalRawText


def getAttorneyCaseReports(all_hearings):

    listOfAttorneys = getListOfAttorneys()

    all_reports = []
    print(len(all_hearings))

    for attorney in listOfAttorneys:
        print("Checking for Hearings for Attorney " + attorney.name + ".")
        atty_hearings = []
        for h in all_hearings:
            mo = re.search(attorney.name, h.attorney_name)
            if mo:
                print("Hearing found, case number " + h.case_number)
                atty_hearings.append(h)
            else:
                # print("Nothing found for " + attorney.name)
                pass
        newReport = Report(attorney, atty_hearings)
        all_reports.append(newReport)

    return all_reports


def renameFileAndMoveCOPYToCalendars(file_name):
    new_path = os.path.join(CALENDARS_DIRECTORY, file_name)
    # os.rename(TEMP_FILE, new_path)
    shutil.copy(TEMP_FILE, new_path)
    return new_path



if __name__ == '__main__':
    main()