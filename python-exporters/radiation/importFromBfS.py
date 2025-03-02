#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2025 ZyzonixDevelopments
#
# date created  | 02-03-2025 09:00:00
# 
# file          | importFromBfS.py
# project       | python-exporters
# file version  | 1.1
#

#
# This script is designed to import radiation data from the German Bundesamt für Strahlenschutz and save it to a mySQL server
# It should be run hourly, managed by a crontab
#

#
# Requires on Debian: python3-mysql.connector 
#

import datetime
import traceback
import mysql.connector
import time
import urllib.request, json 

# base directory
# PATHS must end with '/'!
BASEDIR = "/opt/python-exporters/"

# mySQL settings
MYSQLHOST = ""
MYSQLDATABASENAME = ""
MYSQLTABLENAME = "radiation_importFromBfS"
MYSQLUSER = ""
MYSQLPW = ""

locations = {
    "location1" : "",
    "location2" : "",
    "location3" : "",
    "location4" : "",
    "location5" : ""
}

# URL to opendata 
URL = "https://www.imis.bfs.de/ogc/opendata/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=opendata:odlinfo_timeseries_odl_1h&outputFormat=application/json&sortBy=end_measure&maxFeatures=1000&viewparams=kenn:"

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

    # storage for data while requesting other locations
    global dataContainer
    dataContainer = {}

    def requestFromBfS(self, kenn):
        logging.write("Requesting from: " + URL + kenn)
        data = json.load(urllib.request.urlopen(URL + kenn))
        dataContainer[kenn] = {}
        if data:
            for value in data["features"]:
                #print(value)
                time_stamp = value["properties"]["end_measure"]
                measurementValue = value["properties"]["value"]
                dataContainer[kenn][time_stamp] = measurementValue

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


    def requestLastRow(self):
        # open DB connection
        self.mySQLConnection = dataHandler.openMySQLConnection()
        # if connection fails, return
        if self.testMySQLConnection: 

            # get cursor
            self.mySQLCursor = self.mySQLConnection.cursor()

            SQLCommand = "SELECT time_local FROM pythonexporters.radiation_importFromBfS ORDER BY time_local DESC LIMIT 1"

            self.mySQLCursor.execute(SQLCommand)
            lastRow = self.mySQLCursor.fetchall()
            return lastRow
        else: return False

    def storeData(self, time_local, location1, location2, location3, location4, location5):

        # if connection fails, return
        if self.testMySQLConnection: 
            
            if location1 == 0.0: location1value = "NULL"
            else: location1value = "'" + str(location1) + "'"

            if location2 == 0.0: location2value = "NULL"
            else: location2value = "'" + str(location2) + "'"

            if location3 == 0.0: location3value = "NULL"
            else: location3value = "'" + str(location3) + "'"

            if location4 == 0.0: location4value = "NULL"
            else: location4value = "'" + str(location4) + "'"

            if location5 == 0.0: location5value = "NULL"
            else: location5value = "'" + str(location5) + "'"

            SQLCommand = "INSERT INTO `" + MYSQLTABLENAME + "`(`time_local`, `location1`, `location2`, `location3`, `location4`, `location5`)" 
            SQLCommand += "VALUES ('" + str(time_local) + "'," + location1value + ", " + location2value + ", " + location3value + ", " + location4value + ", " + location5value + ")"

            self.mySQLCursor.execute(SQLCommand)
            self.mySQLConnection.commit()

        else:
            logging.writeError("failed connecting to mySQL server, check config - exiting.")

    # select data from container, skip empty locations
    def requestDataFromContainer(self, location, timestamp):
        try: 
            value = dataContainer[locations[location]][timestamp]
        except:
            value = 0.0
        return value


    def controller(self):        
        lastData = dataHandler.requestLastRow(self)

        # case: no data in SQL table
        if not lastData:
            yesterday = datetime.datetime.now() - datetime.timedelta(1)
            lastTimestamp = yesterday.strftime('%Y-%m-%d %H:%M:%S')
            logging.write("SQL Table empty, using yesterday: " + lastTimestamp)
            formattedTimestamp = time.mktime(yesterday.timetuple())
        else:
            lastTimestamp = lastData[0][0]
            logging.write("Last data in SQL Table is: " + str(lastTimestamp))
            formattedTimestamp = time.mktime(lastTimestamp.timetuple())

        # firstly request data
        for location in locations.keys():
            # skip emtpy location
            if locations[location]:
                dataHandler.requestFromBfS(self, locations[location])

        # check if timestamp in database is older than requested
        if dataContainer.keys():
            newData = False

            # open DB connection
            self.mySQLConnection = dataHandler.openMySQLConnection()
            
            # get cursor
            self.mySQLCursor = self.mySQLConnection.cursor()

            lastUnstoredTimestamp = ""
            # keys are locations
            key = next(iter(dataContainer.keys()))
            for timestamp in dataContainer[key].keys():
                selectedTimestamp = time.mktime(datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").timetuple())
                if selectedTimestamp > formattedTimestamp:
                    timestampForSQL = timestamp.replace("T", " ").replace("Z", " ")
                    loction1value = dataHandler.requestDataFromContainer(self, "location1", timestamp)
                    loction2value = dataHandler.requestDataFromContainer(self, "location2", timestamp)
                    loction3value = dataHandler.requestDataFromContainer(self, "location3", timestamp)
                    loction4value = dataHandler.requestDataFromContainer(self, "location4", timestamp)
                    loction5value = dataHandler.requestDataFromContainer(self, "location5", timestamp)
                    logging.write("Found unstored data:" + " " + str(timestampForSQL) + " " + str(loction1value) + " " + str(loction2value) + " " + str(loction3value) + " " + str(loction4value) + " " + str(loction5value))
                    dataHandler.storeData(self, timestampForSQL, loction1value, loction2value, loction3value, loction4value, loction5value)
                    newData = True

            # finally close DB connection
            self.mySQLCursor.close()
            self.mySQLConnection.close()
            if not newData: logging.write("No new data available")


    def __init__(self):        
        logging.write("Started importFromBfS")

        # open mySQL connection only for testing purposes
        self.testMySQLConnection = dataHandler.openMySQLConnection()
        
        # if connection fails, return
        if not self.testMySQLConnection: 
            logging.writeError("(init) failed connecting to mySQL server, check config - exiting.")
            return
        logging.write("Connection to mySQL server possible")

        # close test-connection 
        self.testMySQLConnection.close()

        dataHandler.controller(self)
        

# init server class
if __name__ == "__main__":
    dataHandler()