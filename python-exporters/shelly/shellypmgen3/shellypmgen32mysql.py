#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 26-02-2024 06:50:16
# 
# file          | python-exporters/shellypmgen32mysql.py
# project       | python-exporters
# file version  | 1.0
#
from datetime import datetime, timezone
import requests
import traceback
import time
import mysql.connector

# base directory
# PATHS must end with '/'!
BASEDIR = "/root/python-exporters/"
LOGFILEDIR = "/var/log/python-exporters/"

# link to shelly plug's webinterface must start with http:// and end with /
SHELLYURL = "http://<IP-of-SHELLY-plug>/"

# interval between rerun (in seconds)
RERUNINTERVAL = 10

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

    LOGFILE = ""

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
    

class importData():

    # import from Shelly Smart Plug
    def importFromShelly():
        result = {
            "voltage" : "",
            "current" : "",
            "activePower" : "",
            "freq" : "",
            "retrievedData" : False
        }
        try:
            shellydataRaw = requests.get(SHELLYURL + "rpc/PM1.GetStatus?id=0")
            shellydataJson = shellydataRaw.json()
            result["voltage"] = shellydataJson["voltage"]
            result["current"] = shellydataJson["current"]
            result["activePower"] = shellydataJson["apower"]
            result["freq"] = shellydataJson["freq"]

            # if PM is used with power producing components
            # maybe a future version will support power tracking in both directions
            if str(shellydataJson["apower"]).startswith("-"):
                currentPower = str(shellydataJson["apower"])
                formattedActivePower = currentPower[1:]
                result["activePower"] = float(formattedActivePower)

            shellydataRaw2 = requests.get(SHELLYURL + "rpc/Sys.GetStatus?id=0")
            shellydataJson2 = shellydataRaw2.json()
            result["ram_total"] = shellydataJson2["ram_size"]
            result["ram_free"] = shellydataJson2["ram_free"]
            result["fs_total"] = shellydataJson2["fs_size"]
            result["fs_free"] = shellydataJson2["fs_free"]
            result["retrievedData"] = True
                
        except:
            logging.writeError("Failed to get Shelly Data from '" + SHELLYURL + "rpc/PM1.GetStatus?id=0' or '" + SHELLYURL + "rpc/Sys.GetStatus?id=0'")
            logging.writeExecError(traceback.format_exc())
        return result

# web register points
class dataHandler():

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
        while True: 

            # save start time for sleep interval (running timedelta)
            startTime = time.time()

            logging.write("Requesting new data")
            measurementTimeUTC = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            measurementTimeLocal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            shellyData = importData.importFromShelly()
            if shellyData["retrievedData"]:
                SQLCommand = "INSERT INTO `shellydata`(`time_utc`, `time_local`, `shelly_voltage`, `shelly_current`, `shelly_active_power`, `shelly_freq`, `shelly_ram_total`, `shelly_ram_free`, `shelly_fs_total`, `shelly_fs_free`)"
                SQLCommand += "VALUES ('" + str(measurementTimeUTC) + "','" + str(measurementTimeLocal) + "','" + str(shellyData["voltage"]) + "','" + str(shellyData["current"]) + "','" + str(shellyData["activePower"]) + "','" + str(shellyData["freq"]) + "','" + str(shellyData["ram_total"]) + "','" + str(shellyData["ram_free"]) + "','" + str(shellyData["fs_total"]) + "','" + str(shellyData["fs_free"]) + "')"
                self.mySQLCursor.execute(SQLCommand)
                self.mySQLConnection.commit()

                logging.write("Retrieved table successfully")
            else:
                logging.writeError("Was not able to retrieve data from Shelly plug: '" + SHELLYURL)


            # get end time for sleep interval (running timedelta)
            endTime = time.time()
            timedelta = endTime-startTime
            logging.write("timedelta: " + str(timedelta))
            time.sleep(RERUNINTERVAL - timedelta)
        

    def __init__(self):
        logging.LOGFILE = "shellypmgen32mysql_" + str(datetime.now().strftime("%Y-%m-%d")) + ".log"
        
        logging.write("Started shellypmgen32mysql")

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
