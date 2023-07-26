#!/bin/bash
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2022 ZyzonixDevelopments
#
# date created  | 07-12-2022 10:36:32
# 
# file          | revive-elektra.sh
# project       | revive-elektra
# file version  | 0.0.1
#

# VAR-STORAGE
# timestamp
ts=`date +%T`

check_process_id() {
  echo "$ts: checking $1"
  # return if no process to check is provided
  [ "$1" = "" ] && return 0 
  # check for acrive process id, return 1 if exists
  [ `pgrep -n $1` ] && return 1 || return 0
}

# NetworkManager always first (ssh)
for service in "NetworkManager" "dbus" "sshd" "samba"
do
  # calling function
  check_process_id $service

  # saving result
  result=$?

  # analyzing result
  [ $result -eq 0 ] && echo "$ts: not running, restarting..." && service restart $service 
  [ $result -eq 1 ] && echo "$ts: $service is running"

  # adding empty line to seperate all services visually
  echo ""
done
