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

RUN_MODEL=$(dirname $0)/run_dummy.sh
if [ ! -e "$RUN_MODEL" ]; then
    echo "could not find model script"
    exit 1
fi


mo2-configure $CFG
ret=$?

if [ $ret = 0 ]; then
    $RUN_MODEL $CFG
fi
