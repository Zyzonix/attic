#!/bin/bash
#
# written by Zyzonix
# published by xerberosDevelopments
#
# Copyright (c) 2025 xerberosDevelopments
#
# date created  | 25-06-2025 18:12:27
# 
# file          | rustdesk/set-custom-rustdesk-id.sh
# project       | attic
#

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

printf "\n\nSleeping for 10sec to verify correct status of rustdesk services..."
sleep 10
printf "\n\nStopping rustdesk services"
systemctl stop rustdesk.service
printf "\n"

read -p "Enter custom ID: " ID
printf "ID will be set to: $ID"

printf "\n\nSetting RustDesk contents..."

homes=$(ls /home)

for home in $homes; do
    sed -i "s/enc_id.*/id = '$ID'/g" /home/$home/.config/rustdesk/RustDesk.toml
    sed -i "/id =.*/a\enc_id = ''" /home/$home/.config/rustdesk/RustDesk.toml
done

sed -i "s/enc_id.*/id = 'ID'/g" /root/.config/rustdesk/RustDesk.toml
sed -i "/id =.*/a\enc_id = ''" /root/.config/rustdesk/RustDesk.toml


sleep 5
printf "\n\nStarting rustdesk services\n"
systemctl start rustdesk.service