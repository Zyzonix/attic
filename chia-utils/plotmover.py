#!/usr/bin/env python3
#
# written by Zyzonix
# published by xerberosDevelopments
#
# Copyright (c) 2024 xerberosDevelopments
#
# date created  | 09-08-2024 07:05:28
# 
# file          | chia-utils/plotmover.py
# project       | attic
#

# script is designed to move plots from a temporary directory to their final locations

import os
import time
import sys
import psutil
import shutil

# sleep interval in seconds
SLEEPINTERVAL = 60
PLOTFILEEXTENSION = ".plot"

# temporary directory from which files should be moved (must be end with /)
TEMPDIR = ""

# final directories where files should be moved to
FINALDIRS = [
    "/"
]

# plot holder
# format: filename:size
prePLOTSTOMOVE = {}
afterPLOTSTOMOVE = {}
finalPLOTSTOMOVE = []
finalDirsSpaceLeft = []
plotsMoved = {}

print("---[NEW RUN]---")
if not TEMPDIR: 
    print("No TEMP dir defined - exiting...")
    sys.exit(0)

# scan temp dir
filesInDir = os.listdir(TEMPDIR)
for file in filesInDir:
    if file.endswith(PLOTFILEEXTENSION):
        plotSize = os.path.getsize(TEMPDIR + file)
        prePLOTSTOMOVE[file] = plotSize
        print("Found " + file + " with size " + str(plotSize))

if not prePLOTSTOMOVE:
    print("No files found to move in " + TEMPDIR)
    print("Exiting...")
    sys.exit(0)

print("Found " + str(len(prePLOTSTOMOVE.keys())) + " files.")
print("Going to sleep for " + str(SLEEPINTERVAL) + "...")
time.sleep(SLEEPINTERVAL)
print("-------")

# scan temp dir again
filesInDir = os.listdir(TEMPDIR)
for file in filesInDir:
    if file.endswith(PLOTFILEEXTENSION):
        plotSize = os.path.getsize(TEMPDIR + file)
        afterPLOTSTOMOVE[file] = plotSize
        print("Found " + file + " with size " + str(plotSize))

print("Found " + str(len(afterPLOTSTOMOVE.keys())) + " files.")

# compare both dictionaries
for file in afterPLOTSTOMOVE.keys():
    if file in prePLOTSTOMOVE.keys():
        if afterPLOTSTOMOVE[file] == prePLOTSTOMOVE[file]:
            print("Found " + file + " with unchanged size " + str(afterPLOTSTOMOVE[file]))
            print("Adding file to moving list...")
            finalPLOTSTOMOVE.append(file)

if not finalPLOTSTOMOVE:
    print("No files with unchanged size since last scan found - exiting...")
    sys.exit(0)
    
print(str(len(finalPLOTSTOMOVE)) + " files to move...")

# find any disk that has enough space left for the plot
if not FINALDIRS:
    print("No final directories specified - exiting...")
    sys.exit(0)

for finalDir in FINALDIRS:
    dirSpaceLeft = psutil.disk_usage(finalDir)
    if dirSpaceLeft.percent < 99.5: 
        finalDirsSpaceLeft.append(finalDir)
        print("'" + finalDir + "' has 99,5%+ free disk space.")

if not finalDirsSpaceLeft:
    print("No final with enough space left detected - exiting...")
    sys.exit(0)

for plot in finalPLOTSTOMOVE:
    if not len(finalDirsSpaceLeft) > 0:
        print("No disks left...")
        break    
    finalDirSelected = finalDirsSpaceLeft[0]
    freeSpace = psutil.disk_usage(finalDirSelected).free - 50000000000
    print("On device " + finalDirSelected + " are " + freeSpace + " bytes free.")
    if freeSpace > prePLOTSTOMOVE[plot]:
        print("'" + plot + "' will be moved to " + finalDirSelected)
        shutil.move(TEMPDIR + plot, finalDirSelected)
        plotsMoved[plot] = finalDirSelected

    else:
        print("Not enough space left for plot on '" + finalDirSelected + "'")
        finalDirsSpaceLeft.pop(finalDirSelected)

        # if first directory is too full, select another if possible
        if len(finalDirsSpaceLeft) >= 2:
            finalDirSelected = finalDirsSpaceLeft[1]
            freeSpace = psutil.disk_usage(finalDirSelected).free - 50000000000
            print("On device " + finalDirSelected + " are " + freeSpace + " bytes free.")
            if freeSpace > prePLOTSTOMOVE[plot]:
                print("'" + plot + "' will be moved to " + finalDirSelected)
                shutil.move(TEMPDIR + plot, finalDirSelected)
                plotsMoved[plot] = finalDirSelected

print("Finished moving:")
for plot in plotsMoved.keys():
    print(plot + " -> " + plotsMoved[plot])

