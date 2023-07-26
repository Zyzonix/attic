#!/bin/bash
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 24-04-2023 17:22:33
# 
# file          | pbs-on-arm.sh
# project       | proxmox-bs-on-arm
# file version  | 0.0.3
#

PBS_VERSION=v2.4.1
PACKAGE_SUFFIX_ARM=arm64.deb
PACKAGE_SUFFIX_ALL=all.deb
GITHUB_URL=https://github.com/ayufan/pve-backup-server-dockerfiles/releases/download/


WGET=/usr/bin/wget
SU=/usr/bin/su


ARM_PKGS="
    proxmox-backup-server_2.4.1-1
    proxmox-backup-server-dbgsym_2.4.1-1
    proxmox-backup-file-restore_2.4.1-1
    proxmox-backup-file-restore-dbgsym_2.4.1-1
    proxmox-backup-client_2.4.1-1
    libproxmox-rs-perl_0.2.1
    libpve-rs-perl_0.7.5
    libpve-rs-perl-dbgsym_0.7.5
    proxmox-mini-journalreader_1.3-1
    proxmox-mini-journalreader-dbgsym_1.3-1
    pve-xtermjs_4.16.0-1
    pve-xtermjs-dbgsym_4.16.0-1
"

ALL_PKGS="
    proxmox-backup-docs_2.4.1-1
    libjs-extjs_7.0.0-1
    libproxmox-acme-plugins_1.4.4
    libproxmox-acme-perl_1.4.4
    libjs-qrcodejs_1.20201119-pve1
    libpve-common-perl_7.3-4
    pmg-i18n_2.12-1
    pbs-i18n_2.12-1
    pve-eslint_8.23.1-1
    proxmox-widget-toolkit_3.6.5
    proxmox-widget-toolkit-dev_3.6.5
"

OTHER_PKGS="
    gdisk
"

# change to root
echo "Changing to root user"
/usr/bin/su
echo ""

echo "Installing all required packages"
/usr/bin/apt install $OTHER_PKGS
echo ""

/usr/bin/sudo /usr/bin/mkdir pbs_$PBS_VERSION"/"
cd pbs_$PBS_VERSION"/"
# get arm specific packages
for package in $ARM_PKGS; do
    $WGET $GITHUB_URL$PBS_VERSION"/"$package"_"$PACKAGE_SUFFIX_ARM
done

# get all other packages
for package in $ALL_PKGS; do
    $WGET $GITHUB_URL$PBS_VERSION"/"$package"_"$PACKAGE_SUFFIX_ALL
done


# install downloaded packages
/usr/bin/sudo /usr/bin/apt install ./* -y


# removing subscription badge
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
systemctl restart proxmox-backup-proxy.service

rm /etc/apt/sources.list.d/pbs-enterprise.list

echo ""
echo "#####################"
echo "# PLEASE REBOOT NOW #"
echo "#####################"
echo ""
