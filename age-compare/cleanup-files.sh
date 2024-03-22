#!/bin/bash
# Script checks whether a file is older than specific time, if so it deletes the file to keep a directory cleaned
#
# Sourced from: https://gist.github.com/ashrithr/5614283
#

#
# Installation in crontab with following scheme: [<time-to-run>] <path-to-file> >> <path-to-logfile>
#

# age provided in days
AGE=14
# directory to end with /
DIRECTORY="/path/to/check/"

# get current time for logging
currentDate=$(date '+%Y-%m-%d_%H-%M-%S')
echo "-----------------------------"
echo $currentDate "selected directory:" $DIRECTORY
echo ""

function check() {
	currentDate=$(date '+%Y-%m-%d_%H-%M-%S')
	if [[ ! -e "$@" ]]; then
		echo $currentDate "file $@ does not exist"
		exit 1
	fi
	MAXAGE=$(bc <<< $AGE'*24*60*60') # seconds in 24 hours
	
	# file age in seconds = current_time - file_modification_time.
	FILEAGE=$(($(date +%s) - $(stat -c '%Y' "$@")))
	test $FILEAGE -lt $MAXAGE && {
			echo $currentDate "less than $AGE days old: $@"
			return 0
	}
	echo $currentDate "file is older than $AGE days: $@"
	echo $currentDate "removing..."
	rm "$@"
	return 1
}

DIRECTORYCONTENT=$DIRECTORY"*"
echo $currentDate "all files/folders in directory:" $DIRECTORYCONTENT
echo ""
for scan in $DIRECTORYCONTENT
do
	# Take action on each file. $scan store current file name
	# will ignore directories
	if [ -f "$scan" ]; then
	check "$scan"
	fi
done

echo ""