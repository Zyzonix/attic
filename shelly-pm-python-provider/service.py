#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 10-07-2023 13:28:13
# 
# file          | shelly-pm-python-provider/service.py
# project       | shelly-pm-python-provider
# file version  | 1.0.0
#
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime
import os
import requests
import traceback
import json

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def retrieveData(url):
    try:  
        data = requests.get(url)
        return data
    except:
        traceback.format_exec()
        return False

def selectData(data):
    finalData = {}
    jsonData = json.loads(data.text)
    finalData["power"] = jsonData["meters"][0]["power"]
    finalData["is_valid"] = jsonData["meters"][0]["is_valid"]
    finalData["total"] = jsonData["meters"][0]["total"]
    return finalData

def dataImportHandler():
    url = "http://<hostname-or-ip-of-shelly-plug>/status"
    webData = retrieveData(url)
    selectedData = {}
    answer = []
    if webData:
        selectedData = selectData(webData)
    else:
        print("Web answer doesn't contain data")
        selectData["power"] = 0
        selectData["is_valid"] = "false"
        selectData["total"] = 0

    answer.append("# HELP power Current real AC power being drawn, in Watts\n")
    answer.append("# TYPE power gauge\n")
    answer.append("power " + str(selectedData["power"]) + "\n")
    answer.append("# HELP is_valid Whether power metering self-checks OK\n")
    answer.append("# TYPE is_valid gauge\n")
    answer.append("is_valid " + str(selectedData["is_valid"]) + "\n")
    answer.append("# HELP total Total energy consumed by the attached electrical appliance in Watt-minute\n")
    answer.append("# TYPE total gauge\n")
    answer.append("total " + str(selectedData["total"]) + "\n")
    return answer


# web register points
class Core():


    # general WOL info
    @app.get("/metrics", response_class=HTMLResponse)
    async def metrics():
        resp = "<html><body><pre>"
        data = dataImportHandler()
        for line in data:
            resp += line
        resp += "</pre></body></html>"
        return resp

    def serverInit():
        print("running server instance")
        uvicorn.run(app, port=80, host='0.0.0.0')

# initialize script
if __name__ == "__main__":
    print("starting data provider")

    Core.serverInit()
