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
# file version  | 0.0.1
#
# GitHub: https://github.com/Zyzonix/storage/proxmox-tweaks/tweak-proxmox-ve.sh
#

#############################################################
# This script is designed for Proxmox Virtual Environment!! #
#############################################################
#
# tested against Proxmox VE 7.4-3
#
# Installation:
# $ mkdir /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/
# $ wget https://raw.githubusercontent.com/Zyzonix/storage/main/proxmox-tweaks/tweak-proxmox-ve.sh
# then install a crontab under /etc/crontab to be run once a day: 
# # Auto tweak proxmox after each upgrade (https://github.com/Zyzonix/storage/proxmox-tweaks)
# 1  0    * * *   root    /bin/bash /usr/share/javascript/proxmox-widget-toolkit/proxmox-tweaks/tweak-proxmox-ve.sh
#

# create backup of old js-file
cp /usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js /usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js.bak

# keystring1 (old config) -> delete line
SEARCH1="if (res === null || res === undefined || !res || res"

# keystring2 (old config)
SEARCH2=".data.status.toLowerCase() !== 'active') {"
# new keystring2
REPLACE1="if (false) {"


# replace first line
sed -i "s/$SEARCH1/$REPLACE1/g" /usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js

# delete second line
sed -i "/$SEARCH2/d" /usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js

# restart proxmox proxy
systemctl restart pveproxy.service
