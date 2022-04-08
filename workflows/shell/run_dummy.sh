#!/bin/bash

CFG=$1
DUMMY=$2

if [ -z "$CFG" ]; then
    echo "no configuration file specified"
    exit 1
fi
if [ ! -e "$CFG" ]; then
    echo "configuration file $CFG does not exist"
    exit 1
fi
CFG=$(realpath $CFG)

if [ -z "$DUMMY" ]; then
    DUMMY=dummy
else
    DUMMY=$(realpath $DUMMY)
fi

# get configured run
MODELDIR=$(mo2-transition $CFG CONFIGURED ACTIVE) || exit 1

# run it
cd $MODELDIR
$DUMMY config.nml results.nc || exit 1

# mark it as completed
mo2-transition $CFG ACTIVE RUN -i || exit 1
