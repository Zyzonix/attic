#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 26-02-2024 09:10:59
# 
# file          | python-exporters/weatherstation.py
# project       | python-exporters
# file version  | 2.0
#

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import uvicorn
from datetime import datetime
import platform, traceback
import subprocess
from ctypes import c_short
import smbus
import time
import psutil

# base directory
# PATHS must end with '/'!
BASEDIR = "/home/pi/python-exporters/"
LOGFILEDIR = "/var/log/python-exporters/"

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

# sysstats collector
class sysstats():

    # retrieving system statistics
    def getSysStats():
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        cput = cput = float(open('/sys/class/thermal/thermal_zone0/temp').read())/1000
        return cpu, ram, cput

# sensor connection
class ais():

    # access to values: station.air_stats.get<VALUE>()

    DEVICE = 0x76 # Default device I2C address
    # Register Addresses
    REG_DATA = 0xF7
    REG_CONTROL = 0xF4
    REG_CONTROL_HUM = 0xF2

    # Oversample setting - page 27
    OVERSAMPLE_TEMP = 2
    OVERSAMPLE_PRES = 2
    OVERSAMPLE_HUM = 2
    MODE = 1

    def getShort(data, index):
        # return two bytes from data as a signed 16-bit value
        return c_short((data[index+1] << 8) + data[index]).value

    def getUShort(data, index):
        # return two bytes from data as an unsigned 16-bit value
        return (data[index+1] << 8) + data[index]    

    def getChar(data,index):
        # return one byte from data as a signed char
        result = data[index]
        if result > 127:
            result -= 256
        return result  

    def getUChar(data,index):
        # return one byte from data as an unsigned char
        result =  data[index] & 0xFF
        return result

    # NEVER USED
    def readBME280ID(addr=DEVICE):
        # initializing device bus if not available
        bus = smbus.SMBus(1)
        # Chip ID Register Address
        REG_ID     = 0xD0
        (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
        return (chip_id, chip_version)


    # getting current temperature 
    def getTemperature():
        # initializing device bus if not available
        bus = smbus.SMBus(1)
        # Oversample setting
        control = ais.OVERSAMPLE_TEMP<<5 | ais.OVERSAMPLE_PRES<<2 | ais.MODE
        bus.write_byte_data(ais.DEVICE, ais.REG_CONTROL, control)

        # Convert byte data to word values
        cal1 = bus.read_i2c_block_data(ais.DEVICE, 0x88, 24)
        dig_T1 = ais.getUShort(cal1, 0)
        dig_T2 = ais.getShort(cal1, 2)
        dig_T3 = ais.getShort(cal1, 4)
        
        # Wait in ms 
        wait_time = 1.25 + (2.3 * ais.OVERSAMPLE_TEMP)
        # Wait the required time 
        time.sleep(wait_time/1000)  
        
        # Reading data a second time
        data = bus.read_i2c_block_data(ais.DEVICE, ais.REG_DATA, 8)

        # Calculating raw value
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)   
        var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
        var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
        
        # Storing values in temp array (function can be used for raw temp / calculation of pressure)
        t_fine = var1+var2
        temp = float(((t_fine * 5) + 128) >> 8)/100.0
        temp_array = [temp, t_fine]
        return temp_array #[0] = final value in degrees (Celcius) [1] = raw value for pressure / humidity


    # getting current humidity
    def getHumidity():
        # initializing device bus if not available
        bus = smbus.SMBus(1)
        # Oversample setting for humidity register
        bus.write_byte_data(ais.DEVICE, ais.REG_CONTROL_HUM, ais.OVERSAMPLE_HUM)
    
        # Convert byte data to word values
        cal2 = bus.read_i2c_block_data(ais.DEVICE, 0xA1, 1)
        cal3 = bus.read_i2c_block_data(ais.DEVICE, 0xE1, 7)
        
        dig_H1 = ais.getUChar(cal2, 0)
        dig_H2 = ais.getShort(cal3, 0)
        dig_H3 = ais.getUChar(cal3, 2)
        dig_H4 = ais.getChar(cal3, 3)
        dig_H4 = (dig_H4 << 24) >> 20
        dig_H4 = dig_H4 | (ais.getChar(cal3, 4) & 0x0F)
        dig_H5 = ais.getChar(cal3, 5)
        dig_H5 = (dig_H5 << 24) >> 20
        dig_H5 = dig_H5 | (ais.getUChar(cal3, 4) >> 4 & 0x0F)
        dig_H6 = ais.getChar(cal3, 6)

        # Wait in ms 
        wait_time = 1.25 + (2.3 * ais.OVERSAMPLE_HUM) + 0.575
        # Wait the required time 
        time.sleep(wait_time/1000)   

        # Reading data a second time --> getting raw value
        data = bus.read_i2c_block_data(ais.DEVICE, ais.REG_DATA, 8)
        
        # Calculating raw value
        hum_raw = (data[6] << 8) | data[7]

        # Refine humidity
        humidity = float(ais.getTemperature()[1]) - 76800.0
        humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
        humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
        
        # Compensation of wrong calculations
        if humidity > 100:
            humidity = 100
        elif humidity < 0:
            humidity = 0

        return humidity    


    # getting current air pressure
    def getPressure():
        # initializing device bus if not available
        bus = smbus.SMBus(1)
        # Oversample setting
        control = ais.OVERSAMPLE_TEMP<<5 | ais.OVERSAMPLE_PRES<<2 | ais.MODE
        bus.write_byte_data(ais.DEVICE, ais.REG_CONTROL, control)

        # Convert byte data to word values 
        cal1 = bus.read_i2c_block_data(ais.DEVICE, 0x88, 24) 
        dig_P1 = ais.getUShort(cal1, 6)
        dig_P2 = ais.getShort(cal1, 8)
        dig_P3 = ais.getShort(cal1, 10)
        dig_P4 = ais.getShort(cal1, 12)
        dig_P5 = ais.getShort(cal1, 14)
        dig_P6 = ais.getShort(cal1, 16)
        dig_P7 = ais.getShort(cal1, 18)
        dig_P8 = ais.getShort(cal1, 20)
        dig_P9 = ais.getShort(cal1, 22)

        # Wait in ms 
        wait_time = 1.25 + (2.3 * ais.OVERSAMPLE_PRES) + 0.575
        # Wait the required time 
        time.sleep(wait_time/1000)   

        # Reading data a second time --> getting raw value
        data = bus.read_i2c_block_data(ais.DEVICE, ais.REG_DATA, 8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)

        # getting temperature value
        t_fine = ais.getTemperature()[1]

        # Refine pressure and adjust for temperature
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * dig_P6 / 32768.0
        var2 = var2 + var1 * dig_P5 * 2.0
        var2 = var2 / 4.0 + dig_P4 * 65536.0
        var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig_P1
        if var1 == 0:
            pressure=0
        else:
            pressure = 1048576.0 - pres_raw
            pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = dig_P9 * pressure * pressure / 2147483648.0
            var2 = pressure * dig_P8 / 32768.0
            pressure = pressure + (var1 + var2 + dig_P7) / 16.0
        
        pressure = pressure/100.0
        return pressure

# main data import handler
class importData():

    # import from Shelly Smart Plug
    def importFromSensors():
        result = {
            "currentTemperature" : 0,
            "currentHumidity" : 0,
            "currentPressure" : 0,
            "currentCPUUsage" : 0,
            "currentMemUsage" : 0,
            "currentCPUTemp" : 0
        }
        try:
            result["currentTemperature"] = round(float(ais.getTemperature()[0]), 2)
            result["currentHumidity"] = round(float(ais.getHumidity()), 2)
            result["currentPressure"] = round(float(ais.getPressure()), 2)

            sysstatsData = sysstats.getSysStats()
            print(sysstatsData)
            if sysstats:
                result["currentCPUUsage"] = round(float(sysstatsData[0]), 2)
                result["currentMemUsage"] = round(float(sysstatsData[1]), 2)
                result["currentCPUTemp"] = round(float(sysstatsData[2]), 2)
                
        except:
            logging.writeError("Failed to get data from sensors")
            logging.writeExecError(traceback.format_exc())
        return result

# web register points
class server():

    @app.get("/", response_class=PlainTextResponse)
    async def srv(request: Request):
        logging.write("Got request from: " + str(request.client.host) + " of " + hostInformation.fullHostname + "/")
        sensorData = importData.importFromSensors()
        if sensorData:
            answer = "# HELP weatherstation_temperature Current temperature in °C\n" 
            answer += "# TYPE weatherstation_temperature gauge\n" 
            answer += "weatherstation_temperature " + str(sensorData["currentTemperature"]) + "\n"

            answer += "\n"

            answer += "# HELP weatherstation_humidity Current humidity in %\n" 
            answer += "# TYPE weatherstation_humidity gauge\n"
            answer += "weatherstation_humidity " + str(sensorData["currentHumidity"]) + "\n"

            answer += "\n"

            answer += "# HELP weatherstation_pressure Current pressure in kPa \n" 
            answer += "# TYPE weatherstation_pressure gauge\n"
            answer += "weatherstation_pressure " + str(sensorData["currentPressure"]) + "\n"

            answer += "\n"

            answer += "# HELP weatherstation_cpu_usage Current CPU usage of rpi-weatherstation in % \n" 
            answer += "# TYPE weatherstation_cpu_usage gauge\n"
            answer += "weatherstation_cpu_usage " + str(sensorData["currentCPUUsage"]) + "\n"

            answer += "\n"

            answer += "# HELP weatherstation_mem_usage Current Memory usage of rpi-weatherstation in % \n" 
            answer += "# TYPE weatherstation_mem_usage gauge\n"
            answer += "weatherstation_mem_usage " + str(sensorData["currentMemUsage"]) + "\n"

            answer += "\n"

            answer += "# HELP weatherstation_cpu_temp Current CPU Temp of rpi-weatherstation in °C \n" 
            answer += "# TYPE weatherstation_cpu_temp gauge\n"
            answer += "weatherstation_cpu_temp " + str(sensorData["currentCPUTemp"]) + "\n"

            logging.write("Retrieved data successfully")
        else:
            answer = ""
            logging.writeError("Was not able to retrieve data from sensors")

        return answer

    def __init__(self):
        logging.LOGFILE = "weatherstation-exporter_" + str(datetime.now().strftime("%Y-%m-%d")) + ".log"
        # get hostname and dns suffix
        hostInformation.get()
        uvicorn.run(app, port=8080, host=SERVERIP)


# init server class
if __name__ == "__main__":
    server()
