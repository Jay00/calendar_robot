import logging
from datetime import datetime

#Local Modules
from classes import Report, Hearing
from settings import SEND_FROM_ADDRESS, PASSWORD

def sendAllEmails(allReports, dateOfCalendar):


    for rep in allReports:
        assert type(rep) is Report, "rep is not class report %r" % rep

        listOfHearings = rep.hearings
        numberOfCases = len(listOfHearings)
        numberOfCasesAsString = str(numberOfCases)
        atty = rep.attorney
        toEmailAddress = atty.email

        if numberOfCases == 0:
            html = generateHTMLforNoCases(dateOfCalendar, rep)
        else:
            html = generateHTMLForEmail(rep)

        logging.info("%s has %s hearings scheduled for today.", atty.name, numberOfCasesAsString)
        # print(html)

        sendSingleEmailForAttorney(dateOfCalendar, toEmailAddress, numberOfCasesAsString, html, rep)


def sendSingleEmailForAttorney(dateOfCalendar, toEmailAddress, numberOfCases, html, rep):
    me = SEND_FROM_ADDRESS
    password = PASSWORD

    to = toEmailAddress

    msg = MIMEMultipart('alternative')
    msg['Subject'] = numberOfCases + " Hearings Scheduled for " + dateOfCalendar.strftime('%A, %B %d')
    msg['From'] = 'Court Calendar Robot'
    msg['To'] = toEmailAddress

    # Create the body of the message (a plain-text and an HTML version).
    text = "You have " + numberOfCases + 'scheduled for .'

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    if not TESTINGMODE:

        try:
            smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtpObj.ehlo()

            smtpObj.login(me, password)

            smtpObj.sendmail(me, to, msg.as_string())

            smtpObj.quit()

            print("Emails sent.  Program Complete.")
        except:
            print('Error!  Email failed to send for ', rep.attorney.name)


def generateHTMLforNoCases(dateOfCalendar, report):
    html = """\
    <html>
      <head></head>
      <body>
        <div style='color: white; font-weight: bold; font-size: x-large; border: 2px solid #6d6b6b; background-color: #00cc00; margin: 0px 0px 10px 0px'>
           ALL CLEAR 
        </div>
        You have 0 cases scheduled for %s.<br>
        Report for Attorney %s.
      </body>
    </html>
    """ % (dateOfCalendar.strftime('%A, %B %d'), report.attorney.name)

    return html


def generateHTMLForEmail(reportForSingleAttorney):
    listOfCases = reportForSingleAttorney.hearings
    numberOfCases = str(len(listOfCases))
    dateOfCalendar = reportForSingleAttorney.hearings[0].date
    htmlCases = str()

    for hearing in listOfCases:
        assert type(hearing) is Hearing, "case is not a courtcase: %r" % case
        print(hearing)

        singleCaseHTML = ''
        chargesHTML = ''

        caseHTML = ("""
            <span style='color: #2104db; font-weight: bold'>%s</span> at <span style='font-weight: bold'>%s</span><br>
            <span style='font-weight: bold'>%s</span><br>
            <span>%s</span> - Room: <span style='font-weight: bold'>%s</span><br>
            <span>%s</span>
        """ % (
        hearing.client_name, hearing.date.strftime("%I:%M %p"), hearing.hearing_type, hearing.judge, hearing.courtroom,
        hearing.case_number))

        for charge in hearing.charges:
            chargesHTML = (chargesHTML + """
                %s<br>
            """) % (charge)
        chargesHTML = "<div style='margin:0 0 0 20px; font-size: small; color: #e52d2d'>" + chargesHTML + "</div>"

        caseHTML = "<div style='border: 2px solid #6d6b6b; margin: 0px 0px 10px 0px'>" + caseHTML + chargesHTML + "</div>"
        htmlCases = htmlCases + caseHTML

    htmlCases = "<div style='border: none'>" + htmlCases + "</div>"

    html = """\
    <html>
      <head></head>
      <body>
        You have %s cases scheduled for %s.<br>
        %s

      </body>
    </html>
    """ % (numberOfCases, dateOfCalendar.strftime('%A, %B %d'), htmlCases)

    return html
