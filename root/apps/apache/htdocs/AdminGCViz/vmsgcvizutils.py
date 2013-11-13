#!/usr/bin/python2.7

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/vmsgcvizutils.py#3 $
# $DateTime: 2013/11/12 19:42:41 $
# $Change: 2030932 $
# $Author: mooreb $

import calendar
import math
import time
import re

def timestamp_to_epoch(timeStringISO8601):
    # Potential BUG: +0000 is hardcoded. I'd like to use %z but
    # cannot, as it's not supported by time.strptime and there's no
    # easy workaround: http://wiki.python.org/moin/WorkingWithTime
    secondFractionPattern = re.compile('([.][0-9]+)[+]0000')
    match = secondFractionPattern.search(timeStringISO8601)
    if match:
        fraction = match.group(1)
    else:
        fraction = ""
    timeStringISO8601 = timeStringISO8601.replace(fraction, '')
    # Potential BUG: +0000 is hardcoded. I'd like to use %z but
    # cannot, as it's not supported by time.strptime and there's no
    # easy workaround: http://wiki.python.org/moin/WorkingWithTime
    bootTimeTuple = time.strptime(timeStringISO8601, "%Y-%m-%dT%H:%M:%S+0000")
    bootTimeSecondsSinceEpoch = "%s" % calendar.timegm(bootTimeTuple)
    return (bootTimeSecondsSinceEpoch + fraction)

def convertTimeStamp(absoluteBaselineTime, secondsAfterBaseline):
    offsetTime = absoluteBaselineTime + secondsAfterBaseline
    offsetTimeTuple = time.gmtime(offsetTime)
    # Potential BUG: +0000 is hardcoded. I'd like to use %z but
    # cannot, as it's not supported by time.strptime and there's no
    # easy workaround: http://wiki.python.org/moin/WorkingWithTime
    offsetTimeString = time.strftime("%Y-%m-%dT%H:%M:%S+0000", offsetTimeTuple)
    fractionSecondsString = '%.3f' % (secondsAfterBaseline - math.floor(secondsAfterBaseline))
    retval = offsetTimeString.replace('+', fractionSecondsString[1:] + '+')
    return retval


def envFileAsDictionary(fname):
    retval = {}
    fp = open(fname, 'r')
    for line in fp:
        line = line.rstrip('\r\n')
        try:
            (k, v) = line.split('=', 1)
        except ValueError:
            continue
        retval[k] = v
    return retval
