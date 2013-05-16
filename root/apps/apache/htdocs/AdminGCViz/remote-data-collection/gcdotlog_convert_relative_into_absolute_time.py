#!/usr/bin/python2.7

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/gcdotlog_convert_relative_into_absolute_time.py#2 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
# $Author: mooreb $

import calendar
import fileinput
import math
import os
import sys
import time
import re

# Ugh.
sys.path.insert(0, "/apps/apache/htdocs/AdminGCViz")
import vmsgcvizutils   

def mayne():
    TMPFILE = '/tmp/gcdotlog-relative-time-tmpfile'
    numArgs = len(sys.argv) - 1
    if(2 != numArgs):
        print "Usage: %s {iso8601 combined date and time representations} outputdir" % (sys.argv[0],)
        sys.exit(1);

    bootTimeStringISO8601 = sys.argv[1]
    bootTimeSecondsSinceEpochString = vmsgcvizutils.timestamp_to_epoch(bootTimeStringISO8601)
    bootTimeSecondsSinceEpoch = float(bootTimeSecondsSinceEpochString)
    outputDir = sys.argv[2]
    bootTimeEpochFile = open(outputDir + '/jvm_boottime.epoch', 'w')
    bootTimeEpochFile.write("%s\n" % bootTimeSecondsSinceEpochString)
    bootTimeEpochFile.close()
    
    tmpFile = open(TMPFILE, 'w')
    lineStartsWithFloatingPointNumberPattern = re.compile("^([0-9]+[.][0-9]+): ")
    lastSecsSinceBoot = 0.0;
    for line in fileinput.input('-'):
        line = line.rstrip('\r\n')
        found = lineStartsWithFloatingPointNumberPattern.search(line)
        if found:
            secsSinceBootString = found.group(1)
            secsSinceBoot = float(secsSinceBootString)
            if secsSinceBoot < lastSecsSinceBoot:
                # now we need to truncate the output file, since we have
                # seen a restart; this is not the most recent JVM boot
                tmpFile.close()
                tmpFile = open(TMPFILE, 'w')
            lastSecsSinceBoot = secsSinceBoot
            timeStamp = vmsgcvizutils.convertTimeStamp(bootTimeSecondsSinceEpoch, secsSinceBoot)
            tmpFile.write("%s: %s\n" % (timeStamp, line))
        else:
            tmpFile.write("%s\n" % (line,))

    tmpFile.close()
    for line in fileinput.input(TMPFILE):
        line = line.rstrip('\r\n')
        print "%s" % (line,)

    os.unlink(TMPFILE)

if __name__ == "__main__":
    mayne()
