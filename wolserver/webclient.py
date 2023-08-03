#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 27-07-2023 21:53:19
# 
# file          | webclient.py
# project       | wolserver
# file version  | 1.0
#

from configparser import ConfigParser
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime
import os
from starlette.responses import FileResponse
import platform, traceback
import subprocess

# base directory
# PATHS must end with '/'!
BASEDIR = "/etc/wolserver/"
SERVERSPATH = BASEDIR + "servers.ini"
LOGFILEDIR = "/var/log/wolserver/webclient/"

SERVERIP="127.0.0.1"

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

class config():

    def getServersFomFile():
        hosts = {}
        # create config importer
        serversImpHandler = ConfigParser(comment_prefixes='/', allow_no_value=True)

        try:
            serversImpHandler.read(SERVERSPATH)
            logging.write("Found servers.ini file. Hosts in file: " + str(serversImpHandler.sections()))
            for host in serversImpHandler.sections():
                serverMAC = serversImpHandler[host]["mac"]
                serverAutowakeup = serversImpHandler.getboolean(host, "autowakeup")
                hostIP = serversImpHandler[host]["ip"]
                if serverMAC:
                    hosts[host] = {}
                    hosts[host]["mac"] = serverMAC
                    hosts[host]["autowakeup"] = serverAutowakeup
                    hosts[host]["ip"] = hostIP
        except:
            logging.writeError("Cannot load servers config file!")
            logging.writeExecError(traceback.format_exc())
            return False
        logging.write("Got hosts: " + str(hosts))
        return hosts

# web register points
class server():

    # general WOL info
    @app.get("/", response_class=HTMLResponse)
    async def srv(request: Request):
        logging.write("Got request from: " + str(request.client.host) + " of " + hostInformation.fullHostname + "/")
        # <link rel="icon" type="image/x-icon" href="/favicon.ico">
        resp = '''<html><head><title>WoL Server - ''' + hostInformation.fullHostname + '''</title>
        
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
        <h1>''' + hostInformation.fullHostname + ''' / Wake-on-LAN Server<h1><h3>Registered servers:</h3><p>Please click on the hostname of the server you want to wakeup.</p>'''
        resp += "<hr>"
        hosts = config.getServersFomFile()
        if hosts:
            resp += "<table>"
            resp += "<tr>"
            resp += "<th>Hostname</th>"
            resp += "<th>MAC</th>"
            resp += "<th>IP (if provided)</th>"
            resp += "<th>Autowakeup enabled</th>"
            resp += "</tr>"
            for host in hosts:
                resp += "<tr>"
                resp += "<td><a href='http://" + hostInformation.fullHostname + "/wakeup/" + host + "'> " + host + "</a></td>"
                resp += "<td>" + hosts[host]["mac"] +"</td>"
                ip = "unknown"
                if hosts[host]["ip"]: ip = hosts[host]["ip"]
                resp += "<td>" + str(ip) +"</td>"
                autowakeup = "unknown"
                if hosts[host]["autowakeup"] != "": autowakeup = hosts[host]["autowakeup"]
                resp += "<td>" + str(autowakeup) +"</td>"
                resp += "</tr>"
            resp += "</table>" 
            logging.write("Retrieved table successfully-")
        else:
            resp += "<p>Config file seems to be empty, edit under:  " + SERVERSPATH + "</p>"
            logging.writeError("Config file seems to be empty, edit under: " + SERVERSPATH)

        resp += "<br>"
        resp += "For changing autowakeup or adding additional servers edit '" + SERVERSPATH + "' manually."
        resp += "<hr>"
        resp += "<br>Wolserver v1.0 from: <a href='https://github.com/Zyzonix/attic/tree/main/wolserver'>github.com/Zyzonix/attic/tree/main/wolserver/</a></body></html>"
        return resp

    # wakeup link
    @app.get("/wakeup/{hostname}", response_class=HTMLResponse)
    async def wakeup(hostname, request: Request):
        logging.write("Got request from: " + str(request.client.host) + " of " + hostInformation.fullHostname + "/")
        resp = ""
        hosts = config.getServersFomFile()
        if hosts:
            host = hostname.upper()
            try:
                mac = hosts[host]["mac"]
                resultEncoded = subprocess.run("/usr/bin/wakeonlan " + mac, capture_output=True, shell=True)
                result = resultEncoded.stdout.decode()[:-1]
                resultErr = resultEncoded.stderr.decode()[:-1]
                if "is not a hardware address" in resultErr:
                    logging.writeError("Failed to wakeup " + host)
                    logging.writeError(resultErr)
                    raise
                else:
                    logging.write(result)
                    resp += "Tried waking up " + host + " [" + mac + "]"            
                    resp += "<br>Return to: <a href='https://" + hostInformation.fullHostname + "/'>" + hostInformation.fullHostname + "</a>"
            except:
                resp += "Failed to wake up " + host
                resp += "<br>Return to: <a href='https://" + hostInformation.fullHostname + "/'>" + hostInformation.fullHostname + "</a>"
        else:
            resp += "Was not able to read config file under " + SERVERSPATH
            resp += "<br>Return to: <a href='https://" + hostInformation.fullHostname + "/'>" + hostInformation.fullHostname + "</a>"
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