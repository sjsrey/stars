"""
Data and Matrix Classes
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Boris Dev     bdev@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------
"""

import numpy as np
from copy import copy
import os.path

# stars modules
import Utility
from stars import *
from Errors import *

def csts(values,n,t):
    values = np.array(values)
    values = np.reshape(values,[n,t])
    return values

def tscs(values,n,t):
    values = np.array(values)
    values = np.reshape(values,[t,n])
    values = np.transpose(values)
    return values

def cs(values,n,t):
    return np.reshape(np.array(values),[n,1])

def ts(values,n,t):
    return np.reshape(np.array(values),[t,1])

varMenu = {"CSTS": csts, "TSCS": tscs, "TS": ts, "CS": cs}

def lag(y,wsp):
    """Constructs the spatial lag of a variable.

    Arguments (2)
        y:  STARS Variable
        wsp:    Spatial Weights Matrix (Sparse Form or Full).

    Returns (1)
        lagy: Spatial Lag of y (List).

    Example Usage
        >>> from stars import *
        >>> s = Project("s")
        >>> s.ReadData("csiss")
        >>> region = s.getVariable("bea")
        >>> y = s.getVariable("pcincome")
        >>> wr = spRegionMatrix(region)
        >>> ylag = Variable(lag(y,wr))
    """
    if wsp.matType == "sparse":
        winfo = wsp.dict
        ids = sorted(winfo.keys())
        ylag = []
        for id in ids:
            i = winfo[id]
            nNeighbors = float(i[0])
            neighbors = i[1]
            # axis=0 preserves time dimension for CSTS (n x t) variables
            nsum = np.sum(np.take(y, neighbors, axis=0), axis=0) / nNeighbors
            ylag.append(nsum)
    else:
        w = wsp.full()
        ylag = (w @ y).tolist()
    return ylag


class Variable(np.ndarray):
    """STARS Variable.

    Arguments (1):
        values: list of numeric values.

    Attributes (?):
        n: number of regional observations
        t: number of temporal observations

    Example Usage:
        >>> from stars import *
        >>> s = Project("s")
        >>> s.ReadData("csiss")
        >>> region = s.getVariable("bea")
        >>> region.n
        48
        >>> region.t
        1
        >>> y = s.getVariable("pcincome")
        >>> y.n
        48
        >>> y.t
        72
    """
    variableType = "Variable"

    def __new__(cls, values):
        obj = np.asarray(values).view(cls)
        return obj

    def __array_finalize__(self, obj):
        dim = self.shape
        self.n = dim[0] if len(dim) > 0 else 0
        self.t = dim[1] if len(dim) > 1 else 1
        if obj is None:
            return
        self.id = getattr(obj, 'id', id(self))
        self.note = getattr(obj, 'note', '')
        self.variableType = getattr(obj, 'variableType', 'Variable')
        self.name = getattr(obj, 'name', '')
        self.varType = getattr(obj, 'varType', '')
        self.regionNames = getattr(obj, 'regionNames', [])
        self.timeString = getattr(obj, 'timeString', '')

    def addNote(self,message):
        self.note = message

    def setVariableType(self,variableType):
        self.variableType = variableType

    def setName(self,name):
        self.name = name

    def setType(self,varType):
        self.varType = varType

    def setRegionNames(self,regionNames):
        self.regionNames = regionNames

    def setTimeString(self,timeString):
        self.timeString = timeString


class SVariable(np.ndarray):
    """STARS Variable.

    Arguments (1):
        values: list of numeric values.

    Attributes (?):
        n: number of regional observations
        t: number of temporal observations

    Example Usage:
        >>> from stars import *
        >>> s = Project("s")
        >>> s.ReadData("csiss")
        >>> region = s.getVariable("bea")
        >>> region.n
        48
        >>> region.t
        1
        >>> y = s.getVariable("pcincome")
        >>> y.n
        48
        >>> y.t
        72
    """
    variableType = "Variable"

    def __new__(cls, values):
        obj = np.asarray(values).view(cls)
        return obj

    def __array_finalize__(self, obj):
        dim = self.shape
        self.n = dim[0] if len(dim) > 0 else 0
        self.t = dim[1] if len(dim) > 1 else 1
        if obj is None:
            return
        self.id = getattr(obj, 'id', id(self))
        self.note = getattr(obj, 'note', '')
        self.variableType = getattr(obj, 'variableType', 'Variable')
        self.name = getattr(obj, 'name', '')
        self.varType = getattr(obj, 'varType', '')
        self.regionNames = getattr(obj, 'regionNames', [])
        self.timeString = getattr(obj, 'timeString', '')

    def addNote(self,message):
        self.note = message

    def setVariableType(self,variableType):
        self.variableType = variableType

    def setName(self,name):
        self.name = name

    def setType(self,varType):
        self.varType = varType

    def setRegionNames(self,regionNames):
        self.regionNames = regionNames

    def setTimeString(self,timeString):
        self.timeString = timeString


class DataParser:
    """Process STARS Data file input and creates variable instances."""
    def __init__(self,info,project):
        vnames = list(info.keys())
        self.varNames = vnames
        dataDict = {}
        for i in vnames:
            var = info[i]
            varType = var[0].upper()
            values = var[1]
            n=var[2][0]
            t=var[2][1]
            values = varMenu[varType](values,n,t)
            variable = Variable(values)
            variable.setName(i)
            variable.setType(varType)
            dataDict[i] = variable
            project.dataBase.addVariable(variable) # assumes this is used within a project

class TimeString:
    """Makes labels for periods in a time-series. """

    def __init__(self,type):
        self.type = type
        self.string = "NONE"
        self.numeric = 0
    def __str__(self):
        return (str(self.getNumeric()))

    __repr__ = __str__

    def getString(self):
        """Create string representation of time series coordinates."""

        return self.string

    def getNumeric(self):
        """Create numeric representation of time series coordinates."""

        return self.numeric

class Annual(TimeString):
    """Labels for annual time series """

    def __init__(self,startTime,finishTime,inc=1):
        TimeString.__init__(self,"ANNUAL")
        startTime = int(startTime)
        finishTime = int(finishTime)
        finishTime = finishTime+1
        self.numeric = list(range(startTime,finishTime,int(inc)))
        self.string = list(map(repr,self.numeric))
        self.t = len(self.numeric)
        self.timeType = 'ANNUAL'
        self.summary()

    def summary(self):
        t1 = "Time Series Type: " + self.timeType
        t2 = "T = " + str(self.t)
        t3 = "Start Year: " + self.string[0]
        t4 = "End Year: " + self.string[-1]
        self.timeSummary = "\n".join([t1,t2,t3,t4])

    def report(self):
        print(self.timeSummary)

class Decadal(TimeString):
    """Labels for decadal time series """
    def __init__(self,startTime,finishTime,inc=10):
        TimeString.__init__(self,"ANNUAL")
        startTime = int(startTime)
        finishTime = int(finishTime)
        finishTime = finishTime+1
        self.numeric = list(range(startTime,finishTime,int(inc)))
        self.string = list(map(repr,self.numeric))
        self.t = len(self.numeric)
        self.timeType = 'DECADAL'
        self.summary()

    def summary(self):
        t1 = "Time Series Type: " + self.timeType
        t2 = "T = " + str(self.t)
        t3 = "Start Year: " + self.string[0]
        t4 = "End Year: " + self.string[-1]
        self.timeSummary = "\n".join([t1,t2,t3,t4])

    def report(self):
        print(self.timeSummary)

class SubAnnual(TimeString):
    """Labels for subannual time series:
        Arguments:
        startSub: integer of subperiod to start with 1 thru 12
        startYear: integer of start year
        finishSub: integer of subperiod to end (included in analysis)
        finishYear: integer of last year
        division: must be 4 for quarterly or 12 for monthly XXX perhaps allow
        for others????
        Attributes:
        self.numeric: range of length t
        self.string: labels for each t
        """
    def __init__(self,startSub,startYear,finishSub,finishYear,division):
        subannualTypes = {4:"QUARTERLY", 12:"MONTHLY"}
        TimeString.__init__(self,subannualTypes[division])
        mRange = [ str(i) for i in range(1,division+1) ]
        yRange = [ str(i) for i in range(startYear,finishYear+1) ]
        f = mRange[startSub-1:]
        first = [ sub +"/"+yRange[0] for sub in f ]
        if startYear == finishYear:
            time = first[0:finishSub]
        else:
            e = mRange[:finishSub]
            end = [ sub +"/"+yRange[-1] for sub in e ]
            mid = []
            if len(yRange) > 2:
                c = 1
                for i in yRange[1:-1]:
                    subAndYear = [ sub +"/"+yRange[c] for sub in mRange ]
                    [ mid.append(my) for my in subAndYear ]
                    c = c+1
            time = first + mid + end
        self.numeric = list(range(len(time)))
        self.string = time
        self.t = len(self.numeric)
        self.timeType = subannualTypes[division]
        self.summary()

    def summary(self):
        t1 = "Time Series Type: " + self.timeType
        t2 = "T = " + str(self.t)
        t3 = "Start Sub-Year / Year: " + self.string[0]
        t4 = "End Sub-Year / Year: " + self.string[-1]
        self.timeSummary = "\n".join([t1,t2,t3,t4])

    def report(self):
        print(self.timeSummary)

class Irregular(TimeString):
    """Labels for irregular time periods:
        Arguments:
        t: number of time periods
        tLabels: optional argument, list of irregular time period names
    """
    def __init__(self,t,tLabels=[]):
        TimeString.__init__(self,"IRREGULAR")
        self.numeric = list(range(1,t+1))
        self.timeType = "IRREGULAR"
        if len(tLabels) == t:
            self.string = tLabels
        else:
            print("Number of labels do not match the number of time periods.\nUsing integers to represent irregular time periods.")
            self.string = [ str(i) for i in self.numeric ]
        self.t = t
        self.summary()

    def summary(self):
        t1 = "Time Series Type: " + self.timeType
        t2 = "T = " + str(self.t)
        t3 = "Start Period: " + self.string[0]
        t4 = "End Period: " + self.string[-1]
        self.timeSummary = "\n".join([t1,t2,t3,t4])

    def report(self):
        print(self.timeSummary)

# stubs for other frequency classes
Quarterly = Annual
Monthly = Annual
timeFreqMenu={"DECADAL":Decadal,"ANNUAL": Annual,
              "QUARTERLY": Quarterly, "MONTHLY": Monthly}

class FileReader:
    """Abstract class for reading STARS input files."""
    def __init__(self,fileName):
        self.fileName = fileName
        self.contents = self.readFile()

    def readFile(self):
        fileName = self.fileName
        try:
            f = open(fileName,'r')
            return f.read().split()
            f.close()
        except:
            mesg = "Cannot open file: %s"%fileName
            Error(mesg)
            return None

    def parse(self):
        pass

class DataReader(FileReader):
    def __init__(self,fileName):
        dataFile= fileName + ".dat"
        FileReader.__init__(self,dataFile)
        try:
            h = open(fileName+".dht",'r')
            self.header = h.readlines()
            h.close()
        except:
            mesg="No header file found: %s"%fileName
            Error(mesg)

        self.timeInfo = self.header[0].split()
        self.timeFreq = self.timeInfo[0].upper()
        self.timeFreq = self.timeFreq.strip()
        if self.timeFreq == "IRREGULAR":
            t = int(self.timeInfo[-1])
            self.timeClass = Irregular(t)
        else:
            self.timeClass = timeFreqMenu[self.timeFreq](*self.timeInfo[1:])
        regionInfo = self.header[1:]
        self.regionType = regionInfo[0].strip()
        self.regionNames = [x.strip() for x in regionInfo[1:]]
        self.parse()


    def timeString(self):
        return self.timeClass.getString()

    def timeNumeric(self):
        return self.timeClass.getNumeric()

    def parse(self):
        self.t = len(self.timeString())
        self.n = len(self.regionNames)
        d = self.contents
        self.nVars = int(d[0])
        self.varNames = d[1:self.nVars+1]
        p = self.nVars+1
        self.contents = d[p:]
        lIndex = []
        for i in self.varNames:
            lIndex.append(self.contents.index(i))
        rIndex = lIndex[1:]
        rIndex.append(len(self.contents))
        self.Info = {}
        i = 0
        for v in self.varNames:
            r = rIndex[i]
            l = lIndex[i]
            info = self.contents[l:r]
            name = info[0]
            type = info[1].upper()
            vals = info[2:]
            vals = list(map(float,vals))
            self.Info[name] = [type,vals,[self.n,self.t]]
            i += 1

class fMatrix:
    """Full matrix"""
    def __init__(self,matrix):
        self.values = matrix
        self.matType="full"
    def setName(self,name):
        self.name = name
    def full(self):
        return self.values

class spMatrix:
    """Sparse Matrix Super Class"""
    def __init__(self,name):
        self.name = name
        self.dict = {}
        self.matType = "sparse"

    def full(self):
        """Returns a full row standardized weights matrix."""
        n = len(self.dict)
        w = np.zeros([n,n])
        ids = list(self.dict.keys())
        for id in ids:
            neighborids = self.dict[id][1]
            nNeighbors = self.dict[id][0]
            w[id, neighborids] = 1. / nNeighbors
        return w

    def setName(self,name):
        self.name = name

    def zeroRows(self):
        """Returns a list of row indices with zero sums.
        """
        full = self.full() > 0
        rowSums = np.sum(full, axis=1)
        zeroRows = rowSums == 0.0
        numZeros = int(np.sum(zeroRows))
        if numZeros > 0:
            return np.argsort(zeroRows)[-numZeros:].tolist()
        else:
            return []

    def islands(self):
        ids = list(self.dict.keys())
        islands = [ id for id in ids if self.dict[id][0]==0 ]
        return islands


    def  symmetryCheck(self):
        """Returns 1 if matrix is symmetric, 0 otherwise."""
        full = self.full() > 0
        comp = full != full.T
        if np.sum(comp) == 0:
            return 1
        else:
            return 0

    def asymmetricRows(self):
        """Returns a list of row indices of asymetries.
        """
        full = self.full() > 0
        comp = full != full.T
        rowSums = np.sum(comp, axis=1)
        rows = rowSums > 0.0
        numRows = int(np.sum(rows))
        if numRows > 0:
            return np.argsort(rows)[-numRows:].tolist()
        else:
            return []

class spGalMatrix(spMatrix):
    """Spatial weights matrix in sparse form based on GAL.

    Arguments (1)
        galinfo: list of integer values defining GAL.

    Attributes (?)

    Example Usage
        >>> from stars import *
        >>> s = Project("s")
        >>> galstates=open("states48.gal",'r')
        >>> ws = galstates.readlines()
        >>> galstates.close()
        >>> galinfo = list(map(int,"".join(ws).split()))
        >>> name="wsp"
        >>> wsp = spGalMatrix(name,galinfo)
    """
    def __init__(self,name,galInfo):
        spMatrix.__init__(self,name)
        self.n=galInfo[0]
        id=1
        for i in range(self.n):
            rid = galInfo[id]
            nNeighbors = galInfo[id+1]
            neighbors = galInfo[id+2:id+2+nNeighbors]
            self.dict[rid] = [nNeighbors, np.array(neighbors)]
            id += 2+nNeighbors

class spRegionMatrix(spMatrix):
    """Spatial weights matrix in sparse form based on regional membership.

    Arguments (1)
        regions: STARS Variable with regional membership identifier.

    Attributes (1)
        dict: Dictionary with key equal to observation id, entry is a
        List with two elements: (1) number of neighbors, (2) ids of neighbors (List).

    Example Usage
        >>> from stars import *
        >>> s = Project("s")
        >>> s.ReadData("csiss")
        >>> region = s.getVariable("bea")
        >>> wr = spRegionMatrix(region)
    """
    def __init__(self,regions):
        spMatrix.__init__(self,regions.name)
        ra = np.take(regions, list(range(len(regions))))
        rids = Utility.unique(ra)
        for r in rids:
            members = np.nonzero(ra[:,0]==r)[0]
            for member in members:
                neighbors = np.take(members, np.nonzero(members!=member)[0])
                self.dict[member] = [len(neighbors),neighbors]
        self.setName(regions.name)

def full2Sparse(fullMatrix):
    # returns sparse binary representation of a full matrix
    # nonzero values are treated as binary 1
    n,k = fullMatrix.shape
    d = {}
    ij_pairs = [ (i,j) for i in range(n-1) for j in range(i+1,n) ]

    for i,j in ij_pairs:
        v = fullMatrix[i,j]
        if v:
            try:
                d[i].append(j)
            except:
                d[i] = [j]
            try:
                d[j].append(i)
            except:
                d[j] = [i]

    # return a dictionary with ids as keys, values are a 2-tuple with
    # first element the number of neighbors, second element a list of
    # neighbor ids

    d1 = [ (i[0],(len(i[1]),i[1])) for i in d.items() ]
    return dict(d1)

def ij(n):
    """Returns upper triangular indices for looping over a square
    matrix"""

    rn = list(range(n))
    return [ (i,j) for i in rn[0:-1] for j in rn[i+1:n] ]

class Regime:
    """Zero offset of a STARS variable intended for use as a regime"""
    def __init__(self, variable, name=None):
        """variable: a cs variable."""
        uid = dict( [ (i,i) for i in variable[:,0] ] )
        n = len(variable)
        rn = range(n)
        uids = sorted(uid.keys())
        bridge = dict( [ (i,uids.index(variable[i,0])) for i in rn ] )
        self.bridge=bridge
        self.uids = uids
        self.partition = list(bridge.values())
        if name:
            self.name = name
        else:
            self.name = variable.name



class DistanceMatrix(fMatrix):
    """Distance matrix """
    def __init__(self,x,y):
        n = len(x)
        ijs = ij(n)
        d = np.zeros((n,n))
        for i,j in ijs:
            d[i,j] = d[j,i] = np.sqrt( (x[i] - x[j])**2 + (y[i] - y[j])**2 )[0]
        self.values = d
        self.ijs = ijs
        self.percentiles()

    def percentiles(self):
        """determines the cumulative frequencies for the sorted
        non-zero distances"""
        self.v = [ self.values[index] for index in self.ijs ]
        self.vunsorted = self.v[:]
        self.v.sort()
        nv = len(self.v)
        self.v = np.array(self.v)
        pct = np.arange(nv)*1./nv
        self.pct = pct

    def pctValue(self,pct):
        """returns the pct percentile"""
        maxp = np.max(self.pct)
        if pct > maxp:
            rv = self.v[-1]
        else:
            rv = self.v[int(np.sum(self.pct <= pct))]
        return rv

    def valuePct(self,value):
        """returns the percentile represented by the value"""
        return self.pct[int(np.sum(self.v <= value))]

    def binaryThreshold(self,threshold):
        b = (self.values <= threshold)
        b = zeroDiagonal(b)
        return b

    def bThresholdRsId(self,threshold):
        b = self.binaryThreshold(threshold)
        br = rowStandardize(b)
        return br

    def continuousThreshold(self,threshold):
        mv = np.max(self.values)
        if threshold >= mv:
            c = self.values
        else:
            c = (self.values <= threshold) * self.values
        c = zeroDiagonal(c)
        return c

    def cThresholdRsId(self,threshold,exponent):
        c = self.continuousThreshold(threshold)
        id = invDistance(c,exponent)
        cr = rowStandardize(id)
        return cr

    def hybrid(self,pct=0.25,binary=1,exponent=2):
        """returns a row standardized proximity matrix where proximity
        is defined as those joins with a distance less than or equal to
        pct distance.

        Arguments (3):
            pct: the percentile cut-off for threshold distance
            binary: if (1) pre standardized values are binary, if 0 pre
                      standardized values are continuous
            exponent: distance decay exponent. ignored if binary is 1
        Returns (1):
            w: a full n by n row standardized matrix

            default is defined as those joins with distances less than
            the 1st quartile distance.

        """

        threshold = self.pctValue(pct)
        if binary:
            w = self.bThresholdRsId(threshold)
        else:
            w = self.cThresholdRsId(threshold,exponent)
        return w

    def inverseDistance(self,exponent=2):
        """Calculate inverse distance matrix
        Arguments (1):
            exponent: distance decay exponent. default 2
        Returns (1):
            w: a full n by n rows standardized distance matrix"""

        id = invDistance(self.values,exponent)
        rid = rowStandardize(id)
        return rid


class CovarianceMatrix:
    def __init__(self,variable):
        self.name = "covar_"+variable.name
        self.n = variable.n
        self.values = np.transpose(variable)
        self.variableT = self.values
        covarMat = self.cov()
        self.matType="full"
        self.values = covarMat
        self.highLow()

    def setName(self,name):
        self.name = name

    def full(self):
        return self.values

    def highLow(self,threshold=None):
        """create a binary matrix with 1 if cij > threshold, 0
        otherwise. default threshold is mean value."""
        if threshold:
            cut = threshold
        else:
            cut = np.mean(self.values)
        hl = self.values > cut
        self.binary = hl

    def cov(self):
        # our own cuz MLab is broken
        n = self.n
        ijs = ij(n)
        mat = np.zeros((n,n))
        n1 = n - 1
        for i,j in ijs:
            x = self.values[:,i]
            y = self.values[:,j]
            xd = x - np.mean(x)
            yd = y - np.mean(y)
            cv = np.sum(xd*yd)/n1
            sy = np.std(y)
            sx = np.std(x)
            mat[i,j] = cv/(sy*sx)
            mat[j,i] = mat[i,j]
        return mat


class CorrMatrix(fMatrix):
    def __init__(self,variable):
        vars = np.transpose(variable)
        self.values = np.corrcoef(vars)
        zd = zeroDiagonal(self.values.copy())
        self.zd = zd
        thresh = np.min(np.max(zd, axis=0))
        self.thresh=thresh
        self.binary = zeroDiagonal(self.values >= thresh)
        self.matType="corr"



def zeroDiagonal(matrix):
    n,k=matrix.shape
    for i in range(n): matrix[i,i] = 0
    return matrix

def rowStandardize(matrix):
    n,k=matrix.shape
    rs = np.sum(matrix, axis=1)
    den = 1./(rs + (rs==0))
    stand = np.diag(den) @ matrix
    return stand

def invDistance(matrix,exponent):
    de = matrix**exponent
    nz = de == 0
    id =  (1./(de+nz)) - nz
    return id

class GalReader(FileReader):
    def __init__(self,fileName):
        galFile= fileName + ".gal"
        FileReader.__init__(self,galFile)
        galinfo=list(map(int," ".join(self.contents).split()))
        self.galInfo = galinfo
        self.w=np.array([0,2,2])
        name = os.path.basename(fileName)
        self.w=spGalMatrix(name,galinfo)

        zeroRows = self.w.zeroRows()
        if len(zeroRows) > 0:
            mesg = "%s contains islands." %galFile
            Error(mesg)


if __name__ == '__main__':
    n = 5
    n2 = n**2
    d = np.arange(n2)
    d = np.reshape(d,(n,n))
    d[0,3]=d[3,0] = 0
    ds = full2Sparse(d)
    print(ds)

    x = list(range(100))
    y = list(range(100))

    from stars import *

    print("New Time Strings")
    a = Annual(1989,1999)
    print(a.string, a.numeric)

    q = SubAnnual(2, 1999, 3, 2002, 4)
    print(q.string, q.numeric)
    m = SubAnnual(2, 1999, 3, 2002, 12)
    print(m.string, m.numeric)

    tNames = [ "I" + str(i) for i in range(10) ]
    i = Irregular(10, tLabels = tNames)
    print(i.string, i.numeric)

    i2 = Irregular(9, tLabels = tNames)
    print(i2.string, i2.numeric)

    g=GalReader("data/ecu138")
