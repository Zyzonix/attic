#!/bin/bash
#
# written by Zyzonix
# published by xerberosDevelopments
#
# Copyright (c) 2026 xerberosDevelopments
#
# date created  | 09-01-2026 11:53:31
# 
# file          | rustdesk/import-rustdesk-to-repository.sh
# project       | attic
#

#
# this script downloads rustdesk-deb-files to filesystem and updates files for deb-repository
#

# path to store downloaded debs (sub path for architecture will be added)
TARGETPATH="/srv/ext-stor/repo/pool/main/"

# version is first argument
VERSION=$1

# URL to releases page
URL="https://github.com/rustdesk/rustdesk/releases/download/"

# sub path to dirs
AMD64_PATH="amd64/"
ARM64_PATH="arm64/"

# name format on github
AMD64_PRE_NAME="rustdesk-"$1"-x86_64.deb"
ARM64_PRE_NAME="rustdesk-"$1"-aarch64.deb"

# final name format
AMD64_FINAL_NAME="rustdesk_"$1"_amd64.deb"
ARM64_FINAL_NAME="rustdesk_"$1"_arm64.deb"

echo "Downloading version:" $1 $TARGETPATH$AMD64_PATH$AMD64_FINAL_NAME
echo ""
read -p "Press any key to continue the download or CTRL+C to exit..." CONFIRM
echo ""

echo "Trying to download:" $AMD64_PRE_NAME
/usr/bin/curl -L $URL$1/$AMD64_PRE_NAME -o $TARGETPATH$AMD64_PATH$AMD64_FINAL_NAME
echo "Downloaded to:" $TARGETPATH$ARM64_PATH
echo "Named downloaded file:" $AMD64_FINAL_NAME
echo ""

echo "Trying to download:" $ARM64_PRE_NAME
/usr/bin/curl -L $URL$1/$ARM64_PRE_NAME -o $TARGETPATH$ARM64_PATH$ARM64_FINAL_NAME
echo "Downloaded to:" $TARGETPATH$ARM64_PATH
echo "Named downloaded file:" $ARM64_FINAL_NAME
echo ""




