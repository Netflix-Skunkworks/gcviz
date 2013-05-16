#!/usr/bin/python2.7

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/parse-proc-pid-maps.py#2 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
# $Author: mooreb $

import sys

def bytesToHumanReadable(n):
    kay = 1024
    meg = kay*1024
    gig = meg*1024
    if ((0 <= n) and (n < kay)):
        return "%d bytes" % n
    elif ((kay <= n) and (n < meg)):
        return "%.2fkb" % ((n+0.0)/kay)
    elif ((meg <= n) and (n < gig)):
        return "%.2fmb" % ((n+0.0)/meg)
    else:
        return "%.2fgb" % ((n+0.0)/gig)

def readfile(filename):
    segments = []
    numSegments=0L
    totalBytes=0L
    infile = open(filename, 'r')
    line = infile.readline()
    while line:
        line = line.rstrip()
        fields = line.split(None, 5)
        if 6 == len(fields):
            (memRange, perms, offset, dev, inode, pathname) = fields
        elif 5 == len(fields):
            (memRange, perms, offset, dev, inode) = fields
            pathname = ''
        else:
            raise Exception('cannot unpack %s' % (line,))
        (begin,end) = memRange.split('-')
        t = long(end, 16) - long(begin, 16)
        totalBytes = totalBytes + t
        numSegments = numSegments + 1
        x = (t, memRange, pathname)
        segments.append(x)
        line = infile.readline()
    print filename
    print "\tnum segments = %s" % (numSegments,)
    print "\ttotal bytes = %s (%s)" % (totalBytes, bytesToHumanReadable(totalBytes))
    for i in sorted(segments, key=lambda x: x[0], reverse=True):
        print "\t\t%12s bytes (%s) %33s %s" % (i[0], bytesToHumanReadable(i[0]), i[1], i[2])

readfile(sys.argv[1])
