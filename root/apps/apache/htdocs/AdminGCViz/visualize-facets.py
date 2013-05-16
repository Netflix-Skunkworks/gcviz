#!/usr/bin/python2.7

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/visualize-facets.py#2 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
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
from mpl_toolkits.mplot3d import Axes3D

numArgs = len(sys.argv) - 1
if(2 != numArgs):
    print "Usage: %s now:iso8601timestamp vms-gc-report-directory" % (sys.argv[0],)
    sys.exit(1);

now = sys.argv[1]
vmsGCReportDirectory = sys.argv[2]

# seconds_since_epoch,datetimestamp,country,cache,numitems,totalTime,timeToCopyToDisc,timeToFill
# 1333073736.242,2012-03-30T02:15:36.242+0000,BS,VideoEDFulfillmentData,23242,1352,757,595
fnameFullPath = vmsGCReportDirectory + os.path.sep + 'vms-cache-refresh-facet-info.csv'
recordset = mlab.csv2rec(fnameFullPath)

countries = recordset.country
countriesDict = {}
countriesList = []
countryNum = 0
for c in countries:
    cPrime = countriesDict.get(c)
    if cPrime:
        countriesList.append(cPrime)
    else:
        countryNum = countryNum + 1
        countriesDict[c] = countryNum
        countriesList.append(countryNum)

caches = recordset.cache
cachesDict = {}
cachesList = []
cacheNum = 0
for c in caches:
    cPrime = cachesDict.get(c)
    if cPrime:
        cachesList.append(cPrime)
    else:
        cacheNum = cacheNum + 1
        cachesDict[c] = cacheNum
        cachesList.append(cacheNum)

allTimeSpentInAllFacets = 0
perFacetRecordSets = []
facetEventByCacheDir = vmsGCReportDirectory + os.path.sep + 'facet-events-by-cache'
dirList=os.listdir(facetEventByCacheDir)
for fname in dirList:
    fnameFullPath = facetEventByCacheDir + os.path.sep + fname
    r = mlab.csv2rec(fnameFullPath)
    allTimeSpentInFacet = sum(r.totaltime)
    allTimeSpentInAllFacets = allTimeSpentInAllFacets + allTimeSpentInFacet
    timeToCopyFacetToDisc = sum(r.timetocopytodisc)
    timeToFillFacet = sum(r.timetofill)
    d = {'totaltime' : allTimeSpentInFacet, 
         'copytime'  : timeToCopyFacetToDisc,
         'filltime'  : timeToFillFacet,
         'facetName' : fname, 
         'recordset' : r}
    perFacetRecordSets.append(d)
perFacetRecordSets.sort(reverse=True, key=lambda d: d['totaltime']) # sort by all time spent in facet

facetReportFileName = vmsGCReportDirectory + os.path.sep + 'facet-report.txt'
facetReportFP = open(facetReportFileName, 'w')
for r in perFacetRecordSets:
    timeThisFacet = r['totaltime']
    s = '%10s milliseconds spent in %25s (%5.2f%%) {copy: %5.2f%%; fill: %5.2f%%}' % (
        timeThisFacet, 
        r['facetName'], 
        ((timeThisFacet*100.0)/allTimeSpentInAllFacets), 
        (r['copytime']*100.0/allTimeSpentInAllFacets), 
        (r['filltime']*100.0/allTimeSpentInAllFacets),
        )
    facetReportFP.write("%s\n" % (s,))
    print s
facetReportFP.close()

# BUG
sys.exit(0)

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot(countriesList, recordset.totaltime/1000, zs=cachesList, zdir='z', marker='o')

ax.set_xlabel('country')
ax.set_ylabel('time to fill this country/facet (seconds)')
ax.set_zlabel('facet')
ax.set_title('total time to fill each facet for each country')

# BUG: save all generated figures.

plt.show()

# sort by total time descending:
#   sort -t , -k 6 -rn vms-cache-refresh-facet-info.csv | more
