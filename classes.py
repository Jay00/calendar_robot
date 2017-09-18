from datetime import datetime

class Hearing:

    def __init__(self, date, client_name, hearing_type, attorney_name, charges, courtroom, judge, case_number, original):
        self.date = date
        self.client_name = client_name
        self.hearing_type = hearing_type
        self.attorney_name = attorney_name
        self.charges = charges
        self.courtroom = courtroom
        self.judge = judge
        self.case_number = case_number
        self.original = original

    def __str__(self):
        return 'Courtroom: ' + self.courtroom + \
               '\nJudge: ' + self.judge + \
               '\nCase Number: ' + self.case_number + \
               '\nAttorney: ' + self.attorney_name + \
               '\nDate/Time: ' + self.date.strftime('%Y-%m-%d  %I:%M %p') + \
               '\nClient: ' + self.client_name + \
               '\nHearing_Type: ' + self.hearing_type + \
               '\nCharges: ' + self.charge_string() + \
               '\nOriginal:\n ' + self.original

    def charge_string(self):
        s = ''
        for c in self.charges:
            s += '\n        ' + c
        return s



class Attorney:
    def __init__(self, name, email):
        self.name = name
        self.email = email


class Report:
    def __init__(self, attorney, hearings):
        self.attorney = attorney  # attorney object
        self.hearings = hearings  # list of courtcase objects
