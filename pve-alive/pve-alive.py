
#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 25-05-2023 16:56:36
# 
# file          | pve-alive/pve-alive.py
# project       | pve-alive
# file version  | 0.0.1
#

#
# Description: check whether  a systemservice/process is running, if so let a LED via GPIO blink (designed for Raspberry Pi)
#

from gpiozero import LED
import subprocess
from time import sleep

class main():
    global processes_to_check 
    processes_to_check = {
        "pvedaemon",
        "pveproxy"
    }

    # GPIO number here 
    greenled = LED(XX)

    def process_check(process):
        running = False
        service_status = subprocess.call(["systemctl", "is-active", "-q", process])
        process_status = subprocess.call(["pidof", "-q", process])

        # if exit code is 0 --> service running
        if (service_status and process_status) == 0: 
            running = True

        return running

    def blinker(self, ledon):
        rerun = 12
        if ledon:
            while rerun > 0:
                #print("Turning LED on")
                main.greenled.on()
                sleep(0.5)
                main.greenled.off()
                #print("Turned off")
                sleep(4.5)
                rerun -= 1
                #print(rerun)
        else:
            sleep(30)
        #print("rerun")
        main.runner(self)

    def sleeper(self):
        sleep(10)
        main.runner(self)

    def runner(self):
        all_processes_running = True
        for process in processes_to_check:
            #print("Checking: " + process)
            process_running_state = main.process_check(process)
            if not process_running_state: 
                all_processes_running = False

        if all_processes_running:
            main.blinker(self, True)
        else:
            #print("Waiting...")
            main.greenled.off()
            main.blinker(self, False)

    def __init__(self):
        #print("Started PVE-Alive")
        self.runner()

if __name__ == '__main__':
    main() 
