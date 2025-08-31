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
# - 3.4.4
#


# Installation:
# $ mkdir /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/
# $ wget https://raw.githubusercontent.com/Zyzonix/attic/main/proxmox-tweaks/tweak-proxmox-bs.sh
# then install a crontab under /etc/cron.daily to be run once a day: 
# # Auto tweak proxmox after each upgrade (https://github.com/Zyzonix/attic/proxmox-tweaks)
# /bin/bash /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/tweak-proxmox-bs.sh


PROXMOXLIBJS=/usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js
PROXMOXWIDGETPATH=/usr/share/javascript/proxmox-widget-toolkit/

KEY1='res === null ||'
KEY2='res === undefined ||'
KEY3='!res ||'
KEY4="res.data.status.toLowerCase() !== 'active'"

DATE=$(date '+%Y-%m-%d')

# check if file was updated (true if contains SEARCH1)
if grep -q "$KEY1" "$PROXMOXLIBJS"; then

    # get row number of line and format to raw number
    FIRSTLINE=$(grep -i -n "res === null ||" $PROXMOXLIBJS)
    readarray -d ":" -t FIRSTLINENUMBER <<< "$FIRSTLINE"
    LINE2NUMBER="$(($FIRSTLINENUMBER+1))"
    LINE3NUMBER="$(($FIRSTLINENUMBER+2))"
    LINE4NUMBER="$(($FIRSTLINENUMBER+3))"

    # get all other lines
    LINE1=$(sed -n ${FIRSTLINENUMBER}p $PROXMOXLIBJS)
    LINE2=$(sed -n ${LINE2NUMBER}p $PROXMOXLIBJS)
    LINE3=$(sed -n ${LINE3NUMBER}p $PROXMOXLIBJS)
    LINE4=$(sed -n ${LINE4NUMBER}p $PROXMOXLIBJS)

    if [[ "$LINE1" == *"$KEY1"* ]] && [[ "$LINE2" == *"$KEY2"* ]] && [[ "$LINE3" == *"$KEY3"* ]] && [[ "$LINE4" == *"$KEY4"* ]]; then
        echo "ProxmoxBS seems to got an update"
        echo "tweak-proxmox-bs.sh found lines to remove. Removing..."
    
        # create backup of old js-file
        cp $PROXMOXLIBJS $PROXMOXLIBJS.bak.$DATE

        # start remove from end to prevent line number change while removing
        sed -i ${LINE4NUMBER}d $PROXMOXLIBJS
        sed -i ${LINE3NUMBER}d $PROXMOXLIBJS
        sed -i ${LINE2NUMBER}d $PROXMOXLIBJS
        sed -i ${FIRSTLINENUMBER}d $PROXMOXLIBJS
        
        echo "Removed old lines..."
        IFLINENUMBER="$(($FIRSTLINENUMBER-1))"
        IFLINECONTENT=$(sed -n ${IFLINENUMBER}p $PROXMOXLIBJS)
        NEWIFLINECONTENT="$IFLINECONTENT false"

        sed -i "${IFLINENUMBER}s/.*/${NEWIFLINECONTENT}/" $PROXMOXLIBJS

        echo "Updated remaining lines."

        echo ""
        echo "Changed lines:"
        echo ""
        /usr/bin/git diff $PROXMOXLIBJS.bak.$DATE $PROXMOXLIBJS

        echo ""

        NUMBEROFBACKUPS=$(/usr/bin/find $PROXMOXWIDGETPATH -name "*.bak.*" | wc -l)
        if (( $NUMBEROFBACKUPS > 1 )); then
            echo "Cleaning up old backups..."
            echo "Found $NUMBEROFBACKUPS backup files"
            echo "Deleting backups older than 120 days..."
            /usr/bin/find $PROXMOXWIDGETPATH -name "*.bak.*" -mtime +120 -print -delete
            echo ""
            echo "Finished backup cleanup"
        fi
        
    fi

    # restart proxmox proxy
    systemctl restart proxmox-backup-proxy.service

    echo ""
    echo "Restarted proxy"
fi
