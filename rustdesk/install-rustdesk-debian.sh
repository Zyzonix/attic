#!/bin/bash
#
# written by Zyzonix
# published by xerberosDevelopments
#
# Copyright (c) 2024 xerberosDevelopments
#
# date created  | 09-08-2024 08:42:34
# 
# file          | rustdesk/install-rustdesk-debian.sh
# project       | attic
#
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

printf "Adding repository key"
curl -sS https://repo.zyzonix.net/ReleaseKey.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/repo.zyzonix.net.gpg > /dev/null

printf "\nAdding repository\n"
echo "deb [signed-by=/usr/share/keyrings/repo.zyzonix.net.gpg] https://repo.zyzonix.net/ stable main" | sudo tee /etc/apt/sources.list.d/repo.zyzonix.net.list

printf "\n"
printf "\nUpdating lists"
apt update

printf "\n\nInstalling rustdesk"
apt install rustdesk -y
printf "Installed rustdesk successfully..."
