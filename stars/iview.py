"""
Interaction classes for views 
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@sourceforge.net
            Mark V. Janikas mjanikas@sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

Implements signature model for interactivity in STARS. 

The signature model provides information on the Observation associated with a
particular entity in a view. This provides a separation of the job of drawing
statistical and geographical Views (which is handled by gView.py and gui.py)
from that of determining what the underling objects are represented by
graphical objects (i.e., the underlying data structures of STARS).

Each View will provide a graphical depiction of one or more Observation
objects. The View should only be responsible for drawing, highlighting and
receiving user interaction. IView serves as a broker between the View and the
underlying data in STARS. In other words, a user selecting a polygon on a Map
results in Map highlighting that polygon (for example). Map then interacts
with IMap (a subclass of IView) to determine what real world observations in
the data are associated with this polygon. IView interactions with the
Observation objects that it manages.

"""

from numpy.oldnumeric import *
from numpy.oldnumeric.mlab import *
import classifier
from pdf import *
import sets

class Observation:
    """
    Signature for the temporal, spatial and value attributes for data point.
    """
    def __init__(self,ts=None,cs=None,variable=None,value=None):
        """
        ts (list) : integers corresponding to time series coordinates.
        cs (list): integers corresonding to cross-sectional identifiers.
        variable (list): variable names associated with data point.
        value (list): float-integer for value attributes.
        """
        self.ts = ts
        self.cs = cs
        self.variable = variable
        self.value = value
        # the following will allow for general seaching of one or more
        # dimensions. see ITable
        dimensions = {}
        dimensions['cs'] = cs
        dimensions['ts'] = ts
        dimensions['var'] = variable
        self.dimensions = dimensions


    def summary(self):
        """
        Prints information on the cross-sectional and time signatures of the
        observation.
        """
        print 'cs entity',self.cs
        print 'ts entity', self.ts

class IView:
    """
    Serves as an intermediate abstraction layer between the data in STARS and
    the graphical Views the data is portrayed on. 

    Superclass to specific subclasses of Views.
    """
    def __init__(self):
        self.observations = []
        self.selected = []
        self.t = []
        self.cs = []
        self.variable = []
        self.selected = []

    def select(self,obsIds=[]):
        """
        Add the list of observation Ids to the list of currently selected
        observation ids.

        obsIds (list): of integer Observation Ids.
        """
        for id in obsIds:
                if id not in self.selected:
                    self.selected.append(id)
                else:
                    self.deselect([id])

    def deselect(self,obsIds=[]):
        """
        Remove particular (or all) Ids from the currently selected obseration
        Ids.

        obsIds (list): of integer Observation ids.
        """
        if obsIds:
            for id in obsIds:
                self.selected.remove(id)
        else:
            self.selected=[]

    def newSelect(self,obsIds):
        """
        Clears current selection set and selects ObsIds.

        obsIds (list): of integer Observation Ids.
        """
        self.deselect()
        self.select(obsIds)

    def selectSingle(self,obsId):
        """
        Add a single observation Id to the selected set

        obsId (integer): Observation Id.
        """
        self.selected.append(obsId)

    def highlight(self):
        """
        Highligt selected observation Ids.

        Needs to be implemented in subclass.
        """
        raise NotImplementedError

    def brush(self,observations=[]):
        """
        Start brushing on observations.

        observations (list): integer Observation Ids.
        """
        if observations:
            self.select(observations)
        self.highlight()

    def getSelected(self):
        """
        Accessor for observations currently selected.

        Returns list of Observation objects that are currently selected.
        """
        return [self.observations[x] for x in self.selected]

    def matchObservations(self,otherViewObservations):
        """
        Find Observations in our View that have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.

        Needs to be implemented in Subclass.
        """
        raise NotImplementedError

    def getObsforIds(self,ids):
        """
        Find the Observation objects associated with particular ids.

        ids (list): of Observation Ids

        returns (list): of Observation objects.
        """
        matched = []
        for id in ids:
            if id in self.observationKeys:
                matched.append(self.observations[id])
        return matched

class IBox(IView):
    """
    Box Plot specific interaction methods
    """
    def __init__(self,variable,values,csids,tsids,fence=1.5):
        """
        variable (string): name of variable
        values (list): values to plot XXX looks like assumed to be cs?
        csids (list): cross-sectional Ids
        tsids (list): time series Ids
        fence (float): length of fence in boxplot
        """
        IView.__init__(self)
        n = len(values)
        rangen = range(n)
        self.singleCs = 0
        self.singleTs = 0
        self.rangen = rangen
        self.cs = csids
        self.ts = tsids
        if len(csids) == 1:
            csids = [ csids[0] for i in rangen ]
            self.singleCs = 1
            self.cs = csids[0]
        if len(tsids) == 1:
            tsids = [ tsids[0] for i in rangen ]
            self.singleTs = 1
            self.ts = tsids[0]

        self.observations = {}
        for value,i in zip(values,rangen):
            iobs = Observation(ts=tsids[i],
                               cs=[csids[i]],
                               variable=[variable],
                               value = value)
            self.observations[i] = iobs

        self.observationKeys = self.observations.keys()

        box = classifier.BoxClass(values,fence = fence)
        self.lowOutliers = box.lowOutliers
        self.highOutliers = box.highOutliers
        self.bins = box.bins
        self.binIds = box.binIds
        self.binCounts = box.binCounts
        self.maxX = box.maxX
        self.minX = box.minX
    
    def matchObservations(self,otherViewObservations):
        """
        Find Observations in our View that have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.
        XXX check logic on matching. should we have an argument to this
        function to specify cs, ts, or all matching. this would allow us to
        move this back up to the super class.

        """

        matched = []
        nobs = len(otherViewObservations)

        for ob in otherViewObservations:
            cs = ob.cs
            cscheck = array(self.cs)
            for cid in cs:
                cmatchId = [ ourc for ourc in cscheck if ourc == cid ]
                if cmatchId:
                    matched.extend(cmatchId)
        return matched

#class IMarkovMatrix(IView):
#    """Markov Matrix specific interaction methods and attributes"""
#    def __init__(self,variable,values,cells,interval):
#        """variable: STARS variable
#           values:   continuous values for matrix scatterplot (array
#           n*(t-k)
#           cells:    cell ids for cell-matrix (array n*(t-k)).
#           interval: length of transition interval (int k)"""
#        IView.__init__(self)
#        self.observations = {}
#        id = 0
#        n = range(len(values))
#        id2cell = dict( [ (i,[]) for i in n ] )
#        T = range(cells.shape[1]-interval)
#        t2cell = dict( [ (i,[]) for i in T ] )
#        k = max(max(cells))
#        rk = range(k)
#        cellObservations = dict( [ ((i,j),[]) for i in rk for j in rk ] )
#        observations = {}

#        for t in T:
#            tk = t+interval
#            for id in n:
#                iObs = Observation(ts=[t],cs=[id],
#                        variable = [variable],
#                        value = [values[id,t],values[id,tk]])
#                observations[(id,t)]=iObs
#                i = cells[id,t]
#                j = cells[id,tk]
#                ij = (i,j)
#                cellObservations[ij].append((id,t))
#                id2cell[id].append(ij)
#                t2cell[t].append(ij)

#        self.observations = observations
#        self.observationKeys = self.observations.keys()
#        self.cellObservations = cellObservations
#        self.t2cell = t2cell
#        self.id2cell = id2cell

#    def matchObservations(self,otherViewObservations):
#        csids = self.matchCsObservations(otherViewObservations)
#        tsids = self.matchTsObservations(otherViewObservations)
#        csids.extend(tsids)
#        return self.pruneMatchedIds(csids)

#    def matchCsObservations(self,otherViewObservations):
#        matchedIds = []
#        for oid in otherViewObservations:
#            if oid.cs:
#                for id in oid.cs:
#                    cells = self.id2cell[id]
#                    if cells:
#                        matchedIds.extend(cells)
#        return self.pruneMatched(matchedIds)

#    def matchTsObservations(self,otherViewObservations):
#        matchedIds = []
#        for oid in otherViewObservations:
#            if oid.ts:
#                for id in oid.ts:
#                    cells = self.t2cell[id]
#                    if cells:
#                        matchedIds.extend(cells)
#        return self.pruneMatched(matchedIds)

#    def match(self,tsIds=None,csIds=None,cellIds=None):
#        """find transition cells that match the intersection of the
#         specified Ids."""
#         tsCells = {}
#         csCells = {}

#         t = [ tsCells.extend(self.t2cell[i]) for i in tsIds ]
#         t = [ csCells.extend(self,t2cell[i]) for i in csIds ]
#         # use sets here for intersection set of cells
#         t = Set(tsCells)
#         c = Set(csCells)
#         match = t.intersect(c)
#         return list(match)


#    def pruneMatched(self,matchedIds):
#        matched = []
#        for match in matechedIds:
#            if matched.count(match) == 0:
#                matched.append(match)
#        return matched


            
            
class IMap(IView):
    """
    Map specific interaction methods and attributes.
    """
    def __init__(self,variable,values,t,poly2cs,cs2poly):
        """
        variable (string): STARS Variable name
        values (list): of numeric values to be mapped?
        t (integer): time period Id
        poly2cs: dictionary with polygon Id as  key and associated
            cross-sectional Ids as value. Maps a specific polygon to a
            specific cross sectional unit (one-to-one).
        cs2poly: dictionary with cross-sectional Id as key and associated
            polygon Ids as values. Maps a specific cross-sectional unit to one
            or more polygons (one-to-many).
        """
        IView.__init__(self)
        self.observations = {}
        self.poly2cs = poly2cs
        self.cs2poly = cs2poly
        pid=0
        for poly in poly2cs.keys():
            csid = poly2cs[poly][0]
            iObs = Observation(ts=[t],
                 cs=[csid],
                 variable=[variable],
                 value=[values[csid-1]])
            self.observations[poly] = iObs
        self.observationKeys = self.observations.keys()

    def matchObservations(self,otherViewObservations):
        """
        Find Observations on Map that have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.

        Overrides matchObservations in IView.
        """
        matchedIds = []
        for oid in otherViewObservations:
            if oid.cs:
                for id in oid.cs:
                    newIds = self.cs2poly[id]
                    for newId in newIds:
                        if newId not in matchedIds:
                            matchedIds.append(newId)
        return matchedIds

class IScatter(IView):
    """
    Scatter graph specific interaction methods and attributes.
    """
    def __init__(self,variableX,valuesX,
            variableY,valuesY,t):
        """
        variableX (string): name of variable to plot on x axis
        valuesX (list): of numeric values associated with variableX
        variableY (string): name of variable to plot on y axis
        valuesY (list): of numeric values associated with variableY
        t (integer): time period Id to plot relationship between variableX and
            variable Y XXX (pulls off the tth column of their respective data
            matrices???)
        """
        IView.__init__(self)
        self.observations = {}
        id = 0
        n=range(len(valuesX))
        self.variableX = variableX
        self.variableY = variableY
        self.valuesX = valuesX
        self.valuesY = valuesY
        for id in n:
            iObs = Observation(ts=[t],
                 cs=[id],
                 variable=[variableX,variableY],
                 value=[valuesX[id],valuesY[id]])
            self.observations[id] = iObs

        self.observationKeys = self.observations.keys()

    def matchObservations(self,otherViewObservations):
        """
        Find Observations on Scatter that have similar signatures to those in
        another View.
        Matches on cross-sectional Ids. XXX Maybe refactor this.

        otherViewObservations (list): of Observation objects from another
        IView object.

        Overrides matchObservations in IView.
        """

        matchedIds = []
        for oid in otherViewObservations:
            if oid.cs:
                for id in oid.cs:
                    if id not in matchedIds:
                        matchedIds.extend([id])
        return matchedIds

class ICScatterPlot(IView):
    """
    Conditional scatter graph specific interaction methods and attributes
    """
    def __init__(self,x,y,z):
        """
        x (matrix): values organized by n cross-sectional units and t time series periods
        y (matrix): values organized by n cross-sectional units and t time series periods
        z (matrix): values organized by n cross-sectional units and t time series periods


        z is the conditioning variable, x and y are portrayed for all time
        periods (all T scatters are combined in a single plot) and color depth
        is used to condition based on z values.


        tsids and csids are determined by col and row length of x,y,z
        each is assumed to be csts for now. XXX Refactor this!
        """
        IView.__init__(self)
        n,t = shape(x)
        self.ts = arange(t)
        self.cs = arange(n)
        self.observations = {}
        cs2key = {}
        ts2key = {}

        if rank(z) == 1:
            if len(z) == n:
                zmat = matrixmultiply(diag(z),ones((n,t)))
            else:
                zmat = matrixmultiply(ones((n,t)),diag(z))
        else:
            zn,zt = shape(z)
            if zt == 1:
                zmat = matrixmultiply(diag(z[:,0].tolist()),ones((n,t)))
            elif zn == 1:
                zmat = matrixmultiply(ones((n,t)),diag(z[0]))
            else:
                zmat = z

        for t in self.ts:
            for i in self.cs:
                xvalue = x[i,t]
                yvalue = y[i,t]
                zvalue = zmat[i,t]
                iObs = Observation(ts=[t],
                    cs = [i],
                    variable = [ x,y,z ],
                    value = [xvalue,yvalue,zvalue])
                self.observations[(i,t)] = iObs
                if cs2key.has_key(i):
                    cs2key[i].append((i,t))
                else:
                    cs2key[i] = [(i,t)]
                if ts2key.has_key(t):
                    ts2key[t].append((i,t))
                else:
                    ts2key[t] = [(i,t)]
        self.cs2key = cs2key
        self.ts2key = ts2key
        self.observationKeys = self.observations.keys()
        self.minx = min(min(x))
        self.maxx = max(max(x))
        self.miny = min(min(y))
        self.maxy = max(max(y))
        self.minz = min(min(zmat))
        self.maxz = max(max(zmat))
        self.colorId = {}
        self.colorMap()
        
    def colorMap(self,nColors=32):
        """
        scale z values to get a color depth to use in conditioning.

        nColors (int): hue range to scale z values.
        """
        for obkey in self.observationKeys:
            observation = self.observations[obkey]
            values = observation.value
            zi = nColors * (values[2]-self.minz)/(self.maxz-self.minz)
            self.colorId[obkey] = int(zi)

    def getObsforIds(self,ids):
        """
        Find the Observation objects associated with particular ids.

        ids (list): of Observation Ids

        returns (list): of Observation objects.

        Overrides getObsforIds in IView.py
        XXX Refactor or move up?
        """

        observations = []
        for id in ids:
            obs = self.observations[id]
            observations.append(obs)
        return observations

    def matchObservations(self,observations):
        """
        Find Observations have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.
        """
        matchedKeys = []
        for obs in observations:
            ts = obs.ts
            csIds = obs.cs
            for cs in csIds:
                if self.cs2key.has_key(cs):
                    matchedKeys.extend(self.cs2key[cs])
        return matchedKeys 

class ITimeSeries(IView):
    """Time Series specific interaction methods and attributes"""
    def __init__(self,variable,values,tsid,csid=[]):
        """
        variable (string): variable name.
        values (list): values XXX assumed to be pure TS?
        tsid (list): of time series Ids.
        csid (list): of cross-sectional Ids.
        """
        IView.__init__(self)
        self.ts = tsid
        self.cs = csid
        tid = 0
        T = len(tsid)
        self.observations = {}
        for tid in range(T):
            obs = Observation(ts=tsid[tid],
                cs = csid,
                variable = [variable],
                value = values[tid])
            self.observations[tsid[tid]] = obs
        self.observationKeys = self.observations.keys()
        
    def matchObservations(self,otherViewObservations):
        """
        Find Observations in our View that have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.
        XXX Move up to superclass?
        """

        matchTsIds = []
        for obs in otherViewObservations:
            if obs.ts:
                for tsid in obs.ts:
                    if tsid in self.ts:
                        id = self.ts.index(tsid)
                        if id not in matchTsIds:
                            matchTsIds.append(id)
        return matchTsIds

    def getTime(self,tsId):
        """
        Get the first timeSeries Id assocaited with tsId
        XXX not sure what this is doing for us?
        """
        newTime = self.observations[tsId][0]
        return newTime

class IHistogram(IView):
    """
    Histogram specific interaction methods and attributes
    """
    def __init__(self,variable,values,tsid,csid,classification="sturges",nBins=5,bins=[]):
        """

        variable (string): variable name
        values (list): values XXX looks like assumed to be cs?
        tsid (integer): ts id XXX not consistent with others - should this be
            refactored?
        csid (list): cross-sectional Ids
        binInfo (list): bounds for bins XXX looks like classification is done
            here, but maybe it should be after the fact (outside fo this
            IView and passed in as an argument? We can use our classification
            schemes from other modules for this).
        """
        IView.__init__(self)
        self.ts = tsid
        self.cs = csid
        tid = 0
        self.observations = {}
        self.idObservations = {}
        n = len(values)
        rn = range(n)
        for id in rn:
            obs = Observation(ts=tsid,cs=[id],
                              variable = [variable],
                              value = values[id])
            self.observations[id] = obs
            self.idObservations[obs] = id

        self.observationKeys = self.observations.keys()
        self.classification = classification
        self.nBins = nBins
        self.Bins = bins

        #maxx=max(values)
        #minx=min(values)
        #rangex=maxx-minx
        #if len(binInfo) == 0:
            #Sturge's Rule
        #    x=values
        #    n = len(x)
        #    nbin = round(1 + log(n)) + 1
        #    maxx = max(x)
        #    minx = min(x)
        #    rangex = maxx - minx
        #    w = rangex/nbin
        #    bounds= arange(minx+w,maxx+w,w)
        #    if bounds[-1] <= maxx:
        #        bounds[-1] = maxx * 1.0001
        #    nbounds = len(bounds)
        #    classes = searchsorted(bounds,x)
        #    counts = [ sum(classes == bin) for bin in range(nbounds) ]

        #elif  len(binInfo) == 1:
        #    nbin = binInfo[0]
        #    rg = maxx - minx
        #    w = rg/nbin*1.
        #    bounds = range(minx+w,maxx+w,w)
        #    classes = searchsorted(bounds,values)
        #    counts = [ sum(classes == x) for x in range(nbin)]

        #else:
        #    bounds = binInfo
        #    nbin = len(bounds)
        #    classes = searchsorted(bounds,values)
        #    counts = [ sum(classes == x) for x in range(nbin)]

        #self.classes = classes
        #self.bounds = bounds
        #self.value = values
        #self.counts = counts

        #use classifier and get rid of results from ifstatements
        # XXX see comments in docstring on this

        classResults = classifier.Classifier(values,method=classification,nBins=nBins,bins=bins)
        self.classes = classResults.binIds
        classes = self.classes
        self.bounds = classResults.bins
        self.value = values
        self.counts = classResults.binCounts
        nbounds = len(self.bounds)

        print self.bounds
        print max(values)

        self.bins = {}
        for binid in range(nbounds):
            self.bins[binid] = []
        nr=range(len(values))
        print min(classes), max(classes)
        for i in nr:
            ci = classes[i]
            self.bins[ci].append(i)

    def matchObservations(self,otherViewObservations):
        """
        Find Observations in our View that have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.
        XXX check logic on matching. should we have an argument to this
        function to specify cs, ts, or all matching. this would allow us to
        move this back up to the super class.

        """

        matchCsIds = []
        for obs in otherViewObservations:
            if obs.cs:
                for csid in obs.cs:
                    if csid in self.cs:
                        id = self.cs.index(csid)
                        if csid not in matchCsIds:
                            matchCsIds.append(id)
        return matchCsIds

    def getBinsforObservations(self,otherViewObservations):
        """
        Find the bins that the observations are in.

        otherViewObservations (list): Observation objects from another view.

        Returns bins (list) of bin ids.

        """
        ids = self.matchObservations(otherViewObservations)
        bins = [ self.classes[x] for x in ids]
        return bins

    def getBinsforIds(self,ids):
        """
        Finds bins that each id is in.

        XXX MJ explain

        """
        bins = [ self.classes[x] for x in ids]
        return bins

    def selectBinIds(self,binId):
        """
        Select bins that contain binId.

            
        XXX MJ explain
        """
        ids =  self.bins[binId]
        self.select(ids)

    def newSelectBinIds(self,binId):
        """

        XXX MJ Explain
        """ 
        ids =  self.bins[binId]
        self.newSelect(ids)

    def binSelectedHeights(self):
        """
        Find the number of selected elements in each bin.

        Returns binSelectCount (dict) : key = binId, value = integer count
        XXX MJ Explain
        """
        ids = self.selected
        bins = self.getBinsforIds(ids)
        binSelectCount = {}
        for bin in bins:
            if binSelectCount.has_key(bin):
                binSelectCount[bin] += 1
            else:
                binSelectCount[bin] = 1
        for binKey in binSelectCount.keys():
            bininfo = binSelectCount[binKey]
            bincount = self.counts[binKey]
            binSelectCount[binKey] = [bininfo,bincount]

        return binSelectCount

class ITimePath(IView):
    """
    Time Path specific interaction methods and attributes
    """
    def __init__(self,xVariableName,xValues,yVariableName,yValues,
                 t,cs):
        """

        xVariableName (string): variable name for x-axis.
        xValues (list): values for xVariable XXX refactor?
        yVariableName (string): variable name for y-axis.
        yValues (list): values for yVariable XXX refactor?
        t (list): ts Ids
        cs (list): list of cross-section ids.
        """
        IView.__init__(self)
        self.observations = {}
        self.tsIds = t
        self.csIds = cs
        n = len(t)
        nrange = range(n)
        for i in nrange:
            csid = cs
            iObs = Observation(ts=[t[i]],
                               cs=csid,
                               variable = [xVariableName,yVariableName],
                               value = [xValues[i],yValues[i]])
            self.observations[i] = iObs
        self.ids = self.observations.keys()
        self.observationKeys = self.observations.keys()
        
    def matchObservations(self,otherViewObservations):
        """
        Find Observations in our View that have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.
        """

        matchedIds = []
        no = len(otherViewObservations)
        flag = 1
        c = 0
        while flag:
            oid=otherViewObservations[c]
            if type(oid.ts) != type([]):
                oid.ts = [oid.ts] 
            tsmatches = [ self.tsIds.index(x) for x in oid.ts \
                          if self.tsIds.count(x) ]
            [matchedIds.append(newId) for newId in tsmatches \
                          if matchedIds.count(newId) < 1 ]
            oidcs = oid.cs
            counts = [ self.csIds.count(x) for x in oidcs ]
            # if the otherViewObservations have the same csid as this
            # TimePath, match all points on the time path
            if max(counts):
                matchedIds = self.ids # match all (and break)
                flag = 0
            oidts = oid.ts
            c += 1
            if c == no:
                flag = 0
        return matchedIds
       
class IDensity(IView):
    """
    Density specific interaction methods and attributes
    """
    def __init__(self,varName,y,tsid,csid,xmin=None,xmax=None):
        """
        varname (string): variable name.
        y (list): values XXX assumed to be cs?
        tsid (list): time series ids
        csid (list): cross-sectional ids
        xmin (float): lower bound for x-axis
        xmax (float): upper found fo x-axis
        """
        IView.__init__(self)
        self.ts = tsid
        self.cs = csid
        kest = Kde(y,xmin=xmin,xmax=xmax)
        self.xgrid = kest.xgrid
        self.fx = kest.fx
        binIds = searchsorted(self.xgrid,y)
        counts = [ sum(y <= cut) for cut in self.xgrid ]
        counts = array(counts)
        c1 = [counts[0]]
        c1.extend(counts[1:] - counts[:-1])
        self.binCounts = c1
        self.nBins = len(self.xgrid)
        self.bins = self.xgrid
        self.observations = {}
        rn = range(len(y))
        bin2id = {}
        id2bin = {}
        for id in rn:
            obs = Observation(ts=[tsid[id]],cs = [csid[id]],
                variable = [varName],
                value = y[id])
            self.observations[id] = obs
            binId = binIds[id]
            id2bin[id] = binId
            if bin2id.has_key(binId):
                bin2id[binId].append(id)
            else:
                bin2id[binId] = [id]

        self.bin2id = bin2id
        self.id2bin = id2bin
        self.observationKeys = self.observations.keys()

    def matchObservations(self,otherViewObservations):
        """
        Find Observations in our View that have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.

        Returns matchCsIds (list) of cross-sectional Ids XXX refactor for
            generality? Why not pass in any kind of values, not just cs?
        """
        matchCsIds = []
        for obs in otherViewObservations:
            if obs.cs:
                try:
                    for csid in obs.cs:
                        if self.cs.count(csid):
                            id = self.cs.index(csid)
                            if matchCsIds.count(csid)==0:
                                matchCsIds.append(id)
                except:
                    temp = [obs.cs]
                    for csid in temp:
                        if csid in self.cs:
                            id = self.cs.index(csid)
                            if csid not in matchCsIds:
                                matchCsIds.append(id)
        return matchCsIds

    def getBinsforObservations(self,otherViewObservations):
        """
        find the vertical "bin" that observations are associated with.

        returns bins (list) of bin ids
        """
        ids = self.matchObservations(otherViewObservations)
        bins = [self.id2bin[id] for id in ids]
        return bins
        
class ICDF(IView):
    """
    CDF specific interaction methods and attributes
    """
    def __init__(self,varName,y,tsid,csid,xmin=None,xmax=None):
        """
        varname (string): variable name.
        y (list): values XXX assumed to be cs?
        tsid (list): time series ids
        csid (list): cross-sectional ids
        xmin (float): lower bound for x-axis
        xmax (float): upper found fo x-axis
        """
        IView.__init__(self)
        self.ts = tsid
        self.cs = csid
        kest = Kde(y,xmin=xmin,xmax=xmax)
        self.cdf = kest.createCDF()
        self.xgrid = kest.xgrid
        self.fx = kest.fx
        binIds = searchsorted(self.xgrid,y)
        counts = [ sum(y <= cut) for cut in self.xgrid ]
        counts = array(counts)
        c1 = [counts[0]]
        c1.extend(counts[1:] - counts[:-1])
        self.binCounts = c1
        self.nBins = len(self.xgrid)
        self.bins = self.xgrid
        self.observations = {}
        rn = range(len(y))
        bin2id = {}
        id2bin = {}
        for id in rn:
            obs = Observation(ts=[tsid[id]],cs = [csid[id]],
                variable = [varName],
                value = y[id])
            self.observations[id] = obs
            binId = binIds[id]
            id2bin[id] = binId
            if bin2id.has_key(binId):
                bin2id[binId].append(id)
            else:
                bin2id[binId] = [id]

        self.bin2id = bin2id
        self.id2bin = id2bin
        self.observationKeys = self.observations.keys()

    def matchObservations(self,otherViewObservations):
        """
        Find Observations in our View that have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.

        Returns matchCsIds (list) of cross-sectional Ids XXX refactor for
            generality? Why not pass in any kind of values, not just cs?
        """
        matchCsIds = []
        for obs in otherViewObservations:
            if obs.cs:
                try:
                    for csid in obs.cs:
                        if self.cs.count(csid):
                            id = self.cs.index(csid)
                            if matchCsIds.count(csid)==0:
                                matchCsIds.append(id)
                except:
                    temp = [obs.cs]
                    for csid in temp:
                        if csid in self.cs:
                            id = self.cs.index(csid)
                            if csid not in matchCsIds:
                                matchCsIds.append(id)
        return matchCsIds

    def getBinsforObservations(self,otherViewObservations):
        """
        find the vertical "bin" that observations are associated with.

        returns bins (list) of bin ids
        """
        ids = self.matchObservations(otherViewObservations)
        bins = [self.id2bin[id] for id in ids]
        return bins
        
class IPCP(IView):
    """
    Parallel coordinate graph specific interaction methods and attributes
    """
    def __init__(self, variableNames, valuesY, t, valuesZ=[], zName=None):
        IView.__init__(self)
        """



        """
        self.observations = {}
        id = 0
        n=range(len(valuesY[0])) # number of cs
        k=range(len(valuesY)) # number of variables
        self.valuesY = valuesY
        self.valuesZ = valuesZ
        self.zName = zName
        self.variableNames = variableNames
        for id in n:
            vals = []
            [vals.append(self.valuesY[j][id]) for j in k] 
            iObs = Observation(ts=[t], cs=[id],variable=self.variableNames,value=vals)
            self.observations[id] = iObs
        
        self.observationKeys = self.observations.keys()
        #z is for conditioned variable - first var user inputs for now
        self.colorId = {}
        if self.zName:
            self.colorMap()
        
    def colorMap(self,nColors=32):
        """
        scales z values to set conditioning color scheme
        XXX see if this is same as conditional scatter method? if so move up?

        """
        z = self.valuesZ
        self.minz = min(z)
        self.maxz = max(z)
        zr = range(len(self.valuesZ))
        observs = self.getObsforIds(zr)
        c = 0
        for obkey in observs:
            zi = nColors * (self.valuesZ[c]-self.minz)/(self.maxz-self.minz)
            #print "ZI",zi,int(zi) 
            self.colorId[c] = int(zi)
            #self.colorId[obkey] = int(zi)
            c = c+1
            
    def matchObservations(self,otherViewObservations):
        """
        Find Observations in our View that have similar signatures to those in
        another View.

        otherViewObservations (list): of Observation objects from another
        IView object.

        Returns matchedIds (list) of matched ids based on cs. 
        XXX check all matchObservations methods across all IView subclasses
        for refactoring.
        """
        matchedIds = []
        for oid in otherViewObservations:
            if oid.cs:
                for id in oid.cs:
                    if id not in matchedIds:
                        matchedIds.extend([id])
        return matchedIds

class ITable(IView):
    """ """
    def __init__(self,values,varName,tsid,csid):
        """
        values: array to be contained in grid cells

        varName: list  of lists with variables associated with
        each cell

        tsid: list of tuples with ts integer(s) associated with each cell

        csid: list of tuples with cs integer(s) associated with each cell
        """
        IView.__init__(self)
        self.ts = tsid
        self.csid = csid
        self.varName = varName
        n = size(values)
        rn = range(n)
        observations = {}
        ts2id = {}
        cs2id = {}
        var2id = {}
        vflat = values.flat
        for id in rn:
            obs = Observation(ts=tsid[id],
                    cs = csid[id],
                    variable = varName[id],
                    value = vflat[id])
            for ts in tsid[id]:
                if ts2id.has_key(ts):
                    ts2id[ts].append(id)
                else:
                    ts2id[ts]=[id]
            for cs in csid[id]:
                if cs2id.has_key(cs):
                    cs2id[cs].append(id)
                else:
                    cs2id[cs]=[id]
            for var in varName[id]:
                if var2id.has_key(var):
                    var2id[var].append(id)
                else:
                    var2id[var]=[id]

            observations[id] = obs

        self.observations = observations
        self.ts2id = ts2id
        self.cs2id = cs2id
        self.var2id = var2id

        self.ids = self.observations.keys()
        self.observationKeys = self.ids
        dimensions = {}
        dimensions["cs"] = cs2id
        dimensions["ts"] = ts2id
        dimensions['var'] = var2id
        self.dimensions=dimensions


    def matchObservations(self,otherViewObservations,dimensions=["cs"]):
        """Genearlized searcher for observation matching.
        
        otherViewObservations: is a list of Observations
        dimensions: list of dimensions to match on. Values: "cs","ts","var"
        XXXThis could be used to match on specified dimensions, either
        conjuntively, disjunctively, or other conditions. Think about using
        this on other types of IViews

        """
        matched = []
        nobs = len(otherViewObservations)
        for oid in otherViewObservations:
            for dimension in dimensions:
                ourDimension = self.dimensions[dimension]
                if oid.dimensions.has_key(dimension):
                    otherKeys = oid.dimensions[dimension]
                    for otherKey in otherKeys:
                        if ourDimension.has_key(otherKey):
                            matched.extend(ourDimension[otherKey])
        if matched:
            # remove duplicates
            matched = sets.Set(matched)
            matched = list(matched)
        return matched
               

    def matchObservationsCS(self,otherViewObservations):
        return self.matchObservations(otherViewObservations)

    def matchObservationsTS(self,otherViewObservations):
        return self.matchObservations(otherViewObservations, dimensions=["ts"])

    def matchObservationsCSTS(self,otherViewObservations):
        return self.matchObservations(otherViewObservations, dimensions=["cs","ts"])

if __name__ == '__main__':
    from numpy.oldnumeric import *
    from numpy.oldnumeric.random_array import *
    t=IView()
    t.select([1,2,3])

    # make up some fake data 55 polygons 40 observations 10 time periods
    N=40
    T=10

    var1 = reshape(arange(N*T),[N,T])
    timeVar = arange(0,T)
    var2 = var1 * 100
    var3 = var2 * 10
    
    # new test data using the us 48 lower states and income data
    # 1929-2000

    N = 48
    T = 72

    data = open("pcincome.txt",'r')
    d = data.readlines()
    data.close()
    data = []
    for row in d:
        row = row.strip()
        data.append([float(x) for x in row.split()])
    data = array(data)

    gis = open("us48.gis",'r')
    gisdata = gis.readlines()
    gis.close()
    nl = len(gisdata)
    row = 0
    cpolyDict = {}
    polyDict = {}
    pId = 0
    pcsDict = {}
    while row < nl:
        info = gisdata[row]
        info = info.split()
        info = [int(x) for x in info]
        csId = info[0]
        polyId = info[1]
        ncoord = info[2]
        pcsDict[pId] = [csId]
        r1 = row + 1
        r2 = row + ncoord + 1
        polyDict[pId] = [ float(coord.strip()) \
                               for coord in gisdata[r1:r2]]
        if cpolyDict.has_key(csId):
            cpolyDict[csId].append(pId)
        else:
            cpolyDict[csId] = [pId]
        pId = pId + 1
        row = row + ncoord + 1

    cs2poly = cpolyDict

    poly2cs = pcsDict
    var1 = data

    map1 = IMap("var1",var1[:,0],0,poly2cs,cs2poly)
    sc1 = IScatter("var1",var1[:,0],"var1",var1[:,-1], 0)
    ts1 = ITimeSeries("tvar",timeVar,timeVar.tolist())
    nid = arange(1,41)
    ts2 = ITimeSeries("tvar",timeVar,timeVar.tolist(),nid.tolist())
    tp1 = ITimePath("xvar",var1[0,:],"yvar",var1[1,:],
                    t=timeVar.tolist(),cs = [0,1])

    map1.select([1,2,3])
    ids = map1.getSelected()
    ts2.matchObservations(ids)


    map3 = IMap("var1",var1[:,3],3,poly2cs,cs2poly)

    map3.select([1,2,4])
    ids = map3.getSelected()
    # if map3 has selected three polygons and signals time series 2 we
    # get which observations on time series 2

    cs = range(N)
    h1 = IHistogram("var1",var1[:,3],tsid=3,csid=cs)
    b = IBox("var1",var1[:,1],tsids=[1],csids=cs)
    # clearling selection on map1 and selecting polygons 0, 15 and 54
    map1.newSelect([0,15,54])
    mobs = map1.getSelected()
    # find corresponding bins in histogram for these polygon
    # observations

    # testing TimePath matching
    map3.deselect()
    map3.select([2])
    ids = map3.getSelected()
    mobs = tp1.matchObservations(ids)
      

    map1.newSelect([0,15,54])
    mobs = map1.getSelected()

    tsids = [0]* N

    d1 = IDensity("var1",var1[:,0],csid=cs,tsid=tsids)

    var1 = var2 /10.
    icsp = ICScatterPlot(var1,var2,var3[0,:])
    icsp1 = ICScatterPlot(var1,var2,var3[:,0])

    # testing a table
    n=48
    t=72
    nt=n*t
    var=[[id] for id in ["pcr"]*nt]
    values = arange(nt)
    values = reshape(values,(n,t))
    csids = array( [ [i] * t for i in range(n) ])
    csids = csids.flat
    ts =range(t)
    tsids = array(  ts * n )
    tsids = tsids.flat
    csids = [ [cs] for cs in csids]
    tsids = [ [ts] for ts in tsids]
    table = ITable(values,var,tsids,csids)

    # new matching scheme
    csmatch = table.matchObservations(mobs)
    tsmatch = table.matchObservations(mobs,dimensions=["ts"])
    varMatch = table.matchObservations(mobs,dimensions=["var"])


