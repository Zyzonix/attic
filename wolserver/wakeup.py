#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 27-07-2023 21:52:48
# 
# file          | wakeup.py
# project       | wolserver
# file version  | 1.0
#
from configparser import ConfigParser
import traceback
from datetime import datetime
import os, sys, time
import subprocess
import socket
import platform

# base directory
# PATHS must end with '/'!
BASEDIR = "/etc/wolserver/"
SERVERSPATH = BASEDIR + "servers.ini"
LOGFILEDIR = "/var/log/wolserver/wakeup/"
WAKEUPINTERVAL = 1

# MAILCONFIG
AUTH = True
MAILSERVER = ""
MAILSERVERPORT = 587
MAILUSER = ""
MAILPASSWORD = ""
EMAILRECEIVER = ""
EMAILSENDER = "Wake-on-LAN Server <" + MAILUSER + ">"

# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime

class logging():

    LOGGINGENABLED = True
    LOGFILE = ""

    def toFile(self, msg):
        if logging.LOGGINGENABLED:
            try:
                # log file scheme e.g.: <name>_2023-01-01_12-10.log
                logFile = open(LOGFILEDIR + logging.LOGFILE, "a")
                logFile.write(msg + "\n")
                logFile.close()
            except:
                logging.LOGGINGENABLED = False
                logging.writeError(self, "Failed to open logfile directory, maybe a permission error?")

    def write(self, msg):
        message = str(ctime.getTime() + " INFO   | " + str(msg))
        print(message)
        logging.toFile(self, message)

    def writeError(self, msg):
        message = str(ctime.getTime() + " ERROR  | " + msg)
        print(message)
        logging.toFile(self, message)

    # log/print error stack trace
    def writeExecError(self, msg):
        message = str(msg)
        print(message)
        logging.toFile(self, message)
    
    def writeSubprocessout(self, msg):
        for line in msg:
            line = str(line)
            line = line[:-3]
            line = line[3:]
            logging.write(self, "SYS   | " + line)
    
    def writeNix(self):
        logging.toFile(self, "")
        print()

class hostInformation():
    hostname = "unknown"
    fullHostname = "unknown.localdomain"

    def get(self):
        try: hostInformation.hostname = platform.node()
        except: logging.writeError(self, "Failed to get hostname")

        try:
            # request dns suffix
            resultEncoded = subprocess.run("/usr/bin/hostname -A", capture_output=True, shell=True)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if resultErr:
                logging.writeError(self, "Failed to get DNS suffix (command exited with error)")
            else:
                # in case of 'hostname hostname' --> only one time hostname
                if str(platform.node() + " ") in result:
                    logging.write(self, "Correcting retrieved hostname from " + result + " to " + platform.node())
                    hostInformation.fullHostname = platform.node()
                else: hostInformation.fullHostname = result
                logging.write(self, "Got full hostname successfully: " + hostInformation.fullHostname)    
                if hostInformation.fullHostname[len(hostInformation.fullHostname) - 1] == " ":
                    hostInformation.fullHostname = hostInformation.fullHostname[:-1]           
        except:
            logging.writeError(self, "Failed to get full hostname")
            logging.writeExecError(self, traceback.format_exc())

class wakeup():
    
    # counter indicates run, runner() will stop if COUNTER is 0
    COUNTER = 5

    def buildMail(self, hosts, awakeList, failedList, statusUnknownList):
        mailText = ""
        mailText += "Wakeup protocol:\n"
        mailText += "Current time: " + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "\n\n"
        if logging.LOGFILE: mailText += "Log file: " + LOGFILEDIR + logging.LOGFILE + "\n"
        mailText += "Running on " + hostInformation.fullHostname + ", IP: " + socket.gethostbyname(platform.node()) + "\n\n"
        if awakeList:
            mailText += "Successfully woke up the follwing hosts:\n"
            for host in awakeList:
                mailText += "- " + host + " (" + str(hosts[host]["ip"]) + ") [" + hosts[host]["mac"] + "]\n"
            mailText += "\n"
        if failedList:
            mailText += "Hosts failed to wakeup:\n"
            for host in failedList:
                hostIP = hosts[host]["ip"]
                if not hostIP: hostIP = "unknown"
                mailText += "- " + host + " (" + str(hostIP) + ") [" + hosts[host]["mac"] + "]\n"
            mailText += "\n"
        if statusUnknownList:
            mailText += "Hosts with unknown status: (No/wrong IP provided or IP not pingable)\n"
            for host in statusUnknownList:
                hostIP = hosts[host]["ip"]
                if not hostIP: hostIP = "unknown"
                mailText += "- " + host + " (" + str(hostIP) + ") [" + hosts[host]["mac"] + "]\n"
        
        autowakeupFalseHosts = []
        for host in hosts:
            if not hosts[host]["autowakeup"]:
                autowakeupFalseHosts.append(host)
        if autowakeupFalseHosts:
            mailText += "\nThe following hosts are configured but autowakeup is false:\n"
            for host in autowakeupFalseHosts:
                mailText += "- " + host + "\n"
        mailText += "\n"
        mailText += "All configured hosts can also be waked up manually in the webinterface of: http://" + hostInformation.fullHostname + "/"
        return mailText

    def sendMail(self, hosts, awakeList, failedList, statusUnknownList):
        if AUTH and EMAILRECEIVER and EMAILSENDER and MAILUSER and MAILSERVER and MAILPASSWORD and MAILSERVERPORT and (awakeList or failedList or statusUnknownList):
            # only import if enabled
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.header import Header

            if AUTH:
                smtp = smtplib.SMTP(MAILSERVER)
                smtp.connect(MAILSERVER, MAILSERVERPORT)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(MAILUSER, MAILPASSWORD)
                
            else:
                smtp = smtplib.SMTP()
                smtp.connect(MAILSERVER, MAILSERVERPORT)
            
            subject = "Wake on LAN Server - Wakeup Results"
            msgRoot = MIMEMultipart("alternative")
            msgRoot['Subject'] = Header(subject, "utf-8")
            msgRoot['From'] = EMAILSENDER
            msgRoot['To'] = EMAILRECEIVER
            mailContent = wakeup.buildMail(self, hosts, awakeList, failedList, statusUnknownList)
            mailText = MIMEText(mailContent, "plain", "utf-8")
            
            msgRoot.attach(mailText)
            try:
                smtp.sendmail(MAILUSER, EMAILRECEIVER, msgRoot.as_string())
                
            except:
                logging.writeError(self, "Failed to send mail to " + EMAILRECEIVER + " | Check your settings!")
                logging.writeExecError(self, traceback.format_exc())
            
        else:
            logging.write(self, "Mailing disabled or not configured properly.")

    # returns true if provided mac is mac
    def wakeupHost(self, host, mac): 
        try:
            logging.write(self, "Trying to wake up " + host + "[" + mac + "]")
            resultEncoded = subprocess.run("/usr/bin/wakeonlan " + mac, capture_output=True, shell=True)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if "is not a hardware address" in resultErr:
                logging.writeError(self, "Failed to wakeup " + host)
                logging.writeError(self, resultErr)
                return False
            else:
                logging.write(self, result)
                return True
        except:
            logging.writeError(self, "Failed to wakeup " + host + "[" + mac + "]")
            logging.writeExecError(self, traceback.format_exc())
            return False

    # returns true if is pingable
    def pingHost(self, host, ip):
        try:
            resultEncoded = subprocess.run("/usr/bin/ping -c2 " + ip, capture_output=True, shell=True)
            returnCode = resultEncoded.returncode
            if returnCode == 0: 
                logging.write(self, "Can ping " + host + " (" + str(ip) + ")")
                return True
            else: return False

        except:
            logging.writeError(self, "Failed to wakeup " + host + "[" + ip + "]")
            logging.writeExecError(self, traceback.format_exc())
            return False

    def getServersFomFile(self):
        hosts = {}
        # create config importer
        self.serversImpHandler = ConfigParser(comment_prefixes='/', allow_no_value=True)

        try:
            self.serversImpHandler.read(SERVERSPATH)
            for host in self.serversImpHandler.sections():
                serverMAC = self.serversImpHandler[host]["mac"]
                serverAutowakeup = self.serversImpHandler.getboolean(host, "autowakeup")
                hostIP = self.serversImpHandler[host]["ip"]
                if serverMAC and serverAutowakeup:
                    hosts[host] = {}
                    hosts[host]["mac"] = serverMAC
                    hosts[host]["autowakeup"] = serverAutowakeup
                    hosts[host]["ip"] = hostIP
        except:
            logging.writeError(self, "Cannot load servers config file!")
            logging.writeExecError(self, traceback.format_exc())
            return False
        
        return hosts

    # main instance
    def runner(self, hosts):
        
        # list of entries in servers.ini with errors waking up (e.g. typo mistakes)
        failedList = []
        # list of servers that are aleady pingable
        awakeList = []

        # entries will be removed if host is awake or failed to wakeup
        statusUnknownList = list(hosts.keys())

        while wakeup.COUNTER > 0:
            logging.write(self, "Wakeup intervals left: " + str(wakeup.COUNTER - 1))
            for host in hosts:
                autowakeupHost = hosts[host]["autowakeup"]
                if host not in failedList: notInFailedList = True
                else: notInFailedList = False
                if host not in awakeList: notInAwakeList = True
                else: notInAwakeList = False
                if autowakeupHost and notInAwakeList and notInFailedList:
                    wakeupResult = wakeup.wakeupHost(self, host, hosts[host]["mac"])
                    if not wakeupResult:
                        failedList.append(host)
                        statusUnknownList.remove(host)
                    if wakeupResult and hosts[host]["ip"]:
                        pingResult = wakeup.pingHost(self, host, hosts[host]["ip"])
                        if pingResult:
                            awakeList.append(host)
                            statusUnknownList.remove(host)

            if wakeup.COUNTER == 1: break
            # stop if all hosts are awake
            if awakeList == hosts.keys(): wakeup.COUNTER = 0
            logging.write(self, "Going to sleep for " + str(WAKEUPINTERVAL) + "s")
            time.sleep(WAKEUPINTERVAL)
            wakeup.COUNTER -= 1
            logging.writeNix(self)
        
        wakeup.sendMail(self, hosts, awakeList, failedList, statusUnknownList)
    
    def __init__(self):

        # disable logging to file if directory is not present
        if not os.path.isdir(LOGFILEDIR): logging.LOGGINGENABLED = False
        # setting logfile name
        logging.LOGFILE = "wakeup_" + str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + ".log"
        print()
        # get host information
        hostInformation.get(self)
        logging.write(self, "Starting wolserver wakeup")
        logging.write(self, "Running on " + hostInformation.fullHostname)
        if logging.LOGGINGENABLED: logging.write(self, "Logging to file under: " + LOGFILEDIR)
        else: logging.writeError(self, "Directory for logs not found (" + LOGFILEDIR + ")")

        # retrieve registered servers
        hosts = wakeup.getServersFomFile(self)
        if not hosts: return

        if len(sys.argv) == 3:
            # get second argument
            if sys.argv[2] == "all":
                logging.write(self, "Trying to wakeup all servers")
                for host in hosts.keys():
                    wakeup.wakeupHost(self, host, hosts[host]["mac"])

            elif sys.argv[2] == "list":
                logging.write(self, "Those servers are currently registered:")
                for host in hosts.keys():
                    logging.write(self, "HOST: " + host + " [" + hosts[host]["mac"] + "]")

            else:
                if not sys.argv[2].upper() in hosts.keys(): 
                    logging.writeError(self, "Server is not registered in config file (servers.ini)")
                else:
                    host = hosts[sys.argv[2].upper()]
                    wakeup.wakeupHost(self, sys.argv[2].upper(), host["mac"])
        else:
            logging.write(self, "Starting controlled wakeup")
            if hosts: self.runner(hosts)
            else: logging.write(self, "No hosts configured.")

if __name__ == "__main__":
    wakeup() 