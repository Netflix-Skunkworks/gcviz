#!/usr/bin/python2.7

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/process_vms_object_cache_stats.py#2 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
# $Author: mooreb $

import fileinput
import os
import re
import sys

# Ugh.
sys.path.insert(0, "/apps/apache/htdocs/AdminGCViz")
import vmsgcvizutils   

numArgs = len(sys.argv) - 1
if(2 != numArgs):
    print "Usage: %s object-cache-stats-file outputdir" % (sys.argv[0],)
    sys.exit(1);

objectCacheStatsFile = sys.argv[1]
baseOutputDir = sys.argv[2]
outputDir = baseOutputDir + os.path.sep + 'vms-object-cache-stats-by-cache'
os.mkdir(outputDir)
outputFiles = {}
rejects = open(objectCacheStatsFile + '.rejects', 'w')

timestampPattern = re.compile('^([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2}:[0-9]{2}),([0-9]{3}) INFO (main|vms-timer-refresh) VMClientCacheManager - Processed Countries')
objectCachePattern = re.compile('objectCache\(([^)]*)\) references\(([^)]*)\) size\(([^)]*)\) ratio\(([^)]*)\) prevsize\(([^)]*)\) additions\(([^)]*)\) transfers\(([^)]*)\) hits\(([^)]*)\) orphans\(([^)]*)\)')

header="secsSinceEpoch,iso8601Timestamp,references,size,ratio,prevsize,additions,transfers,hits,orphans\n"

iso8601Timestamp = "1970-01-01T00:00:00.000+0000"
secsSinceEpoch = "0.000"
for line in fileinput.input(objectCacheStatsFile):
    line = line.rstrip('\r\n')
    foundTimestamp = timestampPattern.search(line)
    if foundTimestamp:
        ymd = foundTimestamp.group(1)
        hms = foundTimestamp.group(2)
        milliseconds = foundTimestamp.group(3)
        iso8601Timestamp = '%sT%s.%s+0000' % (ymd,hms,milliseconds)
        secsSinceEpoch = vmsgcvizutils.timestamp_to_epoch(iso8601Timestamp)
        continue

    foundObjectCache = objectCachePattern.search(line)
    if foundObjectCache:
        cacheName  = foundObjectCache.group(1)
        references = foundObjectCache.group(2)
        size       = foundObjectCache.group(3)
        ratio      = foundObjectCache.group(4)
        prevsize   = foundObjectCache.group(5)
        additions  = foundObjectCache.group(6)
        transfers  = foundObjectCache.group(7)
        hits       = foundObjectCache.group(8)
        orphans    = foundObjectCache.group(9)
        l = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (secsSinceEpoch,iso8601Timestamp,references,size,ratio,prevsize,additions,transfers,hits,orphans)
        f = outputFiles.get(cacheName)
        if f:
            f.write(l)
        else:
            f = open(outputDir + os.path.sep + cacheName, 'w')
            f.write(header)
            f.write(l)
            outputFiles[cacheName] = f
        continue
    else:
        rejects.write("%s\n" % (line,))

rejects.close()
for fp in outputFiles.values():
    fp.close()
