#!/usr/bin/python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 23-05-2023 07:09:26
# 
# file          | server.py
# project       | SHMonitoring (SmartHome-Monitoring)
# file version  | 1.0
#
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime
import requests
import platform, traceback
import subprocess

# base directory
# PATHS must end with '/'!
BASEDIR = "/root/SHMonitoring/"
LOGFILEDIR = "/var/log/SHMonitoring/"

# link to shelly plug's webinterface must start with http:// and end with /
SHELLYURL = "http://<shelly-url-here>/"

# costs per kW/h
COSTSPERKHW = 0.4
CURRENCY = "€"

# IPv4 Address to bind the server on
SERVERIP="<IPv4>"

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime

class logging():

    LOGGINGENABLED = True
    LOGFILE = ""

    def toFile(msg):
        if logging.LOGGINGENABLED:
            try:
                # log file scheme e.g.: <name>_2023-01-01_12-10.log
                logFile = open(LOGFILEDIR + logging.LOGFILE, "a")
                logFile.write(msg + "\n")
                logFile.close()
            except:
                logging.LOGGINGENABLED = False
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

class hostInformation():
    hostname = "unknown"
    fullHostname = "unknown.localdomain"

    def get():
        try: hostInformation.hostname = platform.node()
        except: logging.writeError("Failed to get hostname")

        try:
            # request dns suffix
            resultEncoded = subprocess.run("/usr/bin/hostname -A", capture_output=True, shell=True)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if resultErr:
                logging.writeError("Failed to get DNS suffix (command exited with error)")
            else:
                # in case of 'hostname hostname' --> only one time hostname
                if str(platform.node() + " ") in result:
                    logging.write("Correcting retrieved hostname from " + result + " to " + platform.node())
                    hostInformation.fullHostname = platform.node()
                else: hostInformation.fullHostname = result
                logging.write("Got full hostname successfully: " + hostInformation.fullHostname)
                if hostInformation.fullHostname[len(hostInformation.fullHostname) - 1] == " ":
                    hostInformation.fullHostname = hostInformation.fullHostname[:-1]
        except:
            logging.writeError("Failed to get full hostname")
            logging.writeExecError(traceback.format_exc())

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
            result["fs_size"] = shellydataJson["fs_size"]
            result["fs_free"] = shellydataJson["fs_free"]
            result["retrievedData"] = True
        except:
            logging.writeError("Failed to get Shelly Data from '" + SHELLYURL + "status/'")
            logging.writeExecError(traceback.format_exc())
        return result

class calculateData():

    # shelly plug provides data in W/minute
    # --> calculates in kW/hour
    def getTotalPowerInHours(shellyData):
        totalPowerMinutes = int(shellyData["totalPower"])
        totalPowerHours = totalPowerMinutes/60
        totalKiloPowerHours = totalPowerHours/1000
        return totalKiloPowerHours

    # calculate total costs saved/consumed by connected devices
    def getTotalCosts(totalKiloPowerHours):
        totalCosts = int(totalKiloPowerHours)*COSTSPERKHW
        return totalCosts

# web register points
class server():

    @app.get("/", response_class=HTMLResponse)
    async def srv(request: Request):
        logging.write("Got request from: " + str(request.client.host) + " of " + hostInformation.fullHostname + "/")
        # <link rel="icon" type="image/x-icon" href="/favicon.ico">
        resp = '''<html><head><title>Smart Home Monitoring - ''' + hostInformation.fullHostname + '''</title>
        <meta http-equiv="refresh" content="5">
        </head>
        <style>
        table, th, ts { 
            border: none; 
            text-align: left; 
            min-width: 40%;
        }
        tr:nth-child(even) {
            background-color: #e0e0eb;
        }
        </style>
        <body>
        <h1>''' + hostInformation.fullHostname + ''' / SmartHome Network Monitoring Server</h1><h3>'''
        resp += "<hr>"
        shellyData = importData.importFromShelly()
        if shellyData["retrievedData"]:
            # calculate values
            totalKiloPowerHours = calculateData.getTotalPowerInHours(shellyData)
            totalCosts = calculateData.getTotalCosts(totalKiloPowerHours)
            totalKiloPowerHours2digits = "%0.2f" % totalKiloPowerHours
            totalCosts2digits = "%0.2f" % totalCosts

            # build table
            resp += "<table>"
            resp += "<tr>"
            resp += "<td>Current producing power</td>"
            resp += "<td>" + str(shellyData["currentPower"]) + " W</td>"
            resp += "</tr>"
            resp += "<tr>"
            resp += "<td>Total produced power in W/m</td>"
            resp += "<td>" + str(shellyData["totalPower"]) + " W/m</td>"
            resp += "</tr>"
            resp += "<tr>"
            resp += "<td>Total produced power in kW/h</td>"
            resp += "<td>" + str(totalKiloPowerHours2digits) + " kW/h</td>"
            resp += "</tr>"
            resp += "<tr>"
            resp += "<td>Total saved costs in " + CURRENCY + " | (Costs per kW/h: " + str("%0.2f" % COSTSPERKHW) + CURRENCY + ")</td>"
            resp += "<td>" + str(totalCosts2digits) + " " + CURRENCY + "</td>"
            resp += "</tr>"
            resp += "</table>" 

            # build second health data table
            resp += "<h3>Shelly Health Data</h3>"
            resp += "<table>"
            resp += "<tr>"
            resp += "<td>CPU Temperature in °C</td>"
            resp += "<td>" + str(shellyData["tmptC"]) + "</td>"
            resp += "</tr>"
            resp += "<tr>"
            resp += "<td>Temperature Status</td>"
            resp += "<td>" + str(shellyData["temperatureStatus"]) + "</td>"
            resp += "</tr>"
            resp += "<tr>"
            resp += "<td>RAM Free/Total</td>"
            resp += "<td>" + str(shellyData["ram_free"]) + " KB / " + str(shellyData["ram_total"]) + " KB </td>"
            resp += "</tr>"
            resp += "<tr>"
            resp += "<td>Filesystems Free/Total</td>"
            resp += "<td>" + str(shellyData["fs_free"]) + " KB / " + str(shellyData["fs_size"]) + " KB </td>"
            resp += "</tr>"
            resp += "</table>" 
            resp += "<p>Shelly's webinterface is here: <a href=" + SHELLYURL + ">" + SHELLYURL +"</a></p>"
            logging.write("Retrieved table successfully-")
        else:
            resp += "<p>Was not able to retrieve data from Shelly plug: '" + SHELLYURL + "status/'</p>"
            logging.writeError("Was not able to retrieve data from Shelly plug: '" + SHELLYURL + "status/'")

        resp += "<hr>"
        resp += "<br>SHMonitoring v1.0 from: <a href='https://github.com/Zyzonix/attic/tree/main/SHMonitoring'>github.com/Zyzonix/attic/tree/main/SHMonitoring/</a></body></html>"
        return resp

    # we do not want to use this here
    '''
    @app.get('/favicon.ico')
    async def favicon():
        return FileResponse(BASEDIR + "favicon.ico") #full path here to make icon work 
    '''

    def __init__(self):
        logging.LOGFILE = "webclient_" + str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + ".log"
        # get hostname and dns suffix
        hostInformation.get()
        uvicorn.run(app, port=80, host=SERVERIP)


# init server class
if __name__ == "__main__":
    server()
