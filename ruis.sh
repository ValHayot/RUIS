#!/bin/bash
set -eo pipefail

# Handling of temp dir was taken from: https://stackoverflow.com/a/34676160
# the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# the temp directory used, within $DIR
# omit the -p parameter to create a temporal directory in the default location
WORK_DIR=`mktemp -d -p "$DIR"`
echo "[INFO] Created temp working directory $WORK_DIR"

# check if tmp dir was created
if [[ ! "$WORK_DIR" || ! -d "$WORK_DIR" ]]; then
  echo "[INFO] Could not create temp dir"
  exit 1
fi

# deletes the temp directory
function cleanup {
  rm -rf "$WORK_DIR"
  echo "[INFO] Deleted temp working directory $WORK_DIR"
  echo "DONE"
}

# register the cleanup function to be called on the EXIT signal
trap cleanup exit

#######################
##### RUIS script #####
#######################

UUID=$(uuidgen)
SCREEN_RUIS="RUIS-$UUID"
SCREEN_COLLECTL="collectl-$UUID"

COLLECTL="singularity exec ./collectl.sif collectl"

# Sleep for 0.5 seconds before launching applications to allow setup time for collectl.
# Without this the script will crash for instant return such as ls.
echo "Executing command: $1"
screen -S $SCREEN_RUIS -DmS bash -c "sleep 0.5;$1; screen -S $SCREEN_COLLECTL -X stuff $'\003'; exit; echo [INFO] RUIS: application is done!" &
ruis_pid=$!

if [[ -z ${COLLECTL_OPTIONS} ]]; then
  COLLECTL_OPTIONS="-sCDnfM -omT --dskopts z --cpuopts z -i .1"
fi
screen -S $SCREEN_COLLECTL -DmS $COLLECTL $COLLECTL_OPTIONS --sep , -P -f $WORK_DIR --procfilt P $ruis_pid &
collectl_pid=$!
echo "Monitoring application..."
wait $collectl_pid

echo "Processing output data..."
DATA_DIR="$PWD/data-$(uuidgen)"
mkdir -p $DATA_DIR
ls $WORK_DIR | xargs -I{} mv $WORK_DIR/{} $DATA_DIR/{}

ls $DATA_DIR/*.gz | xargs gunzip
ls $DATA_DIR | grep -v .csv | xargs -I{} mv $DATA_DIR/{} $DATA_DIR/{}.csv
