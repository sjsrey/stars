"""
Data and Matrix Classes
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Boris Dev     bdev@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006 Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================
"""

from numpy.oldnumeric import *
from numpy.oldnumeric.mlab import *
from numpy.oldnumeric.user_array import *
from copy import copy
import os.path

# stars modules
import Utility
from stars import *
from Errors import *
            
def csts(values,n,t):
    values = array(values)
    values = reshape(values,[n,t])
    return values

def tscs(values,n,t):
    values = array(values)
    values = reshape(values,[t,n])
    values = transpose(values)
    return values

def cs(values,n,t):
    return reshape(array(values),[n,1])

def ts(values,n,t):
    return reshape(array(values),[t,1])

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
        ids = winfo.keys()
        ids.sort()
        n = len(ids)
        ylag = []
        for id in ids:
            i = winfo[id]
            nNeighbors = i[0] * 1.
            neighbors = i[1]
            nsum = sum(take(y,neighbors)) / nNeighbors 
            ylag.append(nsum)
    else:
        w = wsp.full()
        ylag = matrixmultiply(w,y)
        ylag = ylag.tolist()
    return ylag

class Variable(UserArray):
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
    def __init__(self,values):
        UserArray.__init__(self,values)
        self.id = id(self)
        self.note = ""
        dim = self.shape
        self.n = dim[0]
        if len(dim) == 2:
            self.t = dim[1]
        else:
            self.t = 1
        
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

class SVariable(UserArray):
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
    def __init__(self,values):
        UserArray.__init__(self,values)
        self.id = id(self)
        self.note = ""
        dim = self.shape
        self.n = dim[0]
        if len(dim) == 2:
            self.t = dim[1]
        else:
            self.t = 1
        
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
        vnames = info.keys()
        self.varNames = vnames
        dataDict = {}
        for i in vnames:
            var = info[i]
            varType = var[0].upper()
            values = var[1]
            n=var[2][0]
            t=var[2][1]
            values = apply(varMenu[varType],[values,n,t])
            variable = Variable(values)
            variable.setName(i)
            #print i
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
        self.numeric = range(startTime,finishTime,inc)
        self.string = map(repr,self.numeric)
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
        print self.timeSummary

class Decadal(TimeString):
    """Labels for decadal time series """
    def __init__(self,startTime,finishTime,inc=10):
        TimeString.__init__(self,"ANNUAL")
        startTime = int(startTime)
        finishTime = int(finishTime)
        finishTime = finishTime+1
        self.numeric = range(startTime,finishTime,inc)
        self.string = map(repr,self.numeric)
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
        print self.timeSummary

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
        self.numeric = range(len(time))
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
        print self.timeSummary
        
class Irregular(TimeString):
    """Labels for irregular time periods:
        Arguments:
        t: number of time periods
        tLabels: optional argument, list of irregular time period names
    """
    def __init__(self,t,tLabels=[]):
        TimeString.__init__(self,"IRREGULAR")
        self.numeric = range(1,t+1)
        self.timeType = "IRREGULAR"
        if len(tLabels) == t:
            self.string = tLabels
        else:
            print "Number of labels do not match the number of time periods.\nUsing integers to represent irregular time periods."
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
        print self.timeSummary

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
        
        #print "header", self.header
        self.timeInfo = self.header[0].split()
        self.timeFreq = self.timeInfo[0].upper()
        self.timeFreq = self.timeFreq.strip()
        if self.timeFreq == "IRREGULAR":
            t = int(self.timeInfo[-1])
            self.timeClass = Irregular(t)
        else:
            self.timeClass = apply(timeFreqMenu[self.timeFreq],self.timeInfo[1:])
        regionInfo = self.header[1:]
        self.regionType = regionInfo[0].strip()
        self.regionNames = map(string.strip,regionInfo[1:])
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
        #print self.contents[0:20]
        lIndex = []
        #print self.varNames
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
            vals = map(float,vals)
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
        #print self.dict
        n = len(self.dict)
        w = zeros([n,n],Float)
        ids = self.dict.keys()
        for id in ids:
            neighborids = self.dict[id][1]
            nNeighbors = self.dict[id][0]
            vals = ones([1,nNeighbors],Float) * 1./nNeighbors
            put(w[id,],neighborids,vals)
        return w
    
    def setName(self,name):
        self.name = name

    def zeroRows(self):
        """Returns a list of row indices with zero sums.
        """
        full = greater(self.full(),0)
        rowSums = sum(full,axis=1)
        zeroRows = equal(rowSums,0.0)
        numZeros = sum(zeroRows)
        if numZeros > 0:
            return argsort(zeroRows)[-numZeros:].tolist()
        else:
            return []

    def islands(self):
        ids = self.dict.keys()
        islands = [ id for id in ids if self.dict[id][0]==0 ]
        return islands


    def  symmetryCheck(self):
        """Returns 1 if matrix is symmetric, 0 otherwise."""
        full = greater(self.full(),0)
        comp = not_equal(full,transpose(full))
        if sum(sum(comp)) == 0:
            return 1
        else:
            return 0

    def asymmetricRows(self):
        """Returns a list of row indices of asymetries.
        """
        full = greater(self.full(),0)
        comp = not_equal(full,transpose(full))
        rowSums = sum(comp,axis=1)
        rows = greater(rowSums,0.0)
        numRows = sum(rows)
        if numRows > 0:
            return argsort(rows)[-numRows:].tolist()
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
        >>> galinfo = map(int,"".join(ws).split())
        >>> name="wsp"
        >>> wsp = spGalMatrix(name,galinfo)
    """
    def __init__(self,name,galInfo):
        spMatrix.__init__(self,name)
        self.n=galInfo[0]
        #print galInfo

        #print self.n
        id=1
        for i in range(self.n):
            rid = galInfo[id] 
            nNeighbors = galInfo[id+1]
            neighbors = galInfo[id+2:id+2+nNeighbors]
            self.dict[rid] = [nNeighbors, array(neighbors)]
        #    print "Record Info"
        #    print i,rid,nNeighbors,neighbors
            id += 2+nNeighbors 
        #    raw_input("wait")

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
        ra = take(regions,range(len(regions)))
        rids = Utility.unique(ra)
        for r in rids:
            members = nonzero(ra[:,0]==r)
            for member in members:
                neighbors = take(members,nonzero(members!=member))
                self.dict[member] = [len(neighbors),neighbors]
        self.setName(regions.name)

def full2Sparse(fullMatrix):
    # returns sparse binary representation of a full matrix
    # requires python 2.2
    # nonzero values are treated as binary 1
    n,k = shape(fullMatrix)
    d = {}
    ij = [ (i,j) for i in range(n-1) for j in range(i+1,n) ]

    for i,j in ij:
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

    rn = range(n)
    return [ (i,j) for i in rn[0:-1] for j in rn[i+1:n] ]

class Regime:
    """Zero offset of a STARS variable intended for use as a regime"""
    def __init__(self, variable, name=None):
        """variable: a cs variable."""
        uid = dict( [ (i,i) for i in variable[:,0] ] )
        n = len(variable)
        rn = range(n)
        uids = uid.keys()
        uids.sort()
        bridge = dict( [ (i,uids.index(variable[i,0])) for i in rn ] ) 
        self.bridge=bridge
        self.uids = uids
        self.partition = bridge.values()
        if name:
            self.name = name
        else:
            self.name = variable.name
        





class DistanceMatrix(fMatrix):
    """Distance matrix """
    def __init__(self,x,y):
        n = len(x)
        ijs = ij(n)
        d = zeros((n,n),Float)
        for i,j in ijs:
            d[i,j] = d[j,i] = sqrt ( (x[i] - x[j])**2 + (y[i] - y[j])**2 )[0]
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
        self.v = array(self.v)
        pct = arange(nv)*1./nv
        self.pct = pct

    def pctValue(self,pct):
        """returns the pct percentile"""
        maxp = max(self.pct)
        if pct > maxp:
            rv = self.v[-1]
        else:
            rv = self.v[sum(self.pct <= pct)]
        return rv

    def valuePct(self,value):
        """returns the percentile represented by the value"""
        return self.pct[sum(self.v <= value)]

    def binaryThreshold(self,threshold):
        b = (self.values <= threshold)
        b = zeroDiagonal(b)
        return b

    def bThresholdRsId(self,threshold):
        b = self.binaryThreshold(threshold)
        br = rowStandardize(b)
        return br

    def continuousThreshold(self,threshold):
        mv = max(max(self.values))
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
        self.values = transpose(variable)
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
            cut = mean(mean(self.values))
        hl = self.values > cut 
        self.binary = hl

    def cov(self):
        # our own cuz MLab is broken
        n = self.n
        ijs = ij(n)
        mat = zeros((n,n),Float)
        n1 = n - 1
        for i,j in ijs:
            x = self.values[:,i]
            y = self.values[:,j]
            xd = x - mean(x)
            yd = y - mean(y)
            cv = sum(xd*yd)/n1
            sy = std(y)
            sx = std(x)
            mat[i,j] = cv/(sy*sx)
            mat[j,i] = mat[i,j]
        return mat


class CorrMatrix(fMatrix):
    def __init__(self,variable):
        vars = transpose(variable)
        self.values = corrcoef(vars)
        zd = zeroDiagonal(self.values)
        self.zd = zd
        thresh = min(max(zd))
        self.thresh=thresh
        self.binary = zeroDiagonal(self.values >= thresh)
        self.matType="corr"



def zeroDiagonal(matrix):
    n,k=shape(matrix)
    for i in range(n): matrix[i,i] = 0
    return matrix

def rowStandardize(matrix):
    n,k=shape(matrix)
    rs = sum(matrix,1)
    den = 1./(rs + (rs==0))
    stand = matrixmultiply(diag(den),matrix)
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
        galinfo=map(int," ".join(self.contents).split())
        self.galInfo = galinfo
        self.w=array([0,2,2])
        name = os.path.basename(fileName)
        self.w=spGalMatrix(name,galinfo)

        #if self.w.symmetryCheck() == 0:
        #    mesg = "%s is not symmetric." %galFile
        #    Error(mesg)
    
        zeroRows = self.w.zeroRows()
        if len(zeroRows) > 0:
            mesg = "%s contains islands." %galFile
            Error(mesg)


if __name__ == '__main__':
    #import doctest, Data 
    #doctest.testmod(Data)
    n = 5
    n2 = n**2
    d = arange(n2)
    d = reshape(d,(n,n))
    d[0,3]=d[3,0] = 0
    ds = full2Sparse(d)
    print ds

    x = range(100)
    y = range(100)
    #d = DistanceMatrix(x,y)
    #cr = d.cThresholdRsId(4,2)

    #d = DistanceMatrix(range(4),range(4))

    from stars import *
    #s = Project("s")
    #s.ReadData("csiss")
    #y = s.getVariable("pcr")
    #w = CorrMatrix(y)

    print "New Time Strings"
    a = Annual(1989,1999)
    print a.string, a.numeric

    q = SubAnnual(2, 1999, 3, 2002, 4)
    print q.string, q.numeric
    m = SubAnnual(2, 1999, 3, 2002, 12)
    print m.string, m.numeric

    tNames = [ "I" + str(i) for i in range(10) ]
    i = Irregular(10, tLabels = tNames)
    print i.string, i.numeric

    i2 = Irregular(9, tLabels = tNames)
    print i2.string, i2.numeric

    g=GalReader("data/ecu138")
    

