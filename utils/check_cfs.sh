#!/bin/bash

#export HLA_CFS_URL="http://web01.nsls2.bnl.gov:8080/ChannelFinder"
export HLA_CFS_URL="http://channelfinder.cs.nsls2.local/ChannelFinder"

for cfs_res in "tags" "properties"
do
    echo "### Checking Channel Finder '${cfs_res}'@${HLA_CFS_URL}"

    curl -s ${HLA_CFS_URL}/resources/${cfs_res} | python -c "import sys;from lxml import etree;print etree.tostring(etree.fromstring(sys.stdin.read()),pretty_print=True)"
done

download_cfs()
{
  query="$1"
  output=$2
  URL="${HLA_CFS_URL}/resources/channels?${query}"
  echo "# from ${URL}"
  curl -s ${URL} |  python -c "import sys;from lxml import etree;print etree.tostring(etree.fromstring(sys.stdin.read()),pretty_print=True)" > ${output}
}

timestamp=`date +%Y%m%d_%H%M%S`
echo "# downloading name=*"
download_cfs "~name=*" "cfs_nsls2_${timestamp}_all.xml"

echo "# downloading name=*1-SR*"
download_cfs "~name=*1-SR*" "cfs_nsls2_${timestamp}_1sr.xml"

echo "# downloading system=V1*"
download_cfs "system=V1*" "cfs_nsls2_${timestamp}_v1.xml"

echo "# downloading aphla"
download_cfs "~tag=aphla.*" "cfs_nsls2_${timestamp}_aphla.xml"



