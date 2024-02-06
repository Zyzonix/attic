#!/bin/bash
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 29-07-2023 19:18:22
# 
# file          | proxmox-tweaks/install-proxmox-tweaks.sh
# project       | attic
# file version  | 0.0.2
#

BSSCRIPTURL=https://raw.githubusercontent.com/Zyzonix/attic/main/proxmox-tweaks/tweak-proxmox-bs.sh
VESCRIPTURL=https://raw.githubusercontent.com/Zyzonix/attic/main/proxmox-tweaks/tweak-proxmox-ve.sh

PATH=/usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/
CRONPATH=/etc/cron.daily/proxmox-tweaks

CRONBS="#!/usr/bin/bash
/bin/bash /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/tweak-proxmox-bs.sh"
CRONVE="#!/usr/bin/bash
/bin/bash /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/tweak-proxmox-ve.sh"

# get download directory to delete script after installation
DOWNDIR=$PWD

# check if executed as root
USR=$(/usr/bin/id -u)
if [ $USR -ne 0 ]
  then echo "Please rerun this script as root (su -i or sudo)- exiting..."
  exit
fi

echo "Installing Proxmox Tweaker"
printf "%s " "Select OS: PVE/PBS:"
read OS

if [[ $OS == "PBS" || $OS == "pbs" ]]; then
    echo "Creating directory" $PATH
    /usr/bin/mkdir -p "$PATH"
    cd $PATH
    
    echo "Downloading script fom " $BSSCRIPTURL
    /usr/bin/wget $BSSCRIPTURL

    echo "Creating crontab"
    echo "$CRONBS" | /usr/bin/tee $CRONPATH

    # make crontab executeable
    /usr/bin/chmod +x $CRONPATH
    
    echo "Cleaning up"
    /usr/bin/rm $DOWNDIR/install-proxmox-tweaks.sh
    echo ""
    echo "Installed Proxmox Tweaker"
    exit 0

elif [[ $OS == "PVE" || $OS == "pve" ]]; then
    echo "Creating directory" $PATH
    /usr/bin/mkdir -p "$PATH"
    cd $PATH
    
    echo "Downloading script fom " $VESCRIPTURL
    /usr/bin/wget $VESCRIPTURL

    echo "Creating crontab"
    echo "$CRONVE" | /usr/bin/tee $CRONPATH

    # make crontab executeable
    /usr/bin/chmod +x $CRONPATH
    
    echo "Cleaning up"
    /usr/bin/rm $DOWNDIR/install-proxmox-tweaks.sh
    echo ""
    echo "Installed Proxmox Tweaker"
    exit 0

else
    echo "Was not able to read your input - returning."
    exit 1
fi
