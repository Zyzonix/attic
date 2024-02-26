#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 26-02-2024 09:58:18
# 
# file          | watchdog.py
# project       | python-prometheus-exporters
# file version  | 1.0
#

#
# Requires this package: https://packages.debian.org/sid/all/python3-ping3/download
#

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import uvicorn
from datetime import datetime
import platform, traceback
import subprocess
import asyncio, threading
import subprocess
from ping3 import ping

# base directory
# PATHS must end with '/'!
BASEDIR = "/root/python-prometheus-exporters/"
LOGFILEDIR = "/var/log/python-prometheus-exporters/"

# URLS to ping
# TARGET-NAME must be without any special characters or a space, for example the TARGET-NAME for google.com would be googlecom
URLSTOPING = {
    "<TARGET-NAME>" : "<TARGET-IP/DNS-NAME>",
    "<TARGET2-NAME>" : "<TARGET-IP/DNS-NAME>"
}

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

class collectData():

    # check connection to server
    async def testConnection(target):
        try:
            url = URLSTOPING[target]
            responseInS = ping(url)
            responseInMs = round(responseInS*1000, 2)
            server.results[target] = responseInMs
            logging.write("Connecting to " + url + " took " + str(responseInMs) + "ms")
        
        except:
            logging.writeError("Failed to collect connection data for " + target)
            logging.writeExecError(traceback.format_exc())

# web register points
class server():

    results = {}

    @app.get("/", response_class=PlainTextResponse)
    async def srv(request: Request):
        logging.write("Got request from: " + str(request.client.host) + " of " + hostInformation.fullHostname + "/")

        threads = []
        answer = ""

        # try connecting to all targets
        for target in URLSTOPING.keys():
            thread = threading.Thread(target=asyncio.run, args=(collectData.testConnection(target), ))
            thread.start()
            threads.append(thread)

        # wait until all threads are finished
        for thread in threads:
            thread.join()

        if server.results:
            for target in server.results.keys():
                answer += "# HELP watchdog_" + target + " Connection to " + URLSTOPING[target] + " in ms\n"  
                answer += "# TYPE watchdog_" + target + " gauge\n" 
                answer += "watchdog_" + target + " " + str(server.results[target]) + "\n"
                answer += "\n"

            logging.write("Retrieved table successfully")

        else:
            answer = ""
            logging.writeError("Was not able to retrieve data")

        return answer

    def __init__(self):
        logging.LOGFILE = "shelly_" + str(datetime.now().strftime("%Y-%m-%d")) + ".log"
        # get hostname and dns suffix
        hostInformation.get()
        uvicorn.run(app, port=8080, host=SERVERIP)


# init server class
if __name__ == "__main__":
    server()
