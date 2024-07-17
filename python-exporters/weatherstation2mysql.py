#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 22-05-2024 09:58:18
# 
# file          | weatherstation2mysql.py
# project       | python-exporters
# file version  | 1.0
#

#
# Requires on Debian: python3-mysql.connector
#

from datetime import datetime, timezone
import traceback
import threading
import mysql.connector
import psutil
from ctypes import c_short
import smbus
import time

# base directory
# PATHS must end with '/'!
BASEDIR = "/home/pi/python-exporters/"

# interval between rerun (in seconds)
RERUNINTERVAL = 15

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

    def controller(self):
        threading.Timer(RERUNINTERVAL, dataHandler.controller, [self]).start()
        
        logging.write("Requesting new data")
        measurementTimeUTC = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        measurementTimeLocal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        dataHandler.results["temperature"] = str(ais.getTemperature()[0])
        dataHandler.results["humidity"] = str(ais.getHumidity())
        dataHandler.results["pressure"] = str(ais.getPressure())
        sysStats = sysstats.getSysStats()
        dataHandler.results["cpu_usage"] = str(sysStats[0])
        dataHandler.results["memory_usage"] = str(sysStats[1])
        dataHandler.results["cpu_temperature"] = str(sysStats[2])

        # open DB connection
        self.mySQLConnection = dataHandler.openMySQLConnection()
        # if connection fails, return
        if not self.testMySQLConnection: 
            logging.writeError("failed connecting to mySQL server, check config - exiting.")
            return
        # get cursor
        self.mySQLCursor = self.mySQLConnection.cursor()

        if dataHandler.results:
            SQLCommand = "INSERT INTO `weatherstation`(`time_utc`, `time_local`, `temperature`, `humidity`, `pressure`, `cpu_usage`, `memory_usage`, `cpu_temperature`)" 
            SQLCommand += "VALUES ('" + str(measurementTimeUTC) + "','" + str(measurementTimeLocal) + "','" + str(dataHandler.results["temperature"]) + "','" + str(dataHandler.results["humidity"]) + "','" + str(dataHandler.results["pressure"]) + "','" + str(dataHandler.results["cpu_usage"]) + "','" + str(dataHandler.results["memory_usage"]) + "','" + str(dataHandler.results["cpu_temperature"]) + "')"
            
            self.mySQLCursor.execute(SQLCommand)
            self.mySQLConnection.commit()

            logging.write("Retrieved table successfully")
        else:
            logging.writeError("Was not able to retrieve data")

        # finally close DB connection
        self.mySQLCursor.close()
        self.mySQLConnection.close()

        
    def __init__(self):        
        logging.write("Started weatherstation2mysql")

        # open mySQL connection only for testing purposes
        self.testMySQLConnection = dataHandler.openMySQLConnection()
        
        # if connection fails, return
        if not self.testMySQLConnection: 
            logging.writeError("failed connecting to mySQL server, check config - exiting.")
            return
        
        # close test-connection 
        self.testMySQLConnection.close()
        
        # start runner
        dataHandler.controller(self)
        

# init server class
if __name__ == "__main__":
    dataHandler()
