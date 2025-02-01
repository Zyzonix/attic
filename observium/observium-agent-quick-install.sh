#!/bin/bash
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 23-05-2023 07:09:26
# 
# file          | observium-agent-quick-install.sh
# project       | observium-scripts
# file version  | 0.0.3
#

echo "#################################################################"
echo "# Automated remote installer for the observium agent for debian #"
echo "#                                                               #"
echo "# This script has been developed by Zyzonix                     #"
echo "# https://fixes.brecht-schule.hamburg/                          #"
echo "#################################################################"
echo ""

# check if executed as root
USR=$(/usr/bin/id -u)
if [ $USR -ne 0 ]
  then echo "Please rerun this script as root (su -i or sudo)- exiting..."
  exit
fi

echo "###################################################################"
echo "# This script needs to be executed on the machine where the agent #"
echo "# should be installed!                                            #"
echo "###################################################################"
echo ""
read -p "Press any key to continue the installation or CTRL+C to exit..." CONFIRM
echo ""

# static vars
OBSERVIUMPATH=/opt/observium
OBSERVIUMIP="0.0.0.0"
OBSERVIUMPORT=22
OBSERVIUMUSER=root
OBSERVIUMROOTPW=
SCPPATH=/usr/bin/scp
SSHPASSPATH=/usr/bin/sshpass
SSHKEYGENPATH=/usr/bin/ssh-keygen
AGENTDIR=/usr/lib/observium_agent

# select whether to install via systemd-socket or xinetd
INSTALLSYSTEMD=false
INSTALLXINETD=false

ID=XXX
echo "Currently supported and tested distributions are Debian/Ubuntu and ArtixLinux."
echo "Getting OS..."
sleep 2
if [ -f /etc/os-release ]; then
    . /etc/os-release
    ID=$ID

    if [ "$ID" = "debian" ] || [ "$ID" = "ubuntu" ]; then
      SYSTEMDDAEMONRELOAD="systemctl daemon-reload"
      SYSTEMDENABLE="systemctl enable observium_agent.socket"
      SYSTEMDRESTART="systemctl restart observium_agent.socket"
      XINETDENABLE="/usr/bin/systemctl enable xinetd.service"
      XINETDRESTART="/usr/bin/systemctl restart xinetd.service"
      UPDATEGETPATH=/usr/bin/apt-get

      echo ""
      echo "Updating and installing sshpass..."
      echo ""
      $UPDATEGETPATH update 
      $UPDATEGETPATH install sshpass -y

      # decide whether to install via systemd or xinetd
      echo ""
      read -p "Install via systemd or xinetd (Enter 'systemd' or 'xinetd', pressing any other key will install via systemd): " INSTALLATIONMETHOD

      if [ "$INSTALLATIONMETHOD" = "xinetd" ]; then
        INSTALLXINETD=true

        echo ""
        echo "Installing xinetd..."
        $UPDATEGETPATH install xinetd -y
      else 
        INSTALLSYSTEMD=true
      fi

    elif [ "$ID" = "artix" ]; then
      XINETDENABLE="/usr/bin/rc-update add xinetd"
      XINETDRESTART="/usr/bin/rc-service xinetd restart"
      UPDATEGETPATH="/usr/bin/pacman"

      echo ""
      echo "Updating and installing xinetd and sshpass"
      echo ""
      $UPDATEGETPATH update 
      $UPDATEGETPATH -S xinetd-openrc sshpass  --noconfirm

      # install xinetd; artix doesn't use systemd
      INSTALLXINETD=true

    else
      echo ""
      echo "Was not able to detect your system - exiting...."
      echo ""
      exit 1

    fi

    # ask for observiums IP/hostname
    echo ""
    read -p "Please enter either the IP or the hostname of your observium installation: " OBSERVIUMIP

    # check SSH port
    read -p "Please enter the SSH port of your observium installation (default: 22): " SSHPORT
    OBSERVIUMPORT=$SSHPORT

    # ask for observiums root pw
    echo -n "Please enter the password for root@"$OBSERVIUMIP": " 
    read -s OBSERVIUMROOTPW


    if [ "$INSTALLSYSTEMD" = "true" ]; then
      echo ""
      echo "Copying systemd socket and service from observium"
      $SSHPASSPATH -p $OBSERVIUMROOTPW $SCPPATH -o StrictHostKeyChecking=no -P $OBSERVIUMPORT $OBSERVIUMUSER@$OBSERVIUMIP:$OBSERVIUMPATH/scripts/systemd/observium_agent.service /etc/systemd/system/observium_agent\@.service
      $SSHPASSPATH -p $OBSERVIUMROOTPW $SCPPATH -o StrictHostKeyChecking=no -P $OBSERVIUMPORT $OBSERVIUMUSER@$OBSERVIUMIP:$OBSERVIUMPATH/scripts/systemd/observium_agent.socket /etc/systemd/system/observium_agent.socket

      echo ""
      echo "Enabling and starting systemd socket"
      $SYSTEMDDAEMONRELOAD
      $SYSTEMDENABLE
      $SYSTEMDRESTART

    elif [ $INSTALLSYSTEMD == "false" ]; then
      echo ""
      echo "Copying xinetd script from observium"
      $SSHPASSPATH -p $OBSERVIUMROOTPW $SCPPATH -o StrictHostKeyChecking=no -P $OBSERVIUMPORT $OBSERVIUMUSER@$OBSERVIUMIP:$OBSERVIUMPATH/scripts/observium_agent_xinetd /etc/xinetd.d/observium_agent_xinetd

      echo ""
      echo "Enabling xinetd"
      $XINETDRESTART
    fi

    echo ""
    echo "Copying observium agent from observium"
    $SSHPASSPATH -p $OBSERVIUMROOTPW $SCPPATH -o StrictHostKeyChecking=no -P $OBSERVIUMPORT $OBSERVIUMUSER@$OBSERVIUMIP:$OBSERVIUMPATH/scripts/observium_agent /usr/bin/observium_agent

    echo ""
    echo "Creating required directories and copying all scripts"
    mkdir -p $AGENTDIR
    mkdir -p $AGENTDIR/scripts-available
    mkdir -p $AGENTDIR/scripts-enabled
    $SSHPASSPATH -p $OBSERVIUMROOTPW $SCPPATH -o StrictHostKeyChecking=no -r -P $OBSERVIUMPORT $OBSERVIUMUSER@$OBSERVIUMIP:$OBSERVIUMPATH/scripts/agent-local/* /usr/lib/observium_agent/scripts-available/

    if [ $INSTALLSYSTEMD == "true" ]; then
      echo ""
      echo "Restarting systemd socket"
      $SYSTEMDRESTART

    elif [ $INSTALLSYSTEMD == "false" ]; then   
      echo ""
      echo "Restarting xinetd"
      $XINETDRESTART
    fi

    echo ""
    echo "You can now link the scripts to '"$AGENTDIR/scripts-enabled"' as example via "
    echo "'sudo ln -s /usr/lib/observium_agent/scripts-available/os /usr/lib/observium_agent/scripts-enabled'"
    echo ""
    echo "If using ufw or another firewall remind of allowing the port 36602 (observium agent)!"
    echo ""

fi

if [ $ID == "XXX" ]; then
    echo "Failed to detect OS."
fi
exit 0
