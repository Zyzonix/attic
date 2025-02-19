#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2025 ZyzonixDevelopments
#
# date created  | 19-02-2025 16:00:00
# 
# file          | radiation2mysql.py
# project       | python-exporters
# file version  | 1.0
#

#
# sourced from https://github.com/wgroth2/pi-stuff/blob/master/counter.py
#

#
# Requires on Debian: python3-mysql.connector and python3-rpi-lgpio
#

import datetime
import traceback
import mysql.connector
import time
import RPi.GPIO as GPIO
from collections import deque

# base directory
# PATHS must end with '/'!
BASEDIR = "/opt/python-exporters/"

# interval between rerun (in seconds)
RERUNINTERVAL = 60

# calculate from counts per minute to micro Sivert per hour
USVHFACTOR = 1.0/153.8  # sourced from https://wiki.dfrobot.com/SKU_SEN0463_Gravity_Geiger_Counter_Module#target_1

# mySQL settings
MYSQLHOST = ""
MYSQLDATABASENAME = ""
MYSQLTABLENAME = ""
MYSQLUSER = ""
MYSQLPW = ""


# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
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


    def storeData(self, measurementTimeUTC, measurementTimeLocal, cpm, usvh):

        # open DB connection
        self.mySQLConnection = dataHandler.openMySQLConnection()
        # if connection fails, return
        if self.testMySQLConnection: 

            # get cursor
            self.mySQLCursor = self.mySQLConnection.cursor()

            SQLCommand = "INSERT INTO `radiation`(`time_utc`, `time_local`, `cpm`, `usvh`)" 
            SQLCommand += "VALUES ('" + str(measurementTimeUTC) + "','" + str(measurementTimeLocal) + "','" + str(cpm) + "','" + str(usvh) + "')"
            
            self.mySQLCursor.execute(SQLCommand)
            self.mySQLConnection.commit()

            # finally close DB connection
            self.mySQLCursor.close()
            self.mySQLConnection.close()

        else:
            logging.writeError("failed connecting to mySQL server, check config - exiting.")


    def controller(self):        
        firstRun = True

        while True:
            # save start time for sleep interval (running timedelta)
            startTime = time.time()

            cpm = int(len(counts))
            microsieverts = cpm*USVHFACTOR
            counts.clear()
            measurements = [
            {
                'measurement': 'radiation',
                'fields': {
                    'cpm': cpm,
                    'usvh': microsieverts
                    }
            }
            ]

            measurementTimeUTC = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            measurementTimeLocal = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            logging.write(measurements)
            if not firstRun: dataHandler.storeData(self, measurementTimeUTC, measurementTimeLocal, cpm, microsieverts)
            else: logging.write("First run - skipping SQL storing")

            # get end time for sleep interval (running timedelta)
            endTime = time.time()
            timedelta = endTime-startTime
            #logging.write("timedelta: " + str(timedelta))
            firstRun = False
            time.sleep(RERUNINTERVAL - timedelta)   

    # counter by adding timestamp to array
    def counter(channel):
        global counts
        timestamp = datetime.datetime.now()
        counts.append(timestamp)
        return

    # set up sensor connection and event detection
    def setup():

        logging.write("Running setup")
        GPIO.setmode (GPIO.BOARD)
        GPIO.setup(7, GPIO.IN)
        GPIO.add_event_detect(7, GPIO.FALLING, callback=dataHandler.counter)

        logging.write("Done with setup")
        return


    def __init__(self):        
        logging.write("Started radiation2mysql")

        # open mySQL connection only for testing purposes
        self.testMySQLConnection = dataHandler.openMySQLConnection()
        
        # if connection fails, return
        if not self.testMySQLConnection: 
            logging.writeError("(init) failed connecting to mySQL server, check config - exiting.")
            return
        logging.write("Connection to mySQL server possible")

        # close test-connection 
        self.testMySQLConnection.close()
        
        # start sensor setup
        dataHandler.setup()

        # start runner
        while True:
            if datetime.datetime.now().second == 0:
                counts.clear()
                dataHandler.controller(self)
        

# init server class
if __name__ == "__main__":
    counts = deque()
    dataHandler()