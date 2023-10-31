#!/usr/bin/bash

usage() { echo "Usage: $0 [-d]" 1>&2; exit 1; }
while getopts ":d:" o; do
    case "${o}" in
	d)
	    dummy=${OPTARG}
	    ;;
        *)
            usage
            ;;
    esac
done

if [ -z "$dummy" ]; then
    dummy=$(which dummy)
    if [ -z "$dummy" ]; then
	echo "could not find dummy binary in your path"
	echo "set your path or use command line option"
	usage
    fi
fi
if [ ! -e "$dummy" ]; then
   echo "no such file $dummy"
   usage
fi
   
target=~/cylc-src/modelopt2
srcdir=$(dirname $0)

mkdir -p ${target}/bin
cp ${srcdir}/flow.cylc ${srcdir}/modelopt.cfg $target
cp ${dummy} ${target}/bin
cp -r ${srcdir}/dummy $target
