#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 26-02-2024 06:50:16
# 
# file          | python-exporters/shelly1pm2mysql.py
# project       | python-exporters
# file version  | 1.2
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
            "currentPower" : "",
            "totalPower" : "",
            "isValid" : False,
            "tmptC" : "",
            "temperatureStatus" : "",
            "retrievedData" : False
        }
        try:
            shellydataRaw = requests.get(SHELLYURL + "status/")
            shellydataJson = shellydataRaw.json()
            result["currentPower"] = shellydataJson["meters"][0]["power"]
            result["totalPower"] = shellydataJson["meters"][0]["total"]
            result["isValid"] = shellydataJson["meters"][0]["is_valid"]
            result["tmptC"] = shellydataJson["tmp"]["tC"]
            result["temperatureStatus"] = shellydataJson["temperature_status"]
            result["ram_total"] = shellydataJson["ram_total"]
            result["ram_free"] = shellydataJson["ram_free"]
            result["fs_total"] = shellydataJson["fs_size"]
            result["fs_free"] = shellydataJson["fs_free"]
            result["retrievedData"] = True

            # format boolean to 0/1
            if result["isValid"]:
                result["isValid"] = 1
            else:
                result["isValid"] = 0
                
        except:
            logging.writeError("Failed to get Shelly Data from '" + SHELLYURL + "status/'")
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
                SQLCommand = "INSERT INTO `shellydata`(`time_utc`, `time_local`, `shelly_current_power`, `shelly_cpu_temp`, `shelly_ram_total`, `shelly_ram_free`, `shelly_fs_total`, `shelly_fs_free`, `shelly_total_power`)"
                SQLCommand += "VALUES ('" + str(measurementTimeUTC) + "','" + str(measurementTimeLocal) + "','" + str(shellyData["currentPower"]) + "','" + str(shellyData["tmptC"]) + "','" + str(shellyData["ram_total"]) + "','" + str(shellyData["ram_free"]) + "','" + str(shellyData["fs_total"]) + "','" + str(shellyData["fs_free"]) + "','" + str(shellyData["totalPower"]) + "')"
                self.mySQLCursor.execute(SQLCommand)
                self.mySQLConnection.commit()

                logging.write("Retrieved table successfully")
            else:
                logging.writeError("Was not able to retrieve data from Shelly plug: '" + SHELLYURL + "status/'")

            # get end time for sleep interval (running timedelta)
            endTime = time.time()
            timedelta = endTime-startTime
            logging.write("timedelta: " + str(timedelta))
            time.sleep(RERUNINTERVAL - timedelta)
        

    def __init__(self):
        logging.LOGFILE = "shelly1pm2mysql_" + str(datetime.now().strftime("%Y-%m-%d")) + ".log"
        
        logging.write("Started shelly1pm2mysql")

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
