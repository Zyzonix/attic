#!/usr/bin/env python3
#
# written by Zyzonix
# published by xerberosDevelopments
#
# Copyright (c) 2025 xerberosDevelopments
#
# date created  | 05-09-2025 18:04:50
# 
# file          | mysql/repair-mysql-master-slave-sync.py
# project       | attic
#

# array of master stations to auto-resync
# format: {<MASTER_NAME>: {
#                           MASTER_HOST:<MASTER_HOST_IP>, 
#                           MASTER_USER:<MASTER_SQL_USER>, 
#                           MASTER_PASSWORD=<MASTER_PASSWORD>, 
#                           MASTER_LOG_FILE:<MASTER_LOG_FILE>,
#                           MASTER_BASH_USER:<MASTER_BASH_USER>,
#                           SSH_PORT:<SSH-Port>
#                       }, [...]}
STATIONS = {
    "NAME" : {
        "MASTER_HOST" : "IP",
        "MASTER_USER" : "USER",
        "MASTER_PASSWORD" : "PW",
        "SSH_USER" : "USER",
        "SSH_PORT" : 22
    }
}

MAILSERVER = ""
MAILSERVERPORT = ""
MAILUSER = ""
MAILPASSWORD = ""
EMAILRECEIVER = ""
EMAILDOMAIN = ""

import traceback
import platform
import subprocess
import email.charset
import email.utils
from ping3 import ping
from datetime import datetime

# Encode emails in UTF-8 by default
email.charset.add_charset("utf-8", email.charset.SHORTEST, email.charset.QP, "utf-8")

# hostaname command
HOSTNAMECOMMAND="/bin/hostname --long"

SEND_MAIL=False

# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime

# main log function
class logging():

    LOGGING_ENABLED = False
    MAILCONTENT = []

    def formatOutput(CONTENT):
        logging.MAILCONTENT.append(CONTENT)

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
        logging.formatOutput(message)

    def writeError(msg):
        message = str(ctime.getTime() + " ERROR  | " + msg)
        print(message)
        logging.toFile(message)
        logging.formatOutput(message)

    # log/print error stack trace
    def writeExecError(msg):
        message = str(msg)
        print(message)
        logging.toFile(message)
        logging.formatOutput(message)
    
    def writeSubprocessout(msg):
        for line in msg:
            line = str(line)
            line = line[:-3]
            line = line[3:]
            logging.write("SYS   | " + line)
    
    def writeNix(self):
        logging.toFile(self, "")
        print()
        logging.formatOutput(" ")

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

    # main mail builder
    def buildMail(CONTENT):
        
        mailText = '<font face="Courier New">'
        for line in CONTENT:
            mailText += line + "<br>"

        mailText += "------<br>"
        mailText += '''
                    '''
        mailText += "Source code: https://github.com/Zyzonix/attic/tree/main/mysql </font>"
        return mailText


    def sendMail():

        # only import if enabled and import successful
        import smtplib
        from email.mime.text import MIMEText

        EMAILSENDER = "cron@" + hostinformationHandler.getFullHostname()

        # save email content
        EMAILCONTENT = []
        EMAILCONTENT += logging.MAILCONTENT

        logging.write("Building mail...")

        smtp = smtplib.SMTP(MAILSERVER, MAILSERVERPORT)
        smtp.connect(MAILSERVER, MAILSERVERPORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(MAILUSER, MAILPASSWORD)
            
        subject = "Running results from repair-mysql-master-slave-sync [" + hostinformationHandler.getFullHostname() + "]"

        payload = mailHandler.buildMail(EMAILCONTENT)

        msgRoot = MIMEText(payload, "html")
        msgRoot['Subject'] = subject
        msgRoot['From'] = EMAILSENDER
        msgRoot['To'] = EMAILRECEIVER
        msgRoot.add_header("Message-Id", email.utils.make_msgid("repair-mysql-master-slave-sync", domain=EMAILDOMAIN))
        msgRoot.add_header("Date", email.utils.formatdate())

        try:
            smtp.sendmail(MAILUSER, EMAILRECEIVER, msgRoot.as_string())
            logging.write("Sent mail successfully to " + EMAILRECEIVER)
        except:
            logging.writeError("Failed to send mail to " + EMAILRECEIVER + " | Check your settings!")
            logging.writeExecError(traceback.format_exc())


class autorepairmysql():

    def checkSyncState(MASTER_NAME):
        SQL_COMMAND = """/usr/bin/mariadb -e "SHOW SLAVE '""" + MASTER_NAME + """' STATUS \G;" | grep Slave_IO_Running  """
        outofsync = False
        try:
            resultEncoded = subprocess.run(SQL_COMMAND, capture_output=True, shell=True)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if resultErr: logging.writeError("Failed to run sync state command,  error returned")
            splitResult2 = result.split(":")[1]
            if "No" in splitResult2: 
                outofsync = True
                logging.write("'" + MASTER_NAME + "' is currently not syncing")
        except:
            logging.writeError("Failed to get sync state")
            logging.writeExecError(traceback.print_exc())
            outofsync = False       
        return outofsync


    def checkPing(IP):
        try:
            responseInS = ping(IP, timeout=10)
            responseInMs = round(responseInS*1000, 2)
            logging.write("Connecting to " + IP + " took " + str(responseInMs) + "ms")
        except:
            logging.writeError("Not pingable (" + IP + ")")
            logging.writeExecError(traceback.format_exc())
            return False
        if responseInMs > 150:
            logging.writeError("Ping took too long (>150ms), skipping...")
            return False
        return True

    
    def getMasterLogFilePos(MASTER_HOST, SSH_PORT, SSH_USER):
        SSH_COMMAND = "/usr/bin/ssh -p" + str(SSH_PORT) + " " + SSH_USER + "@" + MASTER_HOST + """ "sudo /usr/bin/mariadb -u root -e 'SHOW MASTER STATUS\G' | grep File" """
        MASTER_LOG_FILE = False
        try:
            resultEncoded = subprocess.run(SSH_COMMAND, capture_output=True, shell=True)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if resultErr: logging.writeError("Failed to run command to get MASTER_LOG_FILE, error returned")
            MASTER_LOG_FILE = result.split(":")[1].split(" ")[1]
            logging.write("Current log is " + MASTER_LOG_FILE)
        except:
            logging.writeError("Failed to get MASTER_LOG_FILE")
            logging.writeExecError(traceback.print_exc())
            MASTER_LOG_FILE = False    
        return MASTER_LOG_FILE
    

    def reinitiateSync(STATION, MASTER_HOST, MASTER_USER, MASTER_PASSWORD, MASTER_LOG_FILE):
        logging.write("Stopping sync for " + STATION)
        STOP_COMMAND="""/usr/bin/mariadb -u root -e "STOP SLAVE '""" + STATION + """';" """
        try:
            resultEncoded = subprocess.run(STOP_COMMAND, capture_output=True, shell=True)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if resultErr: logging.writeError("Failed to run command to stop sync, error returned")
        except:
            logging.writeError("Failed to stop sync")
            logging.writeExecError(traceback.print_exc())
            return False   

        SET_COMMAND="""/usr/bin/mariadb -u root -e "CHANGE MASTER '""" + STATION + "' TO master_host='" + MASTER_HOST + "', master_user='" + MASTER_USER + "', master_password='" + MASTER_PASSWORD + "', master_log_file='" + MASTER_LOG_FILE + """', master_log_pos=0;" """
        try:
            resultEncoded = subprocess.run(SET_COMMAND, capture_output=True, shell=True)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if resultErr: logging.writeError("Failed to run command to set sync state, error returned")
        except:
            logging.writeError("Failed to set sync state")
            logging.writeExecError(traceback.print_exc())
            return False  

        START_COMMAND="""/usr/bin/mariadb -u root -e "START SLAVE '""" + STATION + """';" """
        try:
            resultEncoded = subprocess.run(START_COMMAND, capture_output=True, shell=True)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if resultErr: logging.writeError("Failed to run command to start sync, error returned")
        except:
            logging.writeError("Failed to start sync")
            logging.writeExecError(traceback.print_exc())
            return False  

        return True


    def run(self):
        for STATION in STATIONS.keys():
            logging.write("Selected '" + STATION + "'")
            outofsync = autorepairmysql.checkSyncState(STATION)
            if outofsync: 
                pingable = autorepairmysql.checkPing(STATIONS[STATION]["MASTER_HOST"])
                SEND_MAIL=True
                if pingable: 
                    logging.write("Trying to get master status...")
                    MASTER_LOG_FILE = autorepairmysql.getMasterLogFilePos(STATIONS[STATION]["MASTER_HOST"], STATIONS[STATION]["SSH_PORT"], STATIONS[STATION]["SSH_USER"])
                    if MASTER_LOG_FILE: 
                        logging.write("Reinitiating sync...")
                        result = autorepairmysql.reinitiateSync(STATION, STATIONS[STATION]["MASTER_HOST"], STATIONS[STATION]["MASTER_USER"], STATIONS[STATION]["MASTER_PASSWORD"], MASTER_LOG_FILE)
                        if result: logging.write("Successfully reiinitiated sync between slave and " + STATION)
                
            else: logging.write("Syncing successfully... skipping.")
            
        # finally send a mail
        if SEND_MAIL: 
            if MAILSERVER and MAILPASSWORD and MAILUSER and MAILSERVERPORT and EMAILDOMAIN and EMAILRECEIVER: mailHandler.sendMail()
            else: logging.writeError("Mailing is not configured properly.")

    def __init__(self):
        logging.write("Running MySQL Sync Auto-Repair")
        logging.write("Got " + str(len(STATIONS.keys())) + " station(s) configured.")
        autorepairmysql.run(self)

if __name__ == "__main__":
    autorepairmysql()