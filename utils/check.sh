#!/bin/bash

#export EPICS_CA_ADDR_LIST=controldev32.nsls2.bnl.gov
export EPICS_CA_MAX_ARRAY_BYTES=100000

echo "Using EPICS_CA_ADDR_LIST=${EPICS_CA_ADDR_LIST}"

caget 'SR:C00-BI:G00<DCCT:00>CUR-RB'


caget 'SR:C00-Glb:G00<TUNE:00>RB-Y'
caget "SR:C00-Glb:G00<TUNE:00>RB-X"
caget "SR:C00-Glb:G00<ORBIT:00>RB-X"
caget "SR:C00-Glb:G00<ORBIT:00>RB-Y"
