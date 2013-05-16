#!/usr/bin/python2.7

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/vms_facet_info_transform.py#2 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
# $Author: mooreb $

import fileinput
import re

# Ugh.
sys.path.insert(0, "/apps/apache/htdocs/AdminGCViz")
import vmsgcvizutils   

# Input:
# 2012-03-30 00:47:11,771 country(GF) cache(VideoImages) numItems(24189) totalTime(1397531) timeToCopyToDisc(5550) timeToFill(1391981)
# ...
#
# Output
# seconds_since_epoch,datetimestamp,country,cache,numitems,totalTime,timeToCopyToDisc,timeToFill
# 1333068431.771,2012-03-30T00:47:11.771+0000,GF,VideoImages,24189,1397531,5550,1391981
# ...

facetPattern = re.compile('^([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2}:[0-9]{2}),([0-9]{3}) country\(([A-Z]{2})\) cache\(([^)]+)\) numItems\(([0-9]+)\) totalTime\(([0-9]+)\) timeToCopyToDisc\(([0-9]+)\) timeToFill\(([0-9]+)\)$')

print 'seconds_since_epoch,datetimestamp,country,cache,numitems,totalTime,timeToCopyToDisc,timeToFill'
for line in fileinput.input('-'):
    line = line.rstrip('\r\n')
    found = facetPattern.search(line)
    if found:
        ymd = found.group(1)
        hms = found.group(2)
        milliseconds = found.group(3)
        iso8601Timestamp = '%sT%s.%s+0000' % (ymd,hms,milliseconds)
        secsSinceEpoch = vmsgcvizutils.timestamp_to_epoch(iso8601Timestamp)
        country = found.group(4)
        cache = found.group(5)
        numItems = found.group(6)
        totalTime = found.group(7)
        timeToCopyToDisc = found.group(8)
        timeToFill = found.group(9)
        print '%s,%s,%s,%s,%s,%s,%s,%s' % (secsSinceEpoch, iso8601Timestamp, country, cache, numItems, totalTime, timeToCopyToDisc, timeToFill)
    else:
        sys.stderr.write(line)
