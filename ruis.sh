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
  kill $collectl_pid 2> /dev/null
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
PERFQ=`readlink -f $(which perfquery)`

if [[ -z ${COLLECTL_OPTIONS} ]]; then
  COLLECTL_OPTIONS="-sCDNfM -omT --dskopts z --cpuopts z -i .1"
fi

if [[ $PERFQ != "" ]]
then
    # Check if infiniband exists
    
    perfquery -x
    err=`echo $?`

    if [[ $err == 0 ]]
    then
        echo "Including infiniband profiling"
        PROFILE_IB="--bind $PERFQ:/bin/perfquery"
        COLLECTL_OPTIONS="$COLLECTL_OPTIONS -sX"
    fi
fi

( collectl $COLLECTL_OPTIONS --sep , -P -f "$SINGWD/$TMP" > /dev/null 2>&1 ) &
collectl_pid=$!
echo "Executing command: $@"
eval $@
kill $collectl_pid

echo "Processing output data..."
DATA_DIR="$PWD/data-$(uuidgen)"
mkdir -p $DATA_DIR
ls $WORK_DIR | xargs -I{} mv $WORK_DIR/{} $DATA_DIR/{}

ls $DATA_DIR/*.gz | xargs gunzip
ls $DATA_DIR | grep -v .csv | xargs -I{} mv $DATA_DIR/{} $DATA_DIR/{}.csv

for f in $(ls $DATA_DIR)
do
  new_name=$(echo $f | sed 's/.*\-[0-9]*\.//')
  mv $DATA_DIR/$f $DATA_DIR/$new_name
done
echo $1 > $DATA_DIR/command
