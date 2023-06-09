#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by ZyzonixDevelopments 
# -
# date      | 24/06/2021
# python-v  | 3.8.3
# 

from datetime import datetime, date
import sys
import time 
import os

def core():
    while True:
        print('[' + str(date.today()) + " - " + str(datetime.now().strftime("%H:%M:%S")) + ']\n')
        os.system("df | grep /dev/sd")
        print('-------------------------------------------------------')
        # add new drives here
        drives = []
        drives.append("/dev/sda")
        #drives.append("/dev/sdb")
        drives.append("/dev/sdc")
        #drives.append("/dev/sdd")
        #drives.append("/dev/sde")
        drives.append("/dev/sdf")
        drives.append("/dev/sdg")
        #drives.append("/dev/sdh")
        drives.append("/dev/sdi")
        drives.append("/dev/sdj")
        drives.append("/dev/sdk")
        drives.append("/dev/sdl")
        drives.append("/dev/sdm")
        for dire in drives:
            os.system("hddtemp " + dire)
        print('-------------------------------------------------------')
        print('CPU-statistics')
        os.system("sensors | grep 'Package' && sensors | grep 'Core'")
        print('-------------------------------------------------------')
        print('CHIA-statistics')
        fsses = []
        fsses.append("HP_800GB")
        fsses.append("wd_3tb")
        fsses.append("wd_4tb_1")
        fsses.append("wd_4tb_2")
        fsses.append("wd_2tb")
        fsses.append("samsung_2tb_2")
        fsses.append("samsung_2tb_1")
        fsses.append("seagate_3tb_bc")
        fsses.append("seagate_3tb_sh")
        fsses.append("seagate_4tb_EXT_1")
        fsses.append("seagate_4tb_EXT_2")
        fsses.append("seagate_8tb_EXT_1")
        fsses.append("tsa_16tb_1")
        collector = []
        counter = {"k35":0, "k34":0, "k33":0, "k32":0}
        summ = 0
        for fs in fsses:
            for f in os.listdir("/media/chia/" + fs):
                fsplit = f.split("-")
                if not len(fsplit) == 1:
                    counter[fsplit[1]] = counter[fsplit[1]] + 1
        for pkey in counter.keys():
            print(pkey + " : " + str(counter[pkey]))
            summ += counter[pkey]
        print("plots in total: " + str(summ))
        time.sleep(300)
        os.system("clear")
core()
