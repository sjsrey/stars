"""
Map/Distribution binning classes for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

"""


from numpy.oldnumeric import *
from numpy.oldnumeric.mlab import *

def ranki(x):
    rx=sort(x)
    rxl=rx.tolist()
    return array([ rxl.index(i) for i in x])


def empiricalQuintile(x):
    """Quintiles"""
    n=len(x)
    rx=ranki(x)+1
    return rx/(n+1.)

def percentileMap(x,trim=0.01):
    c1=trim
    c2=0.10
    c3=0.50
    c4=0.90
    c5=1.0-trim
    c6=1.0
    q=empiricalQuintile(x)
    bins=array([c1,c2,c3,c4,c5,c6])
    binIds=searchsorted(bins,q)
    counts = [ sum(binIds==i) for i in range(6) ]
    return((binIds,counts,bins))

def boxMap(x,hinge=1.5):
    q=empiricalQuintile(x)
    i1=sum(q<=0.25)
    i3=sum(q<=0.75)
    sx=sort(x)
    q1=sx[i1]
    q3=sx[i3]
    iqr=q3-q1
    lb=q1-hinge*iqr
    up=q3+hinge*iqr
    n=len(x)
    c5 = sum(x<up)*1./n
    c1=sum(x<lb)*1./n
    c2=0.25
    c3=0.50
    c4=0.75
    c5=c5
    c6=1.0
    q=empiricalQuintile(x)
    bins=array([c1,c2,c3,c4,c5,c6])
    binIds=searchsorted(bins,q)
    counts = [ sum(binIds==i) for i in range(6) ]
    if c1>=c2:
        c1=0.0
        counts[1]=counts[0]
        counts[0]=0
        bins[0]=0.0
    #print i1,i3
    #print iqr,lb,q1,q3,up,max(x)
    #print hinge
    #print sum(x>up)
    #print counts
    #print bins
    return((binIds,counts,bins))

    
class Classifier:
    """Generates intervals to classify a series using a variety of
    common approaches.

   Example Usage:
    """

    def __init__(self,x,method="sturges",nBins=5,bins=[],hinge=1.5, trim=0.01):

        self.n = len(x)
        self.x = x
        xs = x.tolist()
        xs.sort()
        self.xs = xs
        self.maxX = max(x) 
        self.minX = min(x)
        self.rangeX = self.maxX - self.minX
        self.bins = bins
        self.nBins = nBins
        self.method = method
        if bins:
            method = "userDefined"

        self.methods = {}
        self.methods["sturges"] = self.sturges
        self.methods["equalWidth"] = self.equalWidth
        self.methods["userDefined"] = self.userDefined
        self.methods["equalCount"] = self.equalCount
        self.methods["stdev"] = self.stdev
        self.methods["percentiles"] = self.percentiles
        self.methods["uniqueValues"] = self.uniqueValues

        #XXX kludge before refactoring
        if self.method=="boxMap":
            res=boxMap(x,hinge)
            self.binCounts = res[1]
            self.binIds = res[0]
            self.nBins = len(res[1])
            self.bins=res[2]
        elif self.method=="percentileMap":
            res=percentileMap(x,trim)
            self.binCounts = res[1]
            self.binIds = res[0]
            self.nBins = len(self.binCounts)
            self.bins=res[2]

        else:
            self.methods[method]()
            self.binIds = searchsorted(self.bins,self.x)
            if max(self.binIds == nBins):
                # numpy bug workaround, equality is failing and max value is
                # treated as larger than maximum bin value. so set maximum bin
                # value equal to max value.
                self.bins[-1]=max(self.x)
                self.binIds = searchsorted(self.bins,self.x)
            counts = [ sum(self.x <= cut) for cut in self.bins]
            #print "method used: ",method
            self.binCumulativeCounts = counts
            counts = array(counts)
            c1 = [counts[0]]
            c1.extend(counts[1:] - counts[:-1])
            self.binCounts = c1
            self.nBins = len(self.bins)

        


    def sturges(self):
        print "Sturges"
        self.nBins = int(1 + log(self.n)) + 1
        #w = self.rangeX / (self.nBins-1)
        w = self.rangeX / (self.nBins)
        self.w = w
        bins = arange(self.minX+w,self.maxX+2*w,w)
        if bins[-1] < self.maxX:
            #print "low max bin"
            a=raw_input()
        self.bins = bins
    

    def equalWidth(self):
        print "equalWidth"
        w = self.rangeX / self.nBins
        self.w = w
        bins = arange(self.minX+w,self.maxX+w,w)
        self.bins = bins


    def userDefined(self):
        print "userDefined"
        if max(self.x) > self.bins[-1]:
            print "Warning maximum X value exceeds upper bin"
            print "Extending bins accordingly"
            self.bins = self.bins
            self.bins.extend([max(self.x)])

    def equalCount(self):
        """qunitile if nBins=5 (default)"""
        try:
            #print self.nBins
            nk = self.n / self.nBins
            xs = sort(self.x)
            self.xs = xs
            bins = range(nk,self.n,nk)
            self.bins = [xs[rk-1] for rk in bins]
            if self.bins[-1] < self.maxX:
                self.bins.append(self.maxX)

        except:
            print "equalCount warning:"
            print "Number of bins has to be specified."
            print "Default method used instead."
            self.bins=[]
            self.sturges()

    def percentiles(self):
        #print "percentiles called"
        n = self.n
        n1 = n - 1
        pc = 1./self.nBins
        nBin = self.nBins
        ps = arange(pc,1+pc,pc)
        ps = ps[0:nBin]
        ni = [ int(ceil(n1 * p)) for p in ps]
        bins = [ self.xs[i] for i in ni]
        self.pc =ps
        self.ni = ni
        self.bins = bins

    def uniqueValues(self):
        #print "unique values called"
        x = self.x
        binsDict = {}
        for i in x:
            if binsDict.has_key(i):
                binsDict[i].append(i)
            else:
                binsDict[i] = [i]
        bins = binsDict.keys()
        bins.sort()
        self.bins = bins




    def stdev(self):
        x = self.x
        print x.shape
        xbar =mean(x)
        #print type(x),type(xbar)
        #roll our own std function as MLab std changed from version 21.0
        #to 21.3
        xr = reshape(x,(len(x),1))
        s = std(xr)
        #print s,xbar
        #s = sqrt(cov(x))
        z = (x-xbar)/s[0]
        maxZ = max(z)
        if maxZ > 1.5:
            bins = array([-1.5, -0.5, 0.0, 0.5, 1.5, maxZ])
        else:
            bins = array([ -1.5, -0.5, 0.0, 0.5, 1.5])
        self.bins = bins
        self.x = z
   
class BoxClass:
    """ """
    def __init__(self,x,fence=1.5):
        med = median(x)
        self.x=x
        xs = sort(x)
        n=len(x)
        ids = arange(n)
        q1n = int(n * 0.25)
        q3n = int(n * 0.75)
        q1 = xs[q1n]
        q3 = xs[q3n]
        iqr = q3 - q1
        pivot = fence * iqr
        fenceLow = q1 - pivot
        fenceHigh = q3 + pivot
        bins = array([fenceLow,q1,med,q3,fenceHigh])
        self.bins = bins
        self.binIds = searchsorted(bins,x)
        maxBinId = max(self.binIds)
        self.maxX = xs[-1]
        self.minX = xs[0]
        if maxBinId == 5:
            self.highOutliers = compress(greater(x,fenceHigh),ids)
        else:
            self.highOutliers = []

        minBinId = min(self.binIds)
        if minBinId == 0:
            self.lowOutliers = compress(less(x,fenceLow),ids)
        else:
            self.lowOutliers = []

        self.lowBoxIds = compress(equal(self.binIds,2),ids)
        self.highBoxIds = compress(equal(self.binIds,3),ids)
        counts = [ sum(self.x <= cut) for cut in self.bins]
        if len(counts) > len(self.bins):
            counts.append(self.n)
        self.binCounts = counts


if __name__ == '__main__':
    from numpy.oldnumeric import *
    from numpy.oldnumeric.random_array import *

    import doctest,classifier
    doctest.testmod(classifier)

    x=normal(50,10,100)
    xi = array([ int(x[i]) for i in range(100) ])
    xuv = Classifier(xi,method="uniqueValues")
    xp7 = Classifier(x,method="percentiles",nBins=7)
    xp6 = Classifier(x,method="percentiles",nBins=6)

    xs = Classifier(x, method = "stdev")
    xp = Classifier(x,method = "percentiles")
    xn = normal(50,100,48)

    newX = arange(100)
    newX = Classifier(newX,method="equalWidth",nBins=4)


    xb= BoxClass(x)

    nbin = 4
    #for i in range(1000):
    #    x=normal(50,20,100)
    #    xs = Classifier(x, method = "equalWidth",nBins =nbin)
    #    nb = xs.bins.tolist()
    #    minx = min(x)
    #    t= [minx]
    #    nb = t.extend(nb)
    #    nb = t

    #    if len(xs.bins) != nbin:
    #        #print i
    #        nb = xs.bins.tolist()
    #        minx = min(xs)
    #        t= [minx]
    #        nb = t.extend(nb)
    #        #print nb
    #        #print xs.bins
    #        raw_input("pause")

