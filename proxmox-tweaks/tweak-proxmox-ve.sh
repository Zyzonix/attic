#!/bin/bash
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 14-04-2023
# 
# file          | tweak-proxmox-ve.sh
# project       | proxmox-tweaks
# file version  | 0.0.2
#
# GitHub: https://github.com/Zyzonix/attic/proxmox-tweaks/tweak-proxmox-ve.sh
#

#############################################################
# This script is designed for Proxmox Virtual Environment!! #
#############################################################
#
# tested against Proxmox VE 
# - 7.4-16
#

# Installation:
# $ mkdir /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/
# $ wget https://raw.githubusercontent.com/Zyzonix/attic/main/proxmox-tweaks/tweak-proxmox-ve.sh
# then install a crontab under /etc/crontab to be run once a day: 
# # Auto tweak proxmox after each upgrade (https://github.com/Zyzonix/attic/proxmox-tweaks)
# 1  0    * * *   root    /bin/bash /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/tweak-proxmox-ve.sh
#


PROXMOXLIBJS=/usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js

# keystring1 (old config) -> delete line
SEARCH1='if (res === null || res === undefined || !res || res'

# keystring2 (old config)
SEARCH2=".data.status.toLowerCase() !== 'active') {"
# new keystring2
REPLACE1="if (false) {"

# check if file was updated (true if contains SEARCH1)
if grep -q "$SEARCH1" "$PROXMOXLIBJS"; then

    echo "ProxmoxVE seems to got an update"
    echo "tweak-proxmox-ve found lines to remove. Removing..."
    # create backup of old js-file
    cp $PROXMOXLIBJS $PROXMOXLIBJS.bak

    # replace first line
    sed -i "s/$SEARCH1/$REPLACE1/g" $PROXMOXLIBJS

    # delete second line
    sed -i "/$SEARCH2/d" $PROXMOXLIBJS

    # restart proxmox proxy
    systemctl restart pveproxy.service
    
    echo "Restarted proxy"
fi
