#!/usr/bin/python2.7

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/visualize-gc.py#6 $
# $DateTime: 2013/11/12 19:42:41 $
# $Change: 2030932 $
# $Author: mooreb $

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib.lines as lines
import pylab
import sys
import os
import vmsgcvizutils

def isNetflixInternal():
    try:
        open("/etc/profile.d/netflix_environment.sh", "r")
        return True
    except IOError:
        return False

numArgs = len(sys.argv) - 1
if(2 != numArgs):
    print "Usage: %s now:iso8601timestamp vms-gc-report-directory" % (sys.argv[0],)
    sys.exit(1);

now = sys.argv[1]
vmsGCReportDirectory = sys.argv[2]
gcEventDirectory = vmsGCReportDirectory + os.path.sep + 'gc-events-duration-by-event'

event_to_symbol_and_color = {
"FullGC"                            : ("mD", 15),  #(stop the world)
"concurrent-mode-failure"           : ("rh", 10),  #(stop the world)
"promotion-failed"                  : ("rH", 10),  #(stop the world)
"ParNew"                            : ("ro",  5),  #(stop-the-world)
"CMS-initial-mark"                  : ("r^",  5),  #(stop-the-world)
"CMS-remark"                        : ("rs",  5),  #(stop the world)
"CMS-concurrent-mark"               : ("g,",  1),  #(concurrent includes yields to other theads)
"CMS-concurrent-abortable-preclean" : ("g,",  1),  #(concurrent)
"CMS-concurrent-preclean"           : ("g,",  1),  #(concurrent)
"CMS-concurrent-sweep"              : ("g,",  1),  #(concurrent)
"CMS-concurrent-reset"              : ("g,",  1),  #(concurrent?)
"ParallelScavengeYoungGen"          : ("ro",  5),  #(stop-the-world)
"DefNew"                            : ("ro",  5),  #(stop-the-world)
"unknown"                           : ("r*",  15), #???
}

# These markers are present in gc.log but not accounted for above as they have no duration.
# They might be interesting to visualize but we currently minimize the CMS events anyway.
#   CMS-concurrent-mark-start
#   CMS-concurrent-preclean-start
#   CMS-concurrent-sweep-start
#   CMS-concurrent-reset-start
#   CMS-concurrent-abortable-preclean-start

## Read environmental information
def getSmallEnvDict():
    try:
        fullEnvDict = vmsgcvizutils.envFileAsDictionary(vmsGCReportDirectory + os.path.sep + 'env')
    except:
        fullEnvDict = {}
    smallEnvDict = {
        'ec2PublicHostname' : fullEnvDict.get('EC2_PUBLIC_HOSTNAME', 'no-public-hostname'),
        'instanceID'        : fullEnvDict.get('EC2_INSTANCE_ID', 'no-instance-id'),
        'instanceType'      : fullEnvDict.get('EC2_INSTANCE_TYPE', 'no-instance-type'),
        'appname'           : fullEnvDict.get('NETFLIX_APP', 'unknown-app'),
        'asg'               : fullEnvDict.get('NETFLIX_AUTO_SCALE_GROUP', 'unknown-asg'),
        'env'               : fullEnvDict.get('NETFLIX_ENVIRONMENT', 'unknown-env'),
    }
    return smallEnvDict
    

## Read GC event records, one file per type.
# The gc event records have this format:
#   secs_since_epoch,datetimestamp,secs_since_jvm_boot,gc_event_type,gc_event_duration_in_seconds
# for example:
#   1333055023.424,2012-03-29T21:03:43.424+0000,11.272,ParNew,0.19
# in numpy-speak:
#   dtype=[('secs_since_epoch', '<f8'), ('datetimestamp', '|O4'), ('secs_since_jvm_boot', '<f8'), ('gc_event_type', '|S33'), ('gc_event_duration_in_seconds', '<f8')])

dirList=os.listdir(gcEventDirectory)
recordsets = []
maxGCEventDuration = 0.0
maxSTWGCEventDuration = 0.0
for fname in dirList:
    fnameFullPath = gcEventDirectory + os.path.sep + fname
    print 'Reading %s' % (fnameFullPath,)
    (color, markersize) = event_to_symbol_and_color[fname]
    recordset = mlab.csv2rec(fnameFullPath)
    thisRecordsetMax = max(recordset.gc_event_duration_in_seconds)
    maxGCEventDuration = max(maxGCEventDuration, thisRecordsetMax)
    if color.startswith('r') or color.startswith('m'):
        maxSTWGCEventDuration = max(maxSTWGCEventDuration, thisRecordsetMax)
    mpldatenums = mdates.epoch2num(recordset.secs_since_epoch)
    tuple = (fname, recordset, mpldatenums, color, markersize)
    recordsets.append(tuple)

## Plot the GC event records
# example plots in:
#   http://matplotlib.sourceforge.net/gallery.html
#
# this one is particularly good:
#   http://matplotlib.sourceforge.net/examples/pylab_examples/usetex_demo.html
# BUG: add multiple plots. example in:
#   http://matplotlib.sourceforge.net/examples/pylab_examples/anscombe.html

fig = plt.figure()
# 1x1 grid = 1 row, 1 column. 2x3 grid = 2 rows, 3 columns. The third number starts from 1 and increments row-first. See documentation of subplot() for more info.
ax = fig.add_subplot(111)
locator = mdates.AutoDateLocator()
formatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%SZ')
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)

for (dataname, dataset, mpldatenums, color, markersize) in recordsets:
    ax.plot(mpldatenums, dataset.gc_event_duration_in_seconds, color, label=dataname, ms=markersize, lw=markersize)

# draw the most recent jvm boot time line
fp = open(vmsGCReportDirectory + os.path.sep + 'jvm_boottime.epoch')
jvmBootEpoch = fp.readline()
jvmBootEpoch = jvmBootEpoch.rstrip('\r\n')
jvmBootDays = mdates.epoch2num(long(jvmBootEpoch))
jvmBootLine = lines.Line2D([jvmBootDays,jvmBootDays], [0,maxGCEventDuration], label='jvm boot time', linewidth=2)
ax.add_line(jvmBootLine)
fp.close()
fp = open(vmsGCReportDirectory + os.path.sep + 'jvm_boottime')
jvmBootTimestamp = fp.readline()
jvmBootTimestamp = jvmBootTimestamp.rstrip('\r\n')
fp.close()

# draw the vms cache refresh event lines if we're inside netflix
def try_to_draw_vms_cache_refresh_lines():
    if(isNetflixInternal()):
        try:
            fp = open(vmsGCReportDirectory + os.path.sep + 'vms-cache-refresh-overall-events-milliseconds')
        except IOError:
            return
        for line in fp:
            line = line.rstrip('\r\n')
            try:
                (finish_time_ms_str, duration_ms_str) = line.split()
            except ValueError:
                continue
            finish_time_ms = long(finish_time_ms_str)
            duration_ms = long(duration_ms_str)
            start_time_ms = finish_time_ms - duration_ms
            start_time_secs = start_time_ms/1000.0
            start_time_days = mdates.epoch2num(start_time_secs)
            start_time_line = lines.Line2D([start_time_days,start_time_days], [0,maxGCEventDuration], color='r')
            ax.add_line(start_time_line)
            finish_time_secs = finish_time_ms/1000.0
            finish_time_days = mdates.epoch2num(finish_time_secs)
            finish_time_line = lines.Line2D([finish_time_days,finish_time_days], [0,maxGCEventDuration], color='c')
            ax.add_line(finish_time_line)
        fp.close()
        # draw some fake lines just to get them into the legend
        fake_vms_start_line = lines.Line2D([jvmBootDays,0], [jvmBootDays,0], label='VMS cache refresh start', color='r')
        fake_vms_end_line = lines.Line2D([jvmBootDays,0], [jvmBootDays,0], label='VMS cache refresh end', color='c')
        ax.add_line(fake_vms_start_line)
        ax.add_line(fake_vms_end_line)

try_to_draw_vms_cache_refresh_lines()

# various chart options
smallEnvDict = getSmallEnvDict()
ax.set_title('gc events over time for %s %s %s %s %s %s' % (smallEnvDict['appname'], smallEnvDict['env'], smallEnvDict['ec2PublicHostname'], smallEnvDict['instanceID'], smallEnvDict['instanceType'], smallEnvDict['asg']))
ax.grid(True)
ax.set_xlabel('gc event start timestamp')
ax.set_ylabel('gc event duration (seconds)')
fig.autofmt_xdate()
plt.ylim([0,maxSTWGCEventDuration])
fig.set_size_inches(21,12)
pylab.figlegend(*ax.get_legend_handles_labels(), loc='lower center', ncol=5)

# BUG: add sar charts, including but not limited to cpu, network
# BUG: plot secs since jvm start
# BUG: visualize the facet data collected in vms-cache-refresh-facet-info.csv. Maybe leave this up to visualize-instance.

savedImageBaseFileName = vmsGCReportDirectory + os.path.sep + smallEnvDict['appname'] + '-gc-events-' + now
savedIamgeFileName = savedImageBaseFileName + '.png'
plt.savefig(savedIamgeFileName)
print "output on %s" % (savedIamgeFileName,)
savedIamgeFileName = savedImageBaseFileName + '.pdf'
plt.savefig(savedIamgeFileName)
print "output on %s" % (savedIamgeFileName,)

# Potential BUG: do we want to issue the plt.show()
plt.show()


heapSizesFileName = vmsGCReportDirectory + os.path.sep + 'gc-sizes.csv'
heapSizesRecordSet = mlab.csv2rec(heapSizesFileName)
heapSizesFig = plt.figure()
heapSizesAx = heapSizesFig.add_subplot(111)
heapSizesLocator = mdates.AutoDateLocator()
heapSizesFormatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%SZ')
heapSizesAx.xaxis.set_major_locator(heapSizesLocator)
heapSizesAx.xaxis.set_major_formatter(heapSizesFormatter)

ONE_K   = 1024.0
ONE_MEG = 1024.0*1024.0
ONE_GIG = 1024.0*1024.0*1024.0

whole_heap_end_k_max = heapSizesRecordSet.whole_heap_end_k.max()
whole_heap_end_bytes_max = whole_heap_end_k_max* 1024.0

if (whole_heap_end_bytes_max < ONE_MEG):
    heap_end_units = "kilobytes"
    whole_heap_end = heapSizesRecordSet.whole_heap_end_k
elif ((ONE_MEG <= whole_heap_end_bytes_max) and (whole_heap_end_bytes_max < ONE_GIG)):
    heap_end_units = "megabytes"
    whole_heap_end = heapSizesRecordSet.whole_heap_end_k / ONE_K
elif (ONE_GIG <= whole_heap_end_bytes_max):
    heap_end_units = "gigabytes"
    whole_heap_end = heapSizesRecordSet.whole_heap_end_k / ONE_MEG
else:
    raise Exception("did not expect to get here")

heapSizesAx.plot(mdates.epoch2num(heapSizesRecordSet.secs_since_epoch), whole_heap_end, 'o')
heapSizesFig.autofmt_xdate()
heapSizesAx.set_title('heap size over time for %s %s %s %s %s %s' % (smallEnvDict['appname'], smallEnvDict['env'], smallEnvDict['ec2PublicHostname'], smallEnvDict['instanceID'], smallEnvDict['instanceType'], smallEnvDict['asg']))
heapSizesAx.grid(True)
heapSizesAx.set_xlabel('time')
heapSizesAx.set_ylabel('Total Heap Size After Collection (%s)' % (heap_end_units,))

heapSizesFig.set_size_inches(21,12)
heapSizesSavedImageBaseName = vmsGCReportDirectory + os.path.sep + smallEnvDict['appname'] + '-heap-size-' + now
fname = heapSizesSavedImageBaseName + '.png'
plt.savefig(fname)
print 'output on ' + fname
fname = heapSizesSavedImageBaseName + '.pdf'
plt.savefig(fname)
print 'output on ' + fname
plt.show()
