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
# file version  | 1.0.0
#

# -------------------------------------- #
# davfs2 is required to run this script! #
# -------------------------------------- #

MAILTO=root

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
echo ""
echo "» Backing up Nextcloud finished «"
echo ""




