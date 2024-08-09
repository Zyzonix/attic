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
echo "\n\nAdding repository key"
curl -sS https://repo.zyzonix.net/ReleaseKey.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/repo.zyzonix.net.gpg > /dev/null

echo "\n\nAdding repository"
echo "deb [signed-by=/usr/share/keyrings/repo.zyzonix.net.gpg] https://repo.zyzonix.net/ stable main" | sudo tee /etc/apt/sources.list.d/repo.zyzonix.net.list

echo "\n\nUpdating lists"
apt update

echo "\n\Installing rustdesk"
apt install rustdesk -y

echo "Installed rustdesk successfully..."
