import re
from datetime import datetime

from classes import Hearing

class RawTextProcess(object):
    """docstring for RawTextProcess object

    The RawTextProcess takes the raw text from the downloaded PDF and converts it into
    a list of Hearing types objects.

    The hearings in the PDFs are listed in the following heirachal order.
    1. Courtroom
        2. Judge
            3. Case
                4. Hearing
                    - Defendant's Name
                    - Date & Time of Hearing
                    - Type of Hearing
                    - Attorney (if assigned, not all heairngs have an attorney.)
                    - Charges (if charges, not all cases have charges.  (i.e., Arraignmnets))


    self.process_rawtext takes the raw text and intially breaks down the raw text subdividing by Courtroom
    self.courtroom = (Courtroom, string)

    etc.

    """


    def __init__(self, rawtext, calendar_date='', courtrooms=None, judges=None, cases=None, hearings=None, processed_hearing_objects=None, errors=None):
        super(RawTextProcess, self).__init__()
        self.rawtext = rawtext
        self.calendar_date = calendar_date
        self.courtrooms = courtrooms or []  # List of Tuples (Courtroom, string)
        self.judges = judges or []  # List of Tuples (Courtroom, Judge, string)
        self.cases = cases or []  # List of Tuples (Courtroom, Judge, Case, string)
        self.hearings = hearings or []  #  List of Tuples (Courtroom, Judge, Case, Hearing, string)
        self.processed_hearing_objects = processed_hearing_objects or []  # List of Hearing Objects Created
        self.errors = errors or []

    def process_rawtext(self):
        self.courtrooms = self._splitByCourtRoom()
        self.judges = self._splitByJudge()
        self.cases = self._splitByCaseNumber()
        self._processCases()
        self._create_objects_and_process_remaining_strings()

        # self._removeDuplicateCasesBrokenAcrossPage()
        # Run Remove duplicates twice because long strings of charges may cover multiple pages
        # If the charges are spread accross 3 pages, the second loop will catch it.
        # self._removeDuplicateCasesBrokenAcrossPage()

        # for h in self.HEARINGS:
        #     print(h)
        #     print('\n')

        self.calendar_date = self._getPDFCalendarDateFromRawText()

        print("\n\n")
        print("Calendar Date: ", self.calendar_date)
        print("COURTROOMS: ", len(self.courtrooms))
        print("JUDGES: ", len(self.judges))
        print("CASES: ", len(self.cases))
        print("HEARINGS: ", len(self.hearings))


        print("\nERRORS: ", len(self.errors))
        for e in self.errors:
            print("\n")
            print(e)


    def _getPDFCalendarDateFromRawText(self):

        dateRegex = re.compile(r'For\d\d/\d\d/\d\d\d\d')  # Eg.  "For12/15/2016"
        mo = dateRegex.search(self.rawtext)

        if not mo:
            print("The Court Date was not Found in the PDF. \
                The program was terminated.")
            # logging.CRITICAL("The Date of the Calendar Could Not Be Found.")
            raise ValueError("Unable to Find Calendar Date.")

        fileName = mo.group()  # For12/15/2016
        # print(fileName)

        fileName = fileName[3:]  # Gets rid of "For"

        # fileName format is 12/15/2016
        month = fileName[0:2]  # 12
        day = fileName[3:5]  # 15
        year = fileName[6:]  # 2016


        # return the date of the calendar as an object used by another function
        # do it here so we don't open the PDF again later.
        # from datetime import datetime
        dateOfCalendar = datetime.strptime(year + ' ' + month + ' ' + day, '%Y %m %d')

        return dateOfCalendar

    def _splitByCourtRoom(self):
        strings = re.split(r'(?<!JUDGE: )(COURTROOM [A-Z\d-]+)', self.rawtext)
        courtrooms_list = []
        for i in range(1, len(strings), 2):
            c = (strings[i], strings[i + 1])
            # print(c)
            courtrooms_list.append(c)

        return courtrooms_list

    def _splitByJudge(self):
        judge_list = []
        for room in self.courtrooms:
            courtroom = room[0]

            # Split by Judge
            strings = re.split(r'JUDGE: (?P<name>[/,A-Z\d\s-]+)(?=[\d][\d]:[\d][\d])', room[1])
            # print('splitByJudge: ', strings)
            for i in range(1, len(strings), 2):
                judge = strings[i]
                t = (courtroom, judge, strings[i + 1])
                judge_list.append(t)
                # print("T: ", t)

        return judge_list

    def _splitByCaseNumber(self):
        cases_list = []
        for v in self.judges:
            courtroom = v[0]
            judge = v[1]
            # Split by Case
            strings = re.split(r'([1-2][0987][0-9][0-9] [CDFP][A-Z][\w] \d\d\d\d\d\d|20[0-9][0-9] GJRSLD \d\d\d\d\d\d|[1-2][0987][0-9][0-9] [CDFP][A-Z][\w][S][L][D] \d\d\d\d\d\d)',
                               v[2])
            for i in range(1, len(strings), 2):
                t = (courtroom, judge, strings[i], strings[i + 1])
                cases_list.append(t)
                # print('splitByCaseNumber: ', t)
        print("Number of Cases Found: ", str(len(cases_list)))

        return cases_list

    def _processCases(self):
        for c in self.cases:
            self._processSingleCase(c)

    def _processSingleCase(self, v):
        # print("processCaseNumberStrings: ", v)
        # courtroom = v[0]
        # judge = v[1]
        # case_number = v[2]
        # original_string = v[3]
        # print('\n' + original_string)
        string = v[3]
        # print("STRING: ", string)

        # remove the Superiour Court of the District of Columbia text from the end of the string
        # if it is present.  This happends when the string is the last one on the page.  The header
        # from the next page will be attached on the end of this string since strings are split by
        # the case number matches.
        superiorCourtMatchObject = re.search(r'Superior Court of the District of Columbia', string)
        if superiorCourtMatchObject:
            string = string[:superiorCourtMatchObject.start()]

        # Extract Client Name
        name_mo = re.search(r'^[^\d]+', string)

        full_name = name_mo.group().strip()
        print("Name FULL: ", full_name)

        # Remove Name from Remaining String
        string = string[name_mo.end():]


        # Create List of Hearings
        self._splitByHearingDates(string, full_name, v)

    def _splitByHearingDates(self, string, full_name, v):
        '''
        This will run only after the client name has been extracted from the sring.
        Must extract client name first!
        :return: List of Hearings
        '''
        # Split by Date and Time String Occurrence
        list_of_hearings = re.split(r'([01][\d]/[0-3][\d]/[2][0][\d][\d] [0-2][\d]:[0-6][\d] [AP][M])', string)
        # print("Length of List Before: ", len(list_of_hearings))
        # print(list_of_hearings)

        # Remove empty strings from list
        # Strip white space, item.strip()
        list_of_hearings[:] = [item.strip() for item in list_of_hearings if item != '']
        # print("Length of List After: ", len(list_of_hearings))
        # print(list_of_hearings)

        # Make it a list of Tuples
        lis = []
        for i in range(0, len(list_of_hearings), 2):

            courtroom = v[0]
            judge = v[1]
            case_number = v[2]
            original_string = v[3]

            hearing_date = datetime.strptime(list_of_hearings[i], '%m/%d/%Y %I:%M %p')
            remaining_string = list_of_hearings[i + 1]

            h = (courtroom, judge, case_number, full_name, hearing_date, remaining_string)
            lis.append(h)
            self.hearings.append(h)

        # print(lis)

        return lis

    def _create_objects_and_process_remaining_strings(self):

        # h = (courtroom, judge, case_number, full_name, hearing_date, remaining_string)

        for h in self.hearings:
            attorney_name_full, hearing_type, charges_list = self._process_remaining_string(h[5])

            # TO DO
            # Create Hearing class Objects



    def _process_remaining_string(self, string):

        print("\nProcess Remaining String:")
        print(string)
        '''
        SLOTER, RILEY E03/14/2017 10:30 AM      Arraignment - Citation01 Misrepresent Age to Enter ABC Establishment
        The ABC Establishment causes an error since the attorney name is presumed to be the only two capital
        letters next to each other.
        
        PCP also causes errors
        
        Temporary Fix is to change the ABC to A-B-C
        '''
        string = re.sub('ABC', 'abc', string)
        string = re.sub('PCP', 'PcP', string)
        string = re.sub('CPO', 'cpo', string)
        string = re.sub('TPO', 'tpo', string)
        string = re.sub('BB', 'bb', string)
        string = re.sub('DC', 'Dc', string)

        '''
        Search for the start of the attorney name which is all caps
        The start will be the first occurrence of two CAPITAL Letters together
        So, SMITH, JOHN
        
        Exception is O'BRYANT, so ' must be an option.

        OTHER ISSUE:
        Hearing Type: "DC/Traffic Arraignment" causes problem becuase it starts with two capitals

        '''
        attorney_name_full = ''

        # Search the the Attorney Name
        attorney_mo = re.search(r'[A-Z][A-Z\']', string)

        if attorney_mo:
            print(attorney_mo.group())
            # Hearing type is right before the Attorney Name
            hearing_type = string[:attorney_mo.start()].strip()
            print("Hearing Type: ", hearing_type)

            string = string[attorney_mo.start():]
            # print("Hearing Type Found: ", hearing_type, "\nAttorney_MO: ", attorney_mo.group())
            # print("Original String:", original_string)

        elif not attorney_mo:
            '''
            If there is no attorney name found.  Then search for the charges.
            as Charges will be the next item in the string.  Some cases just don't have
            an assigned attorney.
            '''
            charges_mo = re.search(r'[\d][\d] ', string)
            if charges_mo:
                hearing_type = string[:charges_mo.start()].strip()
                # print("Hearing Type Found - Case with No Attorney Name: ", hearing_type)
                # print("Original String:", original_string)

                # Set Attorney Name to Blank
                attorney_name_full = 'No Attorney'
            else:
                '''
                No Charges found.
                No Attorney found.
                If no charges are found this string may be one without either charges or an assigned attorney
                '''
                attorney_name_full = 'No Attorney - 2'

                '''
                09: 45CaseNumberDefendantEventAttorneyCharges
                '''

                mo = re.search(r'[012][\d]:[0-5][\d]Case', string)
                if mo:
                    string = string[:mo.start()]


                hearing_type = string

        else:
            '''
            This should not happen.  There should always be a hearing type.
            '''
            raise TypeError("No hearing type found.")
            # hearing_type = "UNDEFINED HEARING TYPE"
            # print("\n\n\n\n\n\nHearing Type Not Found.")
            # print("Original String: ", original_string)

        # Modify the following before Splitting for Charges
        # This will prevent a split on the 14, or 15
        # Must modify non-standards here since because if the charges
        # breaks accross a page, it may cause issues.              
        string = re.sub('2015', '(2015)', string)
        string = re.sub('2014', '(2014)', string)
        

        charges_mo = re.search(r'[\d][\d] ', string)
        if charges_mo:
            charges = string[charges_mo.start():].strip()
            # print("Charges: " + charges)
            if attorney_name_full == 'No Attorney':
                pass
                # print("Attorney: " + attorney_name_full)
            else:
                attorney_name_full = string[:charges_mo.start()].strip()
                # print("Attorney: " + attorney_name_full)
        else:
            # No charges found.
            # raise TypeError("The Attorney Name Should Not Be Undefined." + "Original String:\n" + original_string)
            attorney_name_full = "UNDEFINED ATTORNEY NAME"
            charges = '00 No Charges Found'
            # print("No Charges Found.")
            # print("skipping loop because error occurred processing string: \n", original_string)
            # ERRORS.append(courtroom)
            # ERRORS.append(case_number)
            # self.ERRORS.append(hearing_type)
            self.errors.append("No Charges Found in : " + "\"" + string + "\"")
            # ERRORS.append(original_string)
            # continue

        # Correct any non-standard charges string problems
        # charges = re.sub('2015', '(2015)', charges)
        # charges = re.sub('2014', '(2014)', charges)  # TO DO
        charges = re.sub('\$1000 or More', '($1000-or More)', charges)
        charges = re.sub('Age 18', 'Age (18)', charges)
        charges = re.sub('(30 or Over)', '(30-or-Over)', charges)
        charges = re.sub('(20-0564 )', '(20-0564)', charges)
        charges = re.sub('Age 12', 'Age (12)', charges)

        cmo = re.split(r'([\d][\d] )', charges)
        # print(cmo)
        charges_list = []
        for i in range(1, len(cmo), 2):
            c = cmo[i] + cmo[i + 1]

            c = re.sub(r'[0-2][\d]:[0-6][\d]Case NumberDefendantEventAttorneyCharges', '', c)
            # print('cccccccccccccc: ', c)
            charges_list.append(c)
            # print("Charge String: " + c)

        if hearing_type == '':
            raise TypeError(f"Hearing Type Should Not Be Blank.  {string}")


        return attorney_name_full, hearing_type, charges_list




    def _removeDuplicateCasesBrokenAcrossPage(self):
        all_hearings = self.hearings
        '''
        This function is necessary since some cases are split across one
        page to the next.  This function will test to see if the case number
        is the same as the next case number, which should only happen when a
        case is split accross pages.  If the case number is the same, the
        function will grab the charges from the second entry and add them to
        the first entry, and then delete the second repeated entry.
        '''
        print("HEARINGS started with: ", len(all_hearings))
        for i, c in enumerate(all_hearings):
            try:
                nextHearing = all_hearings[i + 1]
            except:
                print("There was no next hearing found.  So there is nothing to compare this case to.  This should happen.")
                print("TOTAL HEARINGS #: ", len(all_hearings))
                self.hearings = all_hearings
                return all_hearings

            if c.case_number == nextHearing.case_number:
                # print("Hearing Case Number is Equal to Next.", c.case_number, c.client_name)


                # Search instead of simple comparison because sometime in the first instance
                # the entire Hearing Type gets cut off at the end of the page.  By searching to see
                # if the first pages description is entirely in the next pages description then it should
                # be the same.
                mo = re.search(c.hearing_type, nextHearing.hearing_type)
                if mo:
                    # print("\n\nHearing Type is Equal to Next.", c.client_name)
                    # print(c.hearing_type, nextHearing.hearing_type)

                    if nextHearing.charges[0] == '00 No Charges Found':
                        # print("NOT Transferring charges becuase it was just a remainder.")
                        all_hearings.remove(nextHearing)
                    else:
                        # print("Transferring Charges for ", nextHearing.client_name, nextHearing.charges)
                        extraCharges = nextHearing.charges
                        c.charges.extend(extraCharges)
                        all_hearings.remove(nextHearing)

                else:
                    # DO NOTHING
                    # print("Hearing Type is NOT Equal to Next.")
                    # print(c.hearing_type, " NOT SAME AS ", nextHearing.hearing_type)
                    pass

        print("HEARINGS ended with: ", len(all_hearings))
        self.hearings = all_hearings
        return all_hearings
