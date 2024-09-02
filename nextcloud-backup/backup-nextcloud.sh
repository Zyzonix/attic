#!/bin/bash
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 17-07-2024 11:23:09
# 
# file          | nextcloud-backup/backup-nextcloud.sh
# project       | attic
# file version  | 1.0.2
#

# ----------------------------------------------------- #
# davfs2 and etherwake are required to run this script! #
# ----------------------------------------------------- #

MAILTO=root

# MAC and IP/DNS name of remote storage
REMOTESERVERMAC=
REMOTESTORAGESERVER=
REMOTESTORAGESSHPORT=22
REMOTESTORAGEUSER=
REMOTESTORAGEUSERPASSWORD=""
# path on remove server to which the tarball should be copied
REMOTESTORAGEPATH=

# simply copy the URL from your Nextcloud's Webinterface (WebDAV)
NEXTCLOUDURL=
NEXTCLOUDUSER=
NEXTCLOUDPASSWORD=
MOUNTDIRECTORY=

# following settings are for storing
# name of tarball (<name>_<date>.tar)
CLOUDNAME=
TARGETSTORAGEDIRECTORY=

# END OF CUSTOM CONFIGURATION PART 

# do not configure this
TARBALLNAME=$CLOUDNAME"_"$(/usr/bin/date '+%Y-%m-%d_%H-%M-%S')
STARTTIME=$(/usr/bin/date '+%Y-%m-%d %H:%M:%S')
STARTTIMERAW=$(date +%s)

# waking up remote storage
/usr/sbin/etherwake $REMOTESERVERMAC

# wait 120 seconds to let server boot
sleep 120

echo "Checking if storage is pingable"
if ! ping -c 1 $REMOTESTORAGESERVER &> /dev/null
then
  echo "Storage server couldn't be waked up... returning"
  exit
fi
echo "Server is pingable continuing..."

echo ""
echo "» Backing up Nextcloud «"
echo ""
echo ""
echo "Starting at:" $STARTTIME
echo "Using the following settings:"
echo ""
echo "- Nextcloud-URL: " $NEXTCLOUDURL
echo "- Nextcloud-User:" $NEXTCLOUDUSER
echo ""
echo "- Mount-Directory:" $MOUNTDIRECTORY
echo "- Target/Storage-Directory:" $TARGETSTORAGEDIRECTORY
echo ""
/usr/bin/sleep 5
echo ""
echo "Mounting..."
/usr/bin/printf "$NEXTCLOUDUSER\n$(echo $NEXTCLOUDPASSWORD)" | /usr/bin/mount -t davfs $NEXTCLOUDURL $MOUNTDIRECTORY -v -r
echo ""
echo "Mounted."
echo "Getting all files..."
/usr/bin/find $MOUNTDIRECTORY.
echo ""
echo "Got all files."
echo "Creating tarball with name: "$TARBALLNAME".tar"
COMPLETEPATH=$TARGETSTORAGEDIRECTORY$TARBALLNAME.tar
/usr/bin/tar -cf $COMPLETEPATH $MOUNTDIRECTORY
echo ""
echo "Created tarball, stored in " $TARGETSTORAGEDIRECTORY
/usr/bin/sleep 10
echo "Unmounting..."
/usr/bin/umount $MOUNTDIRECTORY
echo ""
echo "Unmounted."
echo ""
echo "Finished at:" $(/usr/bin/date '+%Y-%m-%d %H:%M:%S')
ENDTIMERAW=$(date +%s)
echo "Took" $(( (ENDTIMERAW - STARTTIMERAW) / 60)) "minutes."
echo "Copying to remote server via SCP..."
/usr/bin/sshpass -p $REMOTESTORAGEUSERPASSWORD /usr/bin/scp -P $REMOTESTORAGESSHPORT $COMPLETEPATH $REMOTESTORAGEUSER@$REMOTESTORAGESERVER:$REMOTESTORAGEPATH
echo "Copied tarball to remote storage"
echo ""
echo "» Backing up Nextcloud finished «"
echo ""




