#!/bin/bash

set -m

free && sync && sudo sh -c "/usr/bin/echo 3 > /proc/sys/vm/drop_caches" && free
$2 &
PID=$!
echo "Application process ID: $PID"
collectl -i:1 -sZ $1 --procfilt p$PID,P$PID &
CCTL=$!
echo "Collectl PID: $CCTL"
JID=$(jobs -l | grep $PID | awk '{print $1;}' | sed 's/-//g' | sed 's/[][]//g')
fg $JID
kill $CCTL



