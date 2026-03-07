"""
Classic Markov Chains and Spatial Markov classes
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Charlotte Coulter coulter@rohan.sdsu.edu
----------------------------------------------------------------------

OVERVIEW

Markov chains for the analysis of distributional transitions.

Classes:
       Quntilizer
       ClMarkov
       SpMarkov
       LocalMarkov
"""
import numpy as np
import giddy.markov as _gm
# stars imports
from stars import *
from Data import *
from Messages import *
from Utility import *
import pdf


def histogram(a,bins):
    n = np.searchsorted(np.sort(a), bins)
    n = np.concatenate([n, [len(a)]])
    return n[1:]-n[:-1]

def centile(array,k):
    """Calculate the kth centile value of an array.

    Arguments:

    array -- an array of values

    k -- the kth centile value (int).

    Returns:

    centile -- the value associated with the kth centile value (float).


    """
    n=len(array)
    q = k*(n+1)/100.0
    n1 = int(np.floor(q))
    n2 = int(np.ceil(q))
    r= q - n1
    sa = np.sort(array)
    n1 = n1 - 1
    n2 = n2 - 1
    centile = sa[n1] + r * (sa[n2]-sa[n1])
    return centile

def fullQuint(variable):
    """determines quintile values by vectorizing a csts to a cs (or ts)
    variable."""
    bins=np.arange(20,100,20)
    n=variable.n
    t=variable.t
    v=np.reshape(variable,[n*t,1])
    vs=np.sort(v[:,0])
    q = [centile(vs,x) for x in bins]
    return q

class Quintilizer:
    """Transforms an array into its quintile representation.

    ATTRIBUTES:

     classes -- an array of integer values denoting quintile membership.

     quintiles -- the bins of the quintiles.

    """
    def __init__(self,array):
        self.array = array
        b = np.arange(20,100,20)
        q = [centile(array,x) for x in b]
        qclass = np.searchsorted(q,array)
        self.classes = qclass
        self.quintiles = q

class ClMarkov:
    """Classic Markov chain model class

    """
    def __init__(self,variable,bins=[],standardize=[],interval=1,start=0,finish=0,full=0):
        """Builds markov transition matrix

        Arguments:

        variable -- CSTS variable


        Keyword Arguments:

        variable --  CSTS variable.
        bins -- cut-offs for classes (default=quintiles from first period)
        standardize --  array of same time length as variable to serve as numeraire
        interval --   width of the period of transition, (default = 1)
        start --  first period (default = first time period in variable)
        finish -- ending period (default = last period in variable)
        full -- if 1 use quintiles from each period, other options ignored.


        Attributes:

        bins -- cut-off for classes (array)
        interval -- length of transition interval (int)
        start -- first time period (int)
        finish -- last time period (int)
        k -- number of classes (int)
        classes -- class value for each observation (array)
        stand -- standardized values used in classification (array)

        Example Usage:

        >>> from stars import Project
        >>> s=Project("s")
        >>> s.ReadData("csiss")
        >>> income=s.getVariable("pcincome")
        >>> ym=ClMarkov(income)
        >>> ym.transMat
        array([[ 167,   20,    0,    0,    0],
               [  11,  754,   60,    1,    0],
               [   0,   53,  856,   74,    0],
               [   0,    1,   75, 1045,   24],
               [   0,    0,    0,   30,  237]])

        """

        self.variable = variable
        if full:
            tv=np.transpose(variable)
            c=np.transpose(np.array([Quintilizer(x).classes for x in tv]))
            b=np.transpose(np.array([Quintilizer(x).quintiles for x in tv]))
            self.classes = c
            self.bins = b[:,1]
        else:

            if bins:
                if standardize:
                    self.stand = self.variable/(standardize)
                else:
                    self.stand = self.variable/np.mean(self.variable)
                self.bins = bins


            else:
                if standardize:
                    self.stand = self.variable/(standardize)

                else:
                    self.stand = self.variable/np.mean(self.variable)

                self.quints = Quintilizer(self.stand[:,start])
                self.bins = self.quints.quintiles


            maxval = np.max(self.stand)
            if max(self.bins) < maxval:
                self.bins.append(maxval)

            self.classes = np.searchsorted(self.bins,self.stand)
            k = len(self.bins)
            maxk = np.max(self.classes)
            upperBound = np.max(self.stand)
            if type(self.bins) !=type([]):
                self.upperBounds = self.bins.tolist()
            else:
                self.upperBounds = self.bins

        if finish:
            self.finish = finish
        else:
            self.finish = self.variable.t

        k = len(self.bins)
        transMat = np.zeros([k,k], dtype=int)
        rangen = range(self.variable.n)
        matchMat = dict( [((i,j),[ set(),set() ]) for i in range(k)
                    for j in range(k) ] )
        self.matchMat=matchMat
        for time0 in range(start,self.finish-interval,1):
            time1 = time0 + interval
            for r in rangen:
                rowid = self.classes[r,time0]
                colid = self.classes[r,time1]
                transMat[rowid,colid] += 1
                matchMat[(rowid,colid)][0].add(r)
                matchMat[(rowid,colid)][1].add(time0)
        self.interval = interval
        self.start = start
        self.transMat = transMat
        self.k=k
        self.pMat = self.t2pMat(self.transMat)
        self.edist = self.ergodic(self.pMat)

    def t2pMat(self,mat):
        """Transform a transition matrix to a row standardized
        probability matrix."""
        rsum = np.sum(mat, axis=1)
        rsum = rsum + np.where(rsum==0,1,0)
        pMat = np.diag(1./rsum) @ mat
        return pMat

    def ergodic(self,pmatrix):
        """Calculates the steady state distribution via giddy.

        Returns a 1-D array of length k. For reducible chains with
        multiple recurrent classes, averages the per-class distributions.
        """
        try:
            ss = _gm.steady_state(pmatrix, fill_empty_classes=True)
            ss = np.atleast_2d(ss)
            return ss.mean(axis=0)
        except Exception:
            return np.full(pmatrix.shape[0], 1.0 / pmatrix.shape[0])

    def convergeTable(self):
        c = self.classes
        k = self.k
        mp = (k+1)//2
        i = self.interval
        first = c[:,0:-i]
        last = c[:,i:]
        diff = last - first
        below = first < mp
        above = first > mp
        middle = first == mp

        down = diff < 0
        up = diff > 0
        nc = diff == 0

        dd = (middle + below) * down
        uc = below * up
        dc = above * down
        ud = (middle + above) * up


        summary = dd + uc * 2 + dc * 4 + ud * 5
        summary = (summary==0)* 3 + summary
        self.conSumTable = summary


        # 1 downwardly divergent
        # 2 upwardly convergent
        # 3 stationary
        # 4 downwardly convergent
        # 5 upwwardly divergent

        # classify based on largest relative deviation from expected
        # transition type

        c = summary
        rsum = np.transpose(np.array([ np.sum(c==x, axis=1) for x in range(1,6)]))
        csum = np.sum(rsum, axis=0)
        pc = csum *1./np.sum(csum)
        T = summary.shape[1]
        expFreq = pc * T
        pc = pc + (pc == 0)
        self.conTab = rsum
        ef = np.diag(1./(expFreq+(expFreq==0)))
        self.rTab = rsum @ ef
        rks = np.arange(1,6)
        a = [rks[np.nonzero(x==np.max(x))[0]][0] for x in self.rTab]
        self.conType = a

        # extreme endpoint only classification
        mp = (k+1)//2
        i = self.interval
        c=self.classes
        first = c[:,0]
        last = c[:,-1]
        diff = last - first
        below = first < mp
        above = first > mp
        middle = first == mp

        down = diff < 0
        up = diff > 0
        nc = diff == 0

        dd = (middle + below) * down
        uc = below * up
        dc = above * down
        ud = (middle + above) * up

        summary = dd + uc * 2 +  dc * 4 + ud * 5
        summary = summary + (summary == 0)*3

        self.conSumTableEnd = summary




    def report(self):
        """Pretty formatting of summary results"""
        rowLabels = self.upperBounds
        rowLabels = [ "%8.3f"%(x) for x in rowLabels]
        origin = "t\\t+%d"%self.interval
        head = "Markov Transition Probability Matrix\nVariable: %s"%self.variable.name
        tab = Table(self.pMat,head=head,
            rowNames=rowLabels,
            colNames=rowLabels,
            origin=origin).table

        head = "Markov Transition Matrix\nVariable: %s"%self.variable.name
        tab1 = Table(self.transMat,head=head,
            rowNames=rowLabels,
            colNames=rowLabels,
            origin=origin,fmt=[[8,0]]).table
        head = "Ergodic Distribution\nVariable: %s"%self.variable.name
        edist = np.reshape(self.edist,[1,len(self.bins)])
        colNames=rowLabels
        rowLabels = ["P(x)"]
        origin="x"

        tabe = Table(edist,head=head,
            rowNames=rowLabels,
            colNames=colNames,
            origin=origin).table
        tabs = "\n".join([tab,tab1,tabe])
        return(tabs)

    def match2listIds(self):
        """ Retuns a list of three lists
        keys: lists of tuples of cell ids -  (0,0) = row 0 col 0 of the
                transition matrix. keys are in a list of lenght k*k in major
                row order (first k items are row 1, k+1 to 2k items are row
                2.. and so on)
        rowIds: list of tuples of ids for observations that made that transition
                e.g. if we have (0,8,13) that means observations 0,8,13 each
                made the transition from state 0 to state 0. the order matches
                of the tuples matches that of keys.
        colIds: list of tuples of time period when transitions for a cell were
                made (initial period). the order of the tuples matches that of
                keys.
        """
        match = self.matchMat
        keys = sorted(match.keys())
        rowIds = []
        colIds = []
        for key in keys:
            lists = [ tuple(l) for l in match[key] ]
            rowIds.append(lists[0])
            colIds.append(lists[1])
        return [keys, rowIds, colIds]

class SpMarkov(ClMarkov):
    """Spatial Markov Methods """

    def __init__(self,variable,w,bins=[],standardize=[],interval=1,start=0,finish=0,full=0):
        self.variable = variable
        self.w = w
        lag = slag(self.w,variable)
        lagQuint = [Quintilizer(x) for x in np.transpose(lag)]
        self.lagClasses = np.transpose(np.array([x.classes for x in lagQuint]))

        self.varMarkov = ClMarkov(variable,bins=bins,standardize=standardize,
            interval=interval,start=start,finish=finish,full=full)
        self.classes = self.varMarkov.classes
        self.bins = self.varMarkov.bins
        self.upperBounds = self.bins
        self.varMarkov.convergeTable()
        self.conType = self.varMarkov.conType
        self.conSumTableEnd = self.varMarkov.conSumTableEnd

        lagp = lag/np.mean(lag)
        self.lagp = lagp
        lagc = np.searchsorted(self.bins,lagp)
        self.lagc = lagc

        if finish:
            self.finish = finish
        else:
            self.finish = self.variable.t
        k = len(self.bins)
        k1=k-1
        transMat = np.zeros([k,k,k], dtype=int)
        pMat = np.zeros([k,k,k])
        rangen = range(self.variable.n)
        rangeK = range(k)
        matchMat = dict( [ ((i,j,l), [ set(),set() ]) for i in rangeK
                for j in rangeK for l in rangeK ] )
        for time0 in range(start,self.finish-interval,1):
            time1 = time0 + interval
            for r in rangen:
                rowid = self.classes[r,time0]
                colid = self.classes[r,time1]
                lagmat = lagc[r,time0]
                if lagmat > k1:
                    lagmat=k1
                transMat[lagmat,rowid,colid] += 1
                key = (lagmat,rowid,colid)
                matchMat[key][0].add(r)
                matchMat[key][1].add(time0)
        self.matchMat = matchMat
        self.interval = interval
        self.start = start
        self.transMat = transMat
        self.k=k
        edists = []
        for l in range(k):
            tmat = transMat[l,:,:]
            pmat = self.t2pMat(tmat)
            pMat[l,:,:] = pmat
            edists.append(self.ergodic(pmat))
        self.pMat = pMat
        self.edists = np.array(edists)


    def report(self):
        """Pretty formatting of summary results"""
        ptabs = []
        ntabs = []
        rowLabels = self.upperBounds
        colLabels = self.upperBounds
        origin="t\\t+%d"%self.interval
        for l in range(self.k):
            tmat = self.transMat[l,:,:]
            pmat = self.t2pMat(tmat)
            head = "Spatial Markov Transition Probability Matrix\nVariable: %s"%self.variable.name
            head = "%s\nInterval: %d\nLag Class%8.3f"%(head,self.interval,self.upperBounds[l])
            tab = Table(pmat,head=head,
                rowNames=rowLabels,
                colNames=colLabels,
                origin=origin).table
            ptabs.append(tab)
            head = "Spatial Markov Transition Matrix\nVariable: %s"%self.variable.name
            head = "%s\nInterval: %d\nLag Class%8.3f"%(head,self.interval,self.upperBounds[l])
            tab = Table(tmat,head=head,
                rowNames=rowLabels,
                colNames=colLabels,
                origin=origin,fmt=[[8,0]]).table
            ntabs.append(tab)


        head="Ergodic Distributions\nVariable: %s"%self.variable.name
        head="%s\nInterval: %d"%(head,self.interval)
        origin="Lag\\P(x)"
        rowLabels = self.upperBounds
        rowLabels = [ "%8.3f"%(x) for x in rowLabels]
        colNames = rowLabels
        tabe = Table(self.edists,head=head,
            rowNames=rowLabels,
            colNames=colNames,
            origin=origin).table
        ptabs.extend(ntabs)
        ptabs.append(tabe)
        return("\n".join(ptabs))

class LocalTrans(ClMarkov):
    """Transition matrix of local moran statistics"""
    def __init__(self,variable,w,interval=1,start=0,finish=0):
        self.variable = variable
        self.w = w
        self.interval = interval
        lag = slag(w,variable)
        self.lag = lag
        xbar = np.mean(variable)
        stand = variable/xbar
        lagStand = lag/xbar
        blag = (lagStand > 1.0)
        b = (stand > 1.0)
        q1 = blag * b
        q2 = blag * (1-b)
        q3 = (blag==0) * (b==0)
        q4 = (blag==0) * b
        q = q1 + q2 * 2 + q3 * 3 + q4 * 4
        q = q - 1
        self.q = q

        #Classic Markov Calls
        self.varMarkov = ClMarkov(variable)
        self.varMarkov.convergeTable()
        self.conType = self.varMarkov.conType
        self.conSumTableEnd = self.varMarkov.conSumTableEnd


        #local class region by time
        self.local = np.array([histogram(x,np.arange(4)) for x in self.q])

        transMat = np.zeros([4,4], dtype=int)
        regMat = np.zeros([self.variable.n,4,4], dtype=int)
        rangen = range(self.variable.n)
        matchMat = dict( [((i,j),[ set(),set() ]) for i in range(4)
                    for j in range(4) ] )
        if finish:
            self.finish = finish
        else:
            self.finish = self.variable.t
        for time0 in range(start,self.finish-interval,1):
            time1 = time0 + interval
            for r in rangen:
                rowid = q[r,time0]
                colid = q[r,time1]
                transMat[rowid,colid] +=1
                regMat[r,rowid,colid] +=1
                matchMat[(rowid,colid)][0].add(r)
                matchMat[(rowid,colid)][1].add(time0)
        self.transMat = transMat
        self.matchMat = matchMat

        self.regMat = regMat

        rsum = np.sum(transMat, axis=1)
        rsum = rsum + np.where(rsum==0,1,0)
        pmat = np.diag(1./rsum) @ transMat
        self.pmat = pmat
        self.edist = self.ergodic(pmat)
        nTrans = np.sum(self.transMat)
        nType0 = np.sum(np.diag(self.transMat))
        T=self.transMat
        nTypeI =   T[0,1] + T[1,0] + T[2,3] + T[3,2]
        nTypeII =  T[3,0] + T[2,1] + T[1,2] + T[0,3]
        nTypeIII = T[2,0] + T[3,1] + T[0,2] + T[1,3]
        nTypes = [nType0,nTypeI,nTypeII,nTypeIII]
        self.nTypes = np.array(nTypes)
        self.nTrans = nTrans
        self.pTypes = self.nTypes*1./nTrans
        self.cohesion = nType0 + T[2,0] + T[0,2]
        self.pCohesion = self.cohesion*1./nTrans
        self.flux = nTypeI + nTypeII
        self.pFlux = self.flux *1./nTrans

    def mobilitySum(self,tMat):
        nTrans = np.sum(tMat)
        nType0 = np.sum(np.diag(tMat))
        T=tMat
        nTypeI =   T[0,1] + T[1,0] + T[2,3] + T[3,2]
        nTypeII =  T[3,0] + T[2,1] + T[1,2] + T[0,3]
        nTypeIII = T[2,0] + T[3,1] + T[0,2] + T[1,3]
        nTypes = [nType0,nTypeI,nTypeII,nTypeIII]
        nTypes = np.array(nTypes)
        pTypes = nTypes *1. / nTrans
        return pTypes

    def report(self):
        rowLabels = ["HH","LH","LL","HL"]
        origin = "t\\t+%d"%self.interval
        head = "Local Moran Transition Probability Matrix\nVariable: %s"%self.variable.name
        head = "%s\nWeight Matrix: %s\nInterval: %d"%(head,self.w.name,self.interval)
        ptab = Table(self.pmat,head=head,
            rowNames=rowLabels,
            colNames=rowLabels,
            origin=origin).table
        hn = head.replace("Probability ","")
        ntab = Table(self.transMat,head=hn,
            rowNames=rowLabels,
            colNames=rowLabels,
            origin=origin,fmt=[[8,0]]).table
        edist=np.reshape(self.edist,[1,4])
        etab = Table(edist,head="Local Ergodic Distribution",
                colNames=rowLabels,
                rowNames=["P(l)"],origin="").table

        head = "Local Moran Transition Summary Measures\nVariable: %s"%self.variable.name
        head = "%s\nWeight Matrix: %s\nInterval: %d"%(head,self.w.name,self.interval)
        t1 = np.concatenate((self.nTypes,self.pTypes))
        t2 = np.reshape(t1,[2,4])
        t3 = np.transpose(t2)
        colLabels = ["n","P(Type)"]
        rowLabels = ["Type 0","Type I","Type II", "Type III",]
        sumtab = Table(t3,head=head,
            rowNames=rowLabels,
            colNames=colLabels,fmt=[[8,0],[8,3]]).table

        so = "\n\n".join([ptab,etab,ntab,sumtab])
        so = "%s\n\nSpatial Flux: %8.3f\nSpatial Cohesion: %8.3f"%(so,self.pFlux,self.pCohesion)

        rpTypes = np.array([self.mobilitySum(x) for x in self.regMat])
        self.rpTypes = rpTypes
        colLabels = ["0","I","II","III"]
        origin = "Observation"
        regTab = Table(rpTypes,
            colNames = colLabels,
            rowNames = self.variable.regionNames,
            origin = origin).table
        so = "%s\n%s"%(so,regTab)

        head="Local Moran Distribution\nVariable: %s\nWeight Matrix: %s"%(self.variable.name,self.w.name)
        classTab = Table(self.local,head=head,
            rowNames=self.variable.regionNames,
            colNames=["HH","LH","LL","HL"],
            origin="Region",fmt=[[8,0]]).table

        self.classTab = classTab

        so = "%s\n%s"%(so,classTab)


        return so

def _test():
    import doctest, Markov
    return doctest.testmod(Markov)

def _example():
        from stars import Project
        s=Project("s")
        s.ReadData("csiss")
        income=s.getVariable("pcincome")
        ym=ClMarkov(income)
        ym.transMat
        s.ReadGalMatrix("states48")
        w=s.getMatrix("states48")
        sm=SpMarkov(income,w=w)
        return [ym,income.regionNames,sm]


if __name__ == "__main__":
   pass
