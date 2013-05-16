#!/usr/bin/python2.7

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/prepend_epoch.py#2 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
# $Author: mooreb $

import fileinput
import sys

# Ugh.
sys.path.insert(0, "/apps/apache/htdocs/AdminGCViz")
import vmsgcvizutils   

def mayne():
    print "secs_since_epoch"
    for line in fileinput.input('-'):
        line = line.rstrip('\r\n')
        print "%s" % (vmsgcvizutils.timestamp_to_epoch(line),)

if __name__ == "__main__":
    mayne()
