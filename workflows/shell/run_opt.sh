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

CONFIGURE=$(dirname $0)/configure.sh
if [ ! -e "$CONFIGURE" ]; then
    echo "could not find configure script"
    exit 1
fi

ret=1
while [ $ret != 0 ]; do
    mo2-optimise $CFG
    ret=$?
    if [ $ret = 1 ]; then
	$CONFIGURE $CFG &
    elif [ $ret = 2 ]; then
	wait
    fi
done
