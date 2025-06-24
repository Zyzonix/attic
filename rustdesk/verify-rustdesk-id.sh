#!/bin/bash
#
# written by Zyzonix
# published by xerberosDevelopments
#
# Copyright (c) 2025 xerberosDevelopments
#
# date created  | 24-06-2025 11:42:56
# 
# file          | rustdesk/verify-rustdesk-id.sh
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

#read -p "Enter hostname: "  ID
ID=$(echo $HOSTNAME)
printf "Hostname is: $ID"

printf "\n\nSetting RustDesk contents..."

homes=$(ls /home)

for home in $homes; do
    sed -i "s/enc_id.*/id = '$ID'/g" /home/$home/.config/rustdesk/RustDesk.toml
    sed -i "/id =.*/a\enc_id = ''" /root/$home/.config/rustdesk/RustDesk.toml
done

sed -i "s/enc_id.*/id = 'ID'/g" /root/.config/rustdesk/RustDesk.toml
sed -i "/id =.*/a\enc_id = ''" /root/.config/rustdesk/RustDesk.toml


sleep 5
printf "\n\nStarting rustdesk services"
systemctl start rustdesk.service