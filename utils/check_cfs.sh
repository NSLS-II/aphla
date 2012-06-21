#!/bin/bash


for cfs_res in "tags" "properties"
do
    echo "### Checking Channel Finder '${cfs_res}'@${HLA_CFS_URL}"

    curl -s ${HLA_CFS_URL}/resources/${cfs_res} | python -c "import sys;from lxml import etree;print etree.tostring(etree.fromstring(sys.stdin.read()),pretty_print=True)"
done

