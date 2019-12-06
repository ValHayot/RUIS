#!/bin/bash

free && sync && sudo sh -c "/usr/bin/echo 3 > /proc/sys/vm/drop_caches" && free
screen -S bids -dm bash -c "$2; screen -S collectl -X stuff $'\003'; exit"
PID=$(ps aux | grep singularity | grep -v grep | awk -F ' ' '{print $2}')
screen -S collectl -dm collectl $1 

