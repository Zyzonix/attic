#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 26-02-2024 06:50:16
# 
# file          | python-exporters/shelly.py
# project       | python-exporters
# file version  | 1.0
#
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import uvicorn
from datetime import datetime
import requests
import platform, traceback
import subprocess

# base directory
# PATHS must end with '/'!
BASEDIR = "/root/python-exporters/"
LOGFILEDIR = "/var/log/python-exporters/"

# link to shelly plug's webinterface must start with http:// and end with /
SHELLYURL = "http://<SHELLYURL-here>/"

# own server ip to bind webserver 
SERVERIP="<IPv4-to-bind-on-here>"

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
class server():

    @app.get("/", response_class=PlainTextResponse)
    async def srv(request: Request):
        logging.write("Got request from: " + str(request.client.host) + " of " + hostInformation.fullHostname + "/")
        shellyData = importData.importFromShelly()
        if shellyData["retrievedData"]:
            answer = "# HELP shelly_power Current real AC power being drawn, in Watts \n" 
            answer += "# TYPE shelly_power gauge\n" 
            answer += "shelly_current_power " + str(shellyData["currentPower"]) + "\n"

            answer += "\n"

            answer += "# HELP shelly_cpu_temp Current CPU Temp of ShellyPlug in °C \n" 
            answer += "# TYPE shelly_cpu_temp gauge\n"
            answer += "shelly_cpu_temp " + str(shellyData["tmptC"]) + "\n"

            answer += "\n"

            answer += "# HELP shelly_ram_total Total RAM of ShellyPlug in KB \n" 
            answer += "# TYPE shelly_ram_total gauge\n"
            answer += "shelly_ram_total " + str(shellyData["ram_total"]) + "\n"

            answer += "\n"

            answer += "# HELP shelly_ram_free Current free RAM of ShellyPlug in KB \n" 
            answer += "# TYPE shelly_ram_free gauge\n"
            answer += "shelly_ram_free " + str(shellyData["ram_free"]) + "\n"

            answer += "\n"

            answer += "# HELP shelly_fs_total Total FS size of ShellyPlug in KB\n" 
            answer += "# TYPE shelly_fs_total gauge\n"
            answer += "shelly_fs_total " + str(shellyData["fs_total"]) + "\n"

            answer += "\n"

            answer += "# HELP shelly_fs_free Current size of free FS of ShellyPlug in in KB \n" 
            answer += "# TYPE shelly_fs_free gauge\n"
            answer += "shelly_fs_free " + str(shellyData["fs_free"]) + "\n"

            answer += "\n"

            answer += "# HELP total Total energy consumed by the attached electrical appliance in Watt-minute \n" 
            answer += "# TYPE total gauge\n"
            answer += "shelly_total_power " + str(shellyData["totalPower"])

            logging.write("Retrieved table successfully")
        else:
            answer = ""
            logging.writeError("Was not able to retrieve data from Shelly plug: '" + SHELLYURL + "status/'")

        return answer

    def __init__(self):
        logging.LOGFILE = "shelly_" + str(datetime.now().strftime("%Y-%m-%d")) + ".log"
        # get hostname and dns suffix
        hostInformation.get()
        uvicorn.run(app, port=8080, host=SERVERIP)


# init server class
if __name__ == "__main__":
    server()
