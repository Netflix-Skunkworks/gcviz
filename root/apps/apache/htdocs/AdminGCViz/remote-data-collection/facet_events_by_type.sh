#!/bin/bash

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/facet_events_by_type.sh#2 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
# $Author: mooreb $

if [ -z "$1" ]; then
    echo Usage: $0 output-dir
    exit 1
fi

OUTPUTDIR=$1
OUTDIR=${OUTPUTDIR}/facet-events-by-cache
INFILE=${OUTPUTDIR}/vms-cache-refresh-facet-info.csv
mkdir -p ${OUTDIR}
EVENT_TYPES=`awk -F, '{print $4}' ${INFILE} | sort -u | grep -v cache`
echo event_Types is ${EVENT_TYPES}
for e in ${EVENT_TYPES};
do
    echo egrep -e ${e} -e seconds_since_epoch ${INFILE} \> ${OUTDIR}/${e}
    egrep -e ${e} -e seconds_since_epoch ${INFILE} > ${OUTDIR}/${e}
done
