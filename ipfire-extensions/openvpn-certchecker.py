#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2025 ZyzonixDevelopments
#
# date created  | 19-03-2025 10:00:00
# 
# file          | ipfire-extensions/openvpn-certchecker.py
# project       | attic
# file version  | 1.1
#
import email.charset
import email.utils
import traceback
import platform
import subprocess
import traceback
import os
import sqlite3
from datetime import datetime

# Encode emails in UTF-8 by default
email.charset.add_charset("utf-8", email.charset.SHORTEST, email.charset.QP, "utf-8")

# days since last used
LASTUSED=90

# email receiver
EMAILRECEIVER="<receiver-email-address>"

# static variables
VERSION=1.0

# path to database file (must end with /)
PATH="/var/ipfire/ovpn/"

# path to certs
CERTPATH=PATH + "certs/"

# openssl path
OPENSSLPATH="/usr/bin/openssl"
# complete command for openssl
OPENSSLCOMMAND=OPENSSLPATH + " pkcs12 -nodes -legacy -passin pass:"" -in "
OPENSSLCOMMANDPT2=OPENSSLPATH + " x509 -noout -subject"

# command to get cert creation date
OPENSSLCREATECOMMAND = OPENSSLPATH + " x509 -startdate -noout -in "

# date path
DATEPATH="/bin/date"
# complete command for transforming command to get date
DATECOMMAND=DATEPATH + " --utc +'%Y-%m-%d %H:%M:%S' --date='"

# hostaname command
HOSTNAMECOMMAND="/bin/hostname"

# MAIL CONFIG PATH
MAILCONFIGPATH="/var/ipfire/dma/"
MAILCONFIGCONFFILE=MAILCONFIGPATH + "mail.conf"
MAILCOFIGAUTHFILE=MAILCONFIGPATH + "auth.conf"
MAILCOFIGDMAFILE=MAILCONFIGPATH + "dma.conf"


# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime

# main log function
class logging():
    
    # import custom scripts
    # log file handling will be managed with systemd
    LOGGING_ENABLED = False

    def toFile(msg):
        if logging.LOGGING_ENABLED:
            try:
                logFile = open(logging.LOGFILEDIR + logging.LOGFILENAME, "a")
                logFile.write(msg + "\n")
                logFile.close()
            except:
                logging.LOGGING_ENABLED = False
                logging.writeError("Failed to open logfile directory, maybe a permission error?")

    def write(msg):
        message = str(ctime.getTime() + " INFO   | " + str(msg))
        print(message)
        logging.toFile(message)

    def writeError(msg):
        message = str(ctime.getTime() + " ERROR  | " + msg)
        print(message)
        logging.toFile(message)

    # log/print error stack trace
    def writeExecError(msg):
        message = str(msg)
        print(message)
        logging.toFile(message)
    
    def writeSubprocessout(msg):
        for line in msg:
            line = str(line)
            line = line[:-3]
            line = line[3:]
            logging.write("SYS   | " + line)
    
    def writeNix(self):
        logging.toFile(self, "")
        print()

# class for getting hostname
class hostinformationHandler():
    
    def getFullHostname():
        fullHostname = "unknown"
        try:

            # request dns suffix
            resultEncoded = subprocess.run(HOSTNAMECOMMAND, capture_output=True, shell=True)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if resultErr:
                logging.writeError("Failed to get DNS suffix (command exited with error)")
            else:
                # in case of 'hostname hostname' --> only one time hostname
                if str(platform.node() + " ") in result:
                    logging.write("Correcting retrieved hostname from " + result + " to " + platform.node())
                    fullHostname = platform.node()
                else: fullHostname = result

                if fullHostname[len(fullHostname) - 1] == " ":
                    fullHostname = fullHostname[:-1]
        except:
            logging.writeError("Failed to get full hostname")
            logging.writeExecError(traceback.format_exc())

        return fullHostname

# class for mail handling
class mailHandler():

    USEMAIL = False
    MAILSERVER = ""
    MAILSERVERPORT = ""
    MAILUSER = ""
    MAILPASSWORD = ""
    EMAILRECEIVER = ""
    EMAILSENDER = ""
    EMAILDOMAIN = ""

    # get mail configuration from directories
    def getConfiguration():
        try:
            mailconfFile = open(MAILCONFIGCONFFILE, "r")
            mailauthFile = open(MAILCOFIGAUTHFILE, "r")
            maildmaFile = open(MAILCOFIGDMAFILE, "r")

            for line in mailconfFile.readlines():
                lineSplit = line.split("=")
                # remove \n 
                lineSplit[len(lineSplit) - 1] = lineSplit[len(lineSplit) - 1].replace("\n", "")
                if lineSplit[0] == "USEMAIL": 
                    if lineSplit[1].lower() == "on": mailHandler.USEMAIL = True
                    else: mailHandler.USEMAIL = False
                if lineSplit[0] == "RECIPIENT": mailHandler.EMAILRECEIVER = lineSplit[1]
                if lineSplit[0] == "SENDER": mailHandler.EMAILSENDER = lineSplit[1]

            for line in mailauthFile.readlines():
                lineSplit1 = line.split("|")
                # remove \n 
                lineSplit1[len(lineSplit1) - 1] = lineSplit1[len(lineSplit1) - 1].replace("\n", "")
                if len(lineSplit1) > 1:
                    mailHandler.MAILUSER = lineSplit1[0]
                    lineSplit2 = lineSplit1[1].split(":")
                    if len(lineSplit2) > 1:
                        mailHandler.MAILSERVER = lineSplit2[0]
                        mailHandler.MAILPASSWORD = lineSplit2[1]
            
            for line in maildmaFile.readlines():
                lineSplit = line.split(" ")
                # remove \n 
                lineSplit[len(lineSplit) - 1] = lineSplit[len(lineSplit) - 1].replace("\n", "")
                if lineSplit[0] == "PORT":  mailHandler.MAILSERVERPORT = lineSplit[1]
                if lineSplit[0] == "SMARTHOST": mailHandler.MAILSERVER = lineSplit[1]

            # set mail server domain for signing
            if mailHandler.MAILSERVER:
                domainSplit = mailHandler.MAILSERVER.split(".")
                mailServerTopLevelDomain = domainSplit[len(domainSplit) - 1]
                mailServerSecondLevelDomain = domainSplit[len(domainSplit) - 2]
                mailHandler.EMAILDOMAIN = mailServerSecondLevelDomain + "." + mailServerTopLevelDomain

            mailconfFile.close()
            mailauthFile.close()
            maildmaFile.close()
            logging.write("Got mail configuration successfully")
            return True

        except:
            logging.writeError("Failed to get mail config")
            return False


    # main mail builder
    def buildMail(certsInUse, certsUnused, certsFailed):
        
        mailText = '<font face="Courier New">'
        mailText += '''
        <style>
        p { font-family: Courier New }
        table, th, ts, td { 
            font-family: Courier New;
            border: none; 
            text-align: left; 
            width: 500px
        }
        tr:nth-child(even) {
            background-color: #e0e0eb;
        }
        </style>
        '''
        mailText += hostinformationHandler.getFullHostname() + ''' OpenVPN-Server - Certificate information <br>'''

        if certsUnused:
            mailText += "------"
            mailText += '''<br><b>Certificates that weren't used for ''' + str(LASTUSED) + ''' days):</b><br>'''
            mailText += '''
                        '''
            mailText += "<table><tr><th>Connection name:</th><th>Last used:</th><th>Days since last use:</th><th>Date created:</th></tr>"
            mailText += '''
                        '''
            for cert in certsUnused.keys(): 
                mailText += "<tr><td>" + cert + "</td><td>" + str(certsUnused[cert][0]) + "</td><td>" + str(certsUnused[cert][1]) + "</td><td>" + str(certsUnused[cert][2]) + "</td></tr>"
                mailText += '''
                            '''
            mailText += '''</table><br>'''

        if certsInUse:
            mailText += "------"
            mailText += '''<br><b>Certificates that were used in the last ''' + str(LASTUSED) + ''' days:</b><br>'''
            mailText += '''
                        '''
            mailText += "<table><tr><th>Connection name:</th><th>Last used:</th></tr>"
            for cert in certsInUse.keys(): 
                mailText += "<tr><td>" + cert + "</td><td>" + certsInUse[cert] + "</td></tr>"
                mailText += '''
                            '''
            mailText += '''</table><br>'''

        if certsFailed:
            mailText += "------"
            mailText += '''Failed to check:<br>'''
            mailText += '''
                        '''
            for cert in certsFailed: mailText += "- " + cert 

        mailText += "------<br>"
        mailText += '''
                    '''
        mailText += "openvpn-certchecker Version: " + str(VERSION) + "<br>"
        mailText += "Source code: https://github.com/Zyzonix/attic/tree/main/ipfire-extensions </font>"
        return mailText


    def sendMail(certsInUse, certsUnused, certsFailed):
        
        # first import mail config
        result = mailHandler.getConfiguration()

        # check if different mail receiver is configured
        if EMAILRECEIVER: mailHandler.EMAILRECEIVER = EMAILRECEIVER

        if result and mailHandler.USEMAIL and mailHandler.EMAILRECEIVER and mailHandler.EMAILSENDER and mailHandler.MAILUSER and mailHandler.MAILSERVER and mailHandler.MAILPASSWORD and mailHandler.MAILSERVERPORT and mailHandler.EMAILDOMAIN:
            # only import if enabled and import successful
            import smtplib
            from email.mime.text import MIMEText
            from email.header import Header

            logging.write("Building mail...")

            if mailHandler.MAILUSER and mailHandler.MAILPASSWORD:
                smtp = smtplib.SMTP(mailHandler.MAILSERVER)
                smtp.connect(mailHandler.MAILSERVER, mailHandler.MAILSERVERPORT)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(mailHandler.MAILUSER, mailHandler.MAILPASSWORD)
                
            else:
                smtp = smtplib.SMTP()
                smtp.connect(mailHandler.MAILSERVER, mailHandler.MAILSERVERPORT)
            
            subject = ""
            # get number of certs that are unused
            if certsUnused: subject += str(len(certsUnused.keys())) + " "

            payload = mailHandler.buildMail(certsInUse, certsUnused, certsFailed)

            subject += "VPN-Certificate(s) are unused for " + str(LASTUSED) + " days on [" + hostinformationHandler.getFullHostname() + "]"
            msgRoot = MIMEText(payload, "html")
            msgRoot['Subject'] = subject
            msgRoot['From'] = mailHandler.EMAILSENDER
            msgRoot['To'] = mailHandler.EMAILRECEIVER
            msgRoot.add_header("Message-Id", email.utils.make_msgid("openvpn-certchecker", domain=mailHandler.EMAILDOMAIN))
            msgRoot.add_header("Date", email.utils.formatdate())

            try:
                smtp.sendmail(mailHandler.MAILUSER, mailHandler.EMAILRECEIVER, msgRoot.as_string())
                logging.write("Sent mail successfully to " + mailHandler.EMAILRECEIVER)
            except:
                logging.writeError("Failed to send mail to " + mailHandler.EMAILRECEIVER + " | Check your settings!")
                logging.writeExecError(traceback.format_exc())
            
        else:
            logging.write("Mailing disabled or not configured properly.")

# main class
class openvpncertchecker():

    # get all pem-files in directory
    def getP12s(directory):
        allFilesInDir = os.listdir(directory)
        logging.write("Checking directory: " + directory)
        pemFiles = []
        
        # check filetype
        for file in allFilesInDir:
            if file.endswith(".p12"):
                pemFiles.append(file)

        logging.write("Found " + str(len(pemFiles)) + " certificates")
        return pemFiles

    # get date
    def getCNFromCert(cert):
        completeCommand = OPENSSLCOMMAND + CERTPATH + cert + " | " + OPENSSLCOMMANDPT2
        outputSubjectEncoded = subprocess.run(completeCommand, shell=True, capture_output=True)
        outputSubject = outputSubjectEncoded.stdout.decode()[:-1]
        outputSubjectErr = outputSubjectEncoded.stderr.decode()[:-1]
        if not outputSubjectErr:
            try: 
                subjectSplit = outputSubject.split("CN = ")
                certName = subjectSplit[1]
                return certName
            except: 
                try:
                    subjectSplit = outputSubject.split("CN=")
                    certName = subjectSplit[1]
                    return certName 
                except: return False
        else: return False

    # get cert creation date
    def getCertCreateDate(cert):
        outputDateEncoded = subprocess.run(OPENSSLCREATECOMMAND + cert, shell=True, capture_output=True)
        outputDate = outputDateEncoded.stdout.decode()[:-1]
        outputDateErr = outputDateEncoded.stderr.decode()[:-1]
        if not outputDateErr:
            try: 
                # remove 'notBefore='
                rawOutputDate = outputDate.replace("notBefore=", "")
                
                formattedDateEncoded = subprocess.run(DATECOMMAND + rawOutputDate + "'", shell=True, capture_output=True)
                formattedDate = formattedDateEncoded.stdout.decode()[:-1]

                return formattedDate
            except: return False
        else: return False

    # open DB connection
    # only in read-only mode
    def openDBConnection():
        try:
            sqlCommand = "file:" + PATH + "clients.db" + "?mode=ro"
            sqlConnection = sqlite3.connect(sqlCommand, uri=True)
        except:
            logging.writeError("Failed to connect to dabase...")
            return False
        return sqlConnection

    def main():

        # format: p12-name : certName 
        dataArray = {}

        mailRequired = False

        # array of certs that havn't been used for $LASTUSED days
        certsUnused = {}
        # array of certs that have been used within $LASTUSED days
        certsInUse = {}
        # list of failed certs
        certsFailed = []

        if PATH:
            p12s = openvpncertchecker.getP12s(CERTPATH)
            print(p12s)
            if p12s:
                for p12 in p12s:
                    # skip serverkey cert
                    if not ("server" in p12): 
                        certName = openvpncertchecker.getCNFromCert(p12)
                        if certName:
                            dataArray[p12] = certName
                        else:
                            formattedP12 = p12.replace(".p12", "")
                            certsFailed.append(formattedP12)
                            logging.writeError("Failed to obtain CN from " + str(p12))

                if dataArray:
                    logging.write("Collected all names of available p12...")
                    sqlConnection = openvpncertchecker.openDBConnection()
                    sqlCursor = sqlConnection.cursor()

                    currentDate = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
                    if sqlConnection:
                        for p12 in dataArray.keys():
                            logging.write("Checking " + p12)
                            certName = dataArray[p12]
                            sqlCursor.execute("SELECT * FROM sessions WHERE common_name='" + certName + "' ORDER BY connected_at DESC LIMIT 1")
                            try:
                                lastLine = list(sqlCursor.fetchone())
                            except:
                                # if connection was never used
                                logging.write("Connection " + certName + " was never used.")
                                lastLine = [certName, "unused", "unused"]
                            formattedP12 = p12.replace(".p12", "")
                            certFullpath = CERTPATH + p12.replace(".p12", "cert.pem")
                            # if connection is active
                            if not lastLine[2]: 
                                certsInUse[formattedP12] = str(lastLine[1])
                            # if cert was never used 
                            elif lastLine[1] == "unused":
                                mailRequired = True
                                creationDate = openvpncertchecker.getCertCreateDate(certFullpath)
                                certsUnused[formattedP12] = ["Never used", "Never used", creationDate]
                            else: 
                                # get dates
                                lastUsedDate = datetime.strptime(lastLine[2], "%Y-%m-%d %H:%M:%S") 
                                dayDelta = (currentDate - lastUsedDate).days + 1
                                if dayDelta > LASTUSED:
                                    logging.write("Cert " + certName + "/" + p12 + " wasn't used for longer than " + str(LASTUSED) + " days (" + str(dayDelta) + " days unused)")
                                    mailRequired = True
                                    creationDate = openvpncertchecker.getCertCreateDate(certFullpath)
                                    certsUnused[formattedP12] = [str(lastLine[2]), dayDelta, creationDate]
                                else:
                                    certsInUse[formattedP12] = str(lastLine[1])
                    
                # if any cert will expire soon or is already expired send mal
                if mailRequired:
                    mailHandler.sendMail(certsInUse, certsUnused, certsFailed)
                else:
                    logging.write("All certs where in use within the last " + str(LASTUSED) + "days - no notification required!")
                logging.write("Exiting...")
        else:
            logging.writeError("No path configured, check your config! Exiting...")

    # initialization function
    def __init__(self):
        logging.write("Starting ipfire-extentions/openvpn-certchecker check")
        logging.write("Running on " + hostinformationHandler.getFullHostname())
        openvpncertchecker.main()


if __name__ == "__main__":
    openvpncertchecker() 
