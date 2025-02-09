#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 26-02-2024 09:58:18
# 
# file          | watchdog2mysql.py
# project       | python-exporters
# file version  | 1.0
#

#
# Requires on Debian: python3-ping3 and python3-mysql.connector
#

from datetime import datetime, timezone
import traceback
import threading
from ping3 import ping
import mysql.connector
import asyncio

# base directory
# PATHS must end with '/'!
BASEDIR = "/root/python-exporters/"

# URLS to ping
# TARGET-NAME must be without any special characters or a space, for example the TARGET-NAME for google.com would be googlecom
URLSTOPING = {
    "target1" : "<TARGET-IP/DNS-NAME>",
    "target2" : "<TARGET-IP/DNS-NAME>",
    "target3" : "<TARGET-IP/DNS-NAME>",
    "target4" : "<TARGET-IP/DNS-NAME>"
}

# interval between rerun (in seconds)
RERUNINTERVAL = 15

# mySQL settings
MYSQLHOST = ""
MYSQLDATABASENAME = ""
MYSQLTABLENAME = ""
MYSQLUSER = ""
MYSQLPW = ""

# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime

class logging():


    def write(msg):
        message = str(ctime.getTime() + " INFO   | " + str(msg))
        print(message)
    def writeError(msg):
        message = str(ctime.getTime() + " ERROR  | " + msg)
        print(message)

    # log/print error stack trace
    def writeExecError(msg):
        message = str(msg)
        print(message)
    
    def writeSubprocessout(msg):
        for line in msg:
            line = str(line)
            line = line[:-3]
            line = line[3:]
            logging.write("SYS   | " + line)
    
    def writeNix(self):
        print()


class collectData():

    # check connection to server
    async def testConnection(target):
        try:
            url = URLSTOPING[target]
            responseInS = ping(url, timeout=10)
            responseInMs = round(responseInS*1000, 2)
            dataHandler.results[target] = responseInMs
            logging.write("Connecting to " + url + " took " + str(responseInMs) + "ms")
        
        except:
            dataHandler.results[target] = 0
            logging.writeError("Failed to collect connection data for " + target)
            logging.writeExecError(traceback.format_exc())

class dataHandler():

    results = {}

    # create db connection
    def openMySQLConnection():
        
        try:
            # try creating a connection
            serverConnection = mysql.connector.connect(
                host = MYSQLHOST,
                user = MYSQLUSER,
                password = MYSQLPW,
                database = MYSQLDATABASENAME
            )

        except:
            logging.writeExecError(traceback.format_exc())
            return False

        if serverConnection.is_connected(): return serverConnection
        else: return False

    def controller(self):
        threading.Timer(RERUNINTERVAL, dataHandler.controller, [self]).start()
        
        logging.write("Requesting new data")
        measurementTimeUTC = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        measurementTimeLocal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        threads = []

        # try connecting to all targets
        for target in URLSTOPING.keys():
            thread = threading.Thread(target=asyncio.run, args=(collectData.testConnection(target), ))
            thread.start()
            threads.append(thread)

        # wait until all threads are finished
        for thread in threads:
            thread.join()

        if dataHandler.results:
            SQLCommand = "INSERT INTO `watchdogdata`(`time_utc`, `time_local`, `target1`, `target2`, `target3`, `target4`)" 
            SQLCommand += "VALUES ('" + str(measurementTimeUTC) + "','" + str(measurementTimeLocal) + "','" + str(dataHandler.results["target1"]) + "','" + str(dataHandler.results["target2"]) + "','" + str(dataHandler.results["target3"]) + "','" + str(dataHandler.results["target4"]) + "')"
            
            self.mySQLCursor.execute(SQLCommand)
            self.mySQLConnection.commit()

            logging.write("Retrieved table successfully")
        else:
            logging.writeError("Was not able to retrieve data")

        
    def __init__(self):        
        logging.write("Started watchdog2mysql")

        # open mySQL connection
        self.mySQLConnection = dataHandler.openMySQLConnection()
        
        # if connection fails, return
        if not self.mySQLConnection: 
            logging.writeError("failed connecting to mySQL server, check config - exiting.")
            return
        
        # get cursor
        self.mySQLCursor = self.mySQLConnection.cursor()
        
        # start runner
        dataHandler.controller(self)
        

# init server class
if __name__ == "__main__":
    dataHandler()

