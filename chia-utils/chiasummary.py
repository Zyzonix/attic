#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by ZyzonixDevelopments 
# -
# date      | 16/10/2021
# python-v  | 3.8.3
# 

from datetime import datetime, date
import sys
import time 
import os

def core():
    while True:
        print('[' + str(date.today()) + " - " + str(datetime.now().strftime("%H:%M:%S")) + ']\n')
        #print("CHIA farm summary\n")
        os.system("/home/chia/chia-blockchain/venv/bin/python /home/chia/chia-blockchain/venv/bin/chia farm summary")
        print('\n-------------------------------------------------------\n')
        os.system("/home/chia/chia-blockchain/venv/bin/python /home/chia/chia-blockchain/venv/bin/chia show -s")
        #print('-------------------------------------------------------')
        #print('CPU-statistics')
        #os.system("/home/chia/chia-blockchain/venv/bin/python /home/chia/chia-blockchain/venv/bin/chia farm challenges ")
        #print('-------------------------------------------------------')
        #print('CHIA-statistics')
        time.sleep(300)
        os.system("clear")
core()
