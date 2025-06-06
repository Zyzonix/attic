#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 03-03-2024 09:11:51
# 
# file          | ipfire-extensions/openvpn-expiring-notifier.py
# project       | attic
# file version  | 2.0
#
import email.charset
import email.utils
import traceback
import platform
import subprocess
import traceback
import os
from datetime import datetime

# Encode emails in UTF-8 by default
email.charset.add_charset("utf-8", email.charset.SHORTEST, email.charset.QP, "utf-8")

# remaining days of validity until notification
VALIDITYDAYS=14

# show vaild certs in mail
SHOWVALID=True

# email receiver, if empty the preconfigured from IPFire's mail.conf will be used
# scheme: user@example.com
EMAILRECEIVER=""

# static variables
VERSION=2.0

# path to certs (must end with /)
PATH="/var/ipfire/ovpn/certs/"

# openssl path
OPENSSLPATH="/usr/bin/openssl"
# complete command for openssl
OPENSSLCOMMAND=OPENSSLPATH + " x509 -enddate -noout -in "

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
    def buildMail(certsValid, certsExpiringSoon, certsExpired, certsCheckFailed):
        
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
        mailText += hostinformationHandler.getFullHostname() + " OpenVPN-Server - Certificate information <br>"

        if certsExpiringSoon:
            mailText += "------"
            mailText += "<br><b>Certificates that will expire soon (fewer than " + str(VALIDITYDAYS) + " days):</b><br>"
            mailText += '''
                        '''
            mailText += "<table><tr><th>Certificate Name:</th><th>Expiring Date:</th><th>Days left until expired:</th></tr>"
            mailText += '''
                        '''
            for cert in certsExpiringSoon.keys(): 
                mailText += "<tr><td>" + cert + "</td><td>" + certsExpiringSoon[cert][1] + "</td><td>" + certsExpiringSoon[cert][0] + "</td></tr>"
                mailText += '''
                '''
            mailText += "</table><br>"

        if certsExpired:
            mailText += "------"
            mailText += "<br><b>Certificates that already expired:</b><br>"
            mailText += '''
                        '''
            mailText += "<table><tr><th>Certificate Name:</th><th>Expiring Date:</th></tr>"
            for cert in certsExpired.keys(): 
                mailText += "<tr><td>" + cert + "</td><td>" + certsExpired[cert] + "</td></tr>"
                mailText += '''
                            '''
            mailText += "</table><br>"

        if certsValid and SHOWVALID:
            mailText += "------"
            mailText += "<br>Valid certificates:<br>"
            mailText += '''
                        '''
            mailText += "<table><tr><th>Certificate Name:</th><th>Expiring Date:</th><th>Days left until expired:</th></tr>"
            for cert in certsValid.keys(): 
                mailText += "<tr><td>" + cert + "</td><td>" + certsValid[cert][1] + "</td><td>" + certsValid[cert][0] + "</td></tr>"
                mailText += '''
                            '''
            mailText += "</table><br>"

        if certsCheckFailed:
            mailText += "------"
            mailText += '''Failed to check:<br>'''
            mailText += '''
                        '''
            for cert in certsCheckFailed: mailText += "- " + cert + "<br>"

        mailText += "------<br>"
        mailText += '''
                    '''
        mailText += "openvpn-expiring-notifier version: " + str(VERSION) + "<br>"
        mailText += "Source code: https://github.com/Zyzonix/attic/tree/main/ipfire-extensions </font>"
        return mailText


    def sendMail(certsValid, certsExpiringSoon, certsExpired, certsCheckFailed):
        
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
                smtp = smtplib.SMTP(mailHandler.MAILSERVER, mailHandler.MAILSERVERPORT)
                smtp.connect(mailHandler.MAILSERVER, mailHandler.MAILSERVERPORT)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(mailHandler.MAILUSER, mailHandler.MAILPASSWORD)
                
            else:
                smtp = smtplib.SMTP()
                smtp.connect(mailHandler.MAILSERVER, mailHandler.MAILSERVERPORT)
            
            subject = ""
            # get number of certs that will expire soon
            if certsExpiringSoon: subject += str(len(certsExpiringSoon.keys())) + " "

            payload = mailHandler.buildMail(certsValid, certsExpiringSoon, certsExpired, certsCheckFailed)

            subject += "VPN-Certificate(s) will expire soon on [" + hostinformationHandler.getFullHostname() + "]"
            msgRoot = MIMEText(payload, "html")
            msgRoot['Subject'] = subject
            msgRoot['From'] = mailHandler.EMAILSENDER
            msgRoot['To'] = mailHandler.EMAILRECEIVER
            msgRoot.add_header("Message-Id", email.utils.make_msgid("openvpn-notifier", domain=mailHandler.EMAILDOMAIN))
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
class openvpnnotifier():

    # static lists
    certsValid = {}
    certsExpiringSoon = {}
    certsExpired = {}
    certsCheckFailed = []

    # get all pem-files in directory
    def getPEMs(directory):
        allFilesInDir = os.listdir(directory)
        logging.write("Checking directory: " + directory)
        pemFiles = []
        
        # check filetype
        for file in allFilesInDir:
            if file.endswith(".pem"):
                pemFiles.append(file)

        logging.write("Found " + str(len(pemFiles)) + " certificates")
        return pemFiles

    # get date
    def getDateFromCert(cert):
        outputDateEncoded = subprocess.run(OPENSSLCOMMAND + PATH + cert, shell=True, capture_output=True)
        outputDate = outputDateEncoded.stdout.decode()[:-1]
        outputDateErr = outputDateEncoded.stderr.decode()[:-1]
        if not outputDateErr:
            try: 
                # remove 'notAfter='
                rawOutputDate = outputDate.replace("notAfter=", "")
                
                formattedDateEncoded = subprocess.run(DATECOMMAND + rawOutputDate + "'", shell=True, capture_output=True)
                formattedDate = formattedDateEncoded.stdout.decode()[:-1]

                return formattedDate
            except: return False
        else: return False

    # check validity of selected cert
    def checkValidity(cert):
        
        logging.write("Checking " + cert)
        date = openvpnnotifier.getDateFromCert(cert)

        if date:

            # get dates
            expiringDateOfCert = datetime.strptime(date, "%Y-%m-%d %H:%M:%S") 
            currentDate = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
            remainingDays = (expiringDateOfCert - currentDate).days

            # if cert will expire in fewer than VALIDITYDAYS or is already expired
            if remainingDays < VALIDITYDAYS:
                if remainingDays > 0:
                    logging.write("Cert '" + cert + "' will expire in " + str(remainingDays) + " days (" + str(expiringDateOfCert) + ")")
                    openvpnnotifier.certsExpiringSoon[cert.replace("cert.pem", "")] = [str(remainingDays), str(expiringDateOfCert)]
                else:
                    logging.write("Cert '" + cert + "' is already expired: " + str(expiringDateOfCert))
                    openvpnnotifier.certsExpired[cert.replace("cert.pem", "")] = str(expiringDateOfCert)

            else:
                logging.write("Cert '" + cert + "' is still " + str(remainingDays) + " days valid")
                openvpnnotifier.certsValid[cert.replace("cert.pem", "")] = [str(remainingDays), str(expiringDateOfCert)]

        else: 
            logging.writeError("Was not able to retrieve validity date of " + cert)
            logging.writeError("Command output was: " + str(date))


    def main():
        if PATH:
            certs = openvpnnotifier.getPEMs(PATH)
            print(certs)
            if certs:
                for cert in certs:
                    # skip serverkey cert
                    if not ("server" in cert): openvpnnotifier.checkValidity(cert)
                    
                # if any cert will expire soon or is already expired send mal
                if openvpnnotifier.certsExpiringSoon or openvpnnotifier.certsExpired:
                    mailHandler.sendMail(openvpnnotifier.certsValid, 
                                         openvpnnotifier.certsExpiringSoon, 
                                         openvpnnotifier.certsExpired, 
                                         openvpnnotifier.certsCheckFailed)
                else:
                    logging.write("All certs are longer valid than " + str(VALIDITYDAYS) + "days - no notification required!")
                logging.write("Exiting...")
        else:
            logging.writeError("No path configured, check your config! Exiting...")

    # initialization function
    def __init__(self):
        logging.write("Starting ipfire-extentions/openvpn-notifier check")
        logging.write("Running on " + hostinformationHandler.getFullHostname())
        openvpnnotifier.main()


if __name__ == "__main__":
    openvpnnotifier() 
