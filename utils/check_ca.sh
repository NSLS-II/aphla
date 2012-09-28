#!/bin/bash

if [[ "$0" =~ ^/ ]]
then
    SCRIPT_LOCATION=$(readlink -f "$0")
else
    SCRIPT_LOCATION=$(readlink -f "$(pwd)/""$0")
fi
SCRIPT_DIR=$(dirname $SCRIPT_LOCATION)
#echo $SCRIPT_LOCATION
#echo $SCRIPT_DIR
LAT_CONF=${SCRIPT_DIR}/../machine/nsls2/lat_conf_table.txt
PVLST=${SCRIPT_DIR}/../machine/nsls2/pvlist.txt

CANUX=`grep -E 'TUNE.*X' ${LAT_CONF}| awk '{print $2}'`
CANUY=`grep -E 'TUNE.*Y' ${LAT_CONF}| awk '{print $2}'`
CAVX=`grep -E 'ORBIT.*X' ${PVLST}`
CAVY=`grep -E 'ORBIT.*X' ${PVLST}`
CAI=`grep -E 'DCCT.*CUR' ${LAT_CONF}| awk '{print $2}'`

#export EPICS_CA_ADDR_LIST=controldev32.nsls2.bnl.gov
export EPICS_CA_MAX_ARRAY_BYTES=100000

echo "Using EPICS_CA_ADDR_LIST=${EPICS_CA_ADDR_LIST}"

caget $CAI
caget $CAVX
caget $CAVY
caget $CANUX
caget $CANUY


#caget 'SR:C00-Glb:G00<TUNE:00>RB-Y'
#caget "SR:C00-Glb:G00<TUNE:00>RB-X"
#caget "SR:C00-Glb:G00<ORBIT:00>RB-X"
#caget "SR:C00-Glb:G00<ORBIT:00>RB-Y"
