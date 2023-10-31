#!/bin/bash

CFG=$1

if [ -z "$CFG" ]; then
    echo "no configuration file specified"
    exit 1
fi
if [ ! -e "$CFG" ]; then
    echo "configuration file $CFG does not exist"
    exit 1
fi

MODELDIR=$(mo2-configure -d $CFG) || exit 1

pushd $MODELDIR
dummy config.nml results.nc || exit 1
popd

mo2-simobs_dummy -d $MODELDIR/results.nc $CFG

