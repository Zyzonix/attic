#!/bin/bash
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 14-04-2023
# 
# file          | tweak-proxmox-bs.sh
# project       | proxmox-tweaks
# file version  | 0.0.2
#
# GitHub: https://github.com/Zyzonix/attic/proxmox-tweaks/tweak-proxmox-bs.sh
#

#######################################################
# This script is designed for Proxmox Backup Server!! #
#######################################################
#
# tested against Proxmox BS 
# - 2.4-1
# - 2.4-2
# - 3.0-1
#


# Installation:
# $ mkdir /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/
# $ wget https://raw.githubusercontent.com/Zyzonix/attic/main/proxmox-tweaks/tweak-proxmox-bs.sh
# then install a crontab under /etc/cron.daily to be run once a day: 
# # Auto tweak proxmox after each upgrade (https://github.com/Zyzonix/attic/proxmox-tweaks)
# /bin/bash /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/tweak-proxmox-bs.sh


PROXMOXLIBJS=/usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js

# keystring1 (old config) -> delete line
SEARCH1='if (res === null || res === undefined || !res || res'

# keystring2 (old config)
SEARCH2=".data.status.toLowerCase() !== 'active') {"
# new keystring2
REPLACE1="if (false) {"

# check if file was updated (true if contains SEARCH1)
if grep -q "$SEARCH1" "$PROXMOXLIBJS"; then

    echo "ProxmoxBS seems to got an update"
    echo "tweak-proxmox-bs.sh found lines to remove. Removing..."
    # create backup of old js-file
    cp $PROXMOXLIBJS $PROXMOXLIBJS.bak

    # replace first line
    sed -i "s/$SEARCH1/$REPLACE1/g" $PROXMOXLIBJS

    # delete second line
    sed -i "/$SEARCH2/d" $PROXMOXLIBJS

    # restart proxmox proxy
    systemctl restart proxmox-backup-proxy.service

    echo "Restarted proxy"
fi
