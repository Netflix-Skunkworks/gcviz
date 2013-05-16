#!/bin/sh

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/collect_remote_data.sh#5 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
# $Author: mooreb $

# This script must be run on the instance where the gc.log and catalina.out must be analyzed.

NFENV=/etc/profile.d/netflix_environment.sh
if [ -f ${NFENV} ]; then
    . ${NFENV}
else
    NFENV=""
fi

# NOW=`date +%Y-%m-%dT%T`
if [ -z "$1" ]; then
    echo Usage: $0 {iso8601 combined date and time representation} [ options ... ]
    echo "  where options are: [no]jmap_histo_live [no]vms_refresh_events ... (absence implies the option is on)"
    exit 1
fi
NOW=$1

# start processing optional arguments
if [ -z "$2" ]; then
    jmap_histo_live=true
    vms_refresh_events=true
else
    shift
    while [ $# -gt 0 ];
    do
        case "$1" in 
            nojmap_histo_live)
                jmap_histo_live=false
                ;;
            jmap_histo_live)
                jmap_histo_live=true
                ;;
            novms_refresh_events)
                vms_refresh_events=false
                ;;
            vms_refresh_events)
                vms_refresh_events=true
                ;;
        esac
        shift
    done
fi


# Potential BUG: this assumes tomcat. It might be better to use jps, but the corresponding jps expression:
#   JAVAPID=`jps | grep Bootstrap | awk '{print $1}'`
# doesn't seem much (any?) better
JAVAPID=`ps -elfww | grep java | grep Bootstrap | grep -v grep | awk '{print $4}'`
if [ -z "${JAVAPID}" ]; then
    echo CANNOT DETERMINE JAVAPID. EXITING.
    exit 1
fi

JAVACMDLINE=`cat /proc/${JAVAPID}/cmdline`
# This does not work due to crontabs or other programs (or users!) being able to touch files in /proc
# BOOTTIME=`ls --full-time /proc/${JAVAPID}/cmdline | awk '{print $6,$7,$8}' | sed 's/[.][0-9][0-9]*//' | sed 's/ /T/' | sed 's/ //'`
BOOTTIME_LOCAL=`ps h -p ${JAVAPID} -o lstart`
BOOTTIME=`date --date="${BOOTTIME_LOCAL}" "+%Y-%m-%dT%T+0000"`

RDCS=/apps/apache/htdocs/AdminGCViz/remote-data-collection
OUTPUTROOT=/mnt/logs/gc-reports
OUTPUTDIR=${OUTPUTROOT}/${NOW}

echo making output directories
mkdir -p ${OUTPUTDIR}/raw-gc-data
mkdir -p ${OUTPUTDIR}/raw-sar-data

if [ "true" = "$jmap_histo_live" ]; then
    echo 'getting jmap -histo:live logs'
    mkdir -p /apps/tomcat/logs/jmap-histos
    jmap -histo:live ${JAVAPID} > /apps/tomcat/logs/jmap-histos/jmap-histo-live-`date +%Y-%m-%d--%H-%M-%S` 2>&1
    cp -ar /apps/tomcat/logs/jmap-histos ${OUTPUTDIR}
fi

echo copying gc logs
cp -a /apps/tomcat/logs/archive/*gc.log* /apps/tomcat/logs/gc.log ${OUTPUTDIR}/raw-gc-data
for f in `ls ${OUTPUTDIR}/raw-gc-data`
do
    g=${OUTPUTDIR}/raw-gc-data/${f}
    if [ "$(tail -c 1 ${g})" != "" ]; then
        echo >> ${g}
    fi
done

echo processing gc logs
cat ${OUTPUTDIR}/raw-gc-data/*tomcat_gc.log* ${OUTPUTDIR}/raw-gc-data/gc.log | tr -d '\000' | perl -w ${RDCS}/gcdotlog_one_event_per_line.pl > ${OUTPUTDIR}/gc-events-one-per-line
cat ${OUTPUTDIR}/gc-events-one-per-line | python ${RDCS}/gcdotlog_convert_relative_into_absolute_time.py ${BOOTTIME} ${OUTPUTDIR} > ${OUTPUTDIR}/gc-events-one-per-line-in-absolute-time
cat ${OUTPUTDIR}/gc-events-one-per-line-in-absolute-time | perl -w ${RDCS}/gcdotlog_extract_time.pl ${OUTPUTDIR} > ${OUTPUTDIR}/gc-events-duration-in-seconds-only
cat ${OUTPUTDIR}/gc-events-duration-in-seconds-only |grep -v secs_since_jvm_boot | awk -F, '{print $1}' | python ${RDCS}/prepend_epoch.py > /tmp/epochs
paste --delim=, /tmp/epochs ${OUTPUTDIR}/gc-events-duration-in-seconds-only > /tmp/foo
mv /tmp/foo ${OUTPUTDIR}/gc-events-duration-in-seconds-only
bash ${RDCS}/gc_events_by_type.sh ${OUTPUTDIR}
cat ${OUTPUTDIR}/gc-events-one-per-line-in-absolute-time | perl -w ${RDCS}/gcdotlog_extract_sizes.pl ${OUTPUTDIR} > ${OUTPUTDIR}/gc-sizes.csv
cat ${OUTPUTDIR}/gc-sizes.csv |grep -v secs_since_jvm_boot | awk -F, '{print $1}' | python ${RDCS}/prepend_epoch.py > /tmp/epochs
paste --delim=, /tmp/epochs ${OUTPUTDIR}/gc-sizes.csv > /tmp/foo
mv /tmp/foo ${OUTPUTDIR}/gc-sizes.csv
rm /tmp/epochs

if [ -n "${NFENV}" ] && [ "true" = "$vms_refresh_events" ]; then
    echo looking for vms refresh events
    grep --no-filename vms-refreshexecutor /apps/tomcat/logs/archive/*catalina.out* /apps/tomcat/logs/catalina.out  | egrep -e RefreshStat: -e 'Refreshing caches for country' > ${OUTPUTDIR}/vms-cache-refresh-events
    grep -o 'CacheRefresh:[0-9][0-9]*' ${OUTPUTDIR}/vms-cache-refresh-events  | awk -F : '{print $2}' > ${OUTPUTDIR}/vms-cache-refresh-events-milliseconds
    grep --no-filename CacheManagerStats /apps/tomcat/logs/archive/*catalina.out* /apps/tomcat/logs/catalina.out  | grep RefreshStat: | grep OVERALL > ${OUTPUTDIR}/vms-cache-refresh-overall-events
    grep -o 'CacheRefresh:[0-9][0-9]*.*duration:[0-9][0-9]*' ${OUTPUTDIR}/vms-cache-refresh-overall-events | awk '{print $1,$7}' | awk -F : '{print $2,$3}' | awk '{print $1,$3}' > ${OUTPUTDIR}/vms-cache-refresh-overall-events-milliseconds

    echo looking for vms facet info
    grep --no-filename BaseManager /apps/tomcat/logs/archive/*catalina.out* /apps/tomcat/logs/catalina.out | grep CacheRefreshInfo: > ${OUTPUTDIR}/vms-cache-refresh-facet-info
    awk '{print $1,$2,$8,$9,$11,$12,$13,$14}' ${OUTPUTDIR}/vms-cache-refresh-facet-info | python ${RDCS}/vms_facet_info_transform.py > ${OUTPUTDIR}/vms-cache-refresh-facet-info.csv 2> ${OUTPUTDIR}/vms-cache-refresh-facet-info-rejected-lines
    bash ${RDCS}/facet_events_by_type.sh ${OUTPUTDIR}
    bash ${RDCS}/facet_events_by_country.sh ${OUTPUTDIR}

    echo looking for vms objectCache stats
    egrep --no-filename -r -e VMClientCacheManager -e objectCache /apps/tomcat/logs/archive/*catalina.out* /apps/tomcat/logs/catalina.out | egrep -e Processed -e objectCache > ${OUTPUTDIR}/vms-object-cache-stats
    python ${RDCS}/process_vms_object_cache_stats.py ${OUTPUTDIR}/vms-object-cache-stats ${OUTPUTDIR}
fi

echo grabbing environment
cat /proc/${JAVAPID}/cmdline | tr '\000' '\n' >  ${OUTPUTDIR}/cmdline
echo ${BOOTTIME} > ${OUTPUTDIR}/jvm_boottime
env | LANG=C sort > ${OUTPUTDIR}/env
md5sum /apps/tomcat/webapps/ROOT/WEB-INF/lib/* | LANG=C sort -k2 > ${OUTPUTDIR}/web-inf-lib
/proc/${JAVAPID}/exe -version > ${OUTPUTDIR}/java-version 2>&1
cat /proc/${JAVAPID}/maps > ${OUTPUTDIR}/maps
python ${RDCS}/parse-proc-pid-maps.py ${OUTPUTDIR}/maps > ${OUTPUTDIR}/maps-parsed
cat /proc/meminfo > ${OUTPUTDIR}/meminfo
cat /proc/cpuinfo > ${OUTPUTDIR}/cpuinfo
free -m > ${OUTPUTDIR}/free-m

if [ -n "${NFENV}" ]; then
    echo grabbing netflix-specific environment
    find /apps/tomcat/webapps/ROOT/WEB-INF/classes -name "*.properties" -exec grep videometadata /dev/null {} \; > ${OUTPUTDIR}/videometadata-properties 2> /dev/null
    rpm -q ${NETFLIX_APP} > ${OUTPUTDIR}/netflix-rpm-version
    rpm -qa | LANG=C sort > ${OUTPUTDIR}/netflix-rpm-all-packages-versions
fi

echo collecting sar data
for f in `ls /var/log/sa/ | grep ^sa | grep -v sar`; do sar -f /var/log/sa/${f} > ${OUTPUTDIR}/raw-sar-data/sar-cpu-${f}; done
for f in `ls /var/log/sa/ | grep ^sa | grep -v sar`; do sar -n ALL -f /var/log/sa/${f} > ${OUTPUTDIR}/raw-sar-data/sar-network-${f}; done

# BUG: fix this implicit agreement between collect_remote_data.sh and visualize-instance.sh
# echo bundling up results
# tar -C ${OUTPUTROOT} -zcf ${OUTPUTDIR}.tar.gz ${NOW}
