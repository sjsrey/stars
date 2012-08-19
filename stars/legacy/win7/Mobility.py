"""
Distributional mobility metrics
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006 Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW


Classes:
    Tau     spatial rank correlation mobility indices
    Theta   spatial cohesion indices
"""

from stars import *
from numpy.oldnumeric.random_array import permutation
from numpy.oldnumeric.mlab import *
from numpy.oldnumeric import *
from Messages import *
from pdf import *

def unique(s):
    """returns the unique values of a list.

    Example Usage:
    
    >>> x=[1,1,2,3,4,4,5]
    >>> unique(x)
    [1, 2, 3, 4, 5]
    """
    n = len(s)
    if n == 0:
        return []

    u = {}
    for x in s:
        u[x] = 1

    return u.keys()

def aUnique(s):
    """unique elements but returned as an array
    
    Example Usage:

    >>> x=range(10)
    >>> x[8]=9
    >>> x
    [0, 1, 2, 3, 4, 5, 6, 7, 9, 9]
    >>> aUnique(x)
    array([0, 1, 2, 3, 4, 5, 6, 7, 9])
    """
    return array(unique(s))

def rankValues(X,axis=0,high=0,ties=1):
    """return ranks of values in place of values by column,

    X -- n by k array of values
    axis -- 0 sort down column, 1 sort across rows
    high -- 0 lowest rank corresponds to lowest value in col/row, 1 means a
            rank of 0 corresponds to the maximum value in col/row.
    ties -- 1, tied values share a rank, 0 arbitrary numeric ranking
            for tied values.

    Example Usage:

        >>> x=arange(16)
        >>> x=reshape(x,(8,2))
        >>> x
        array([[ 0,  1],
               [ 2,  3],
               [ 4,  5],
               [ 6,  7],
               [ 8,  9],
               [10, 11],
               [12, 13],
               [14, 15]])
        >>> rankValues(x)
        array([[ 0.,  0.],
               [ 1.,  1.],
               [ 2.,  2.],
               [ 3.,  3.],
               [ 4.,  4.],
               [ 5.,  5.],
               [ 6.,  6.],
               [ 7.,  7.]])
        >>> x[2,1]=1
        >>> x
        array([[ 0,  1],
               [ 2,  3],
               [ 4,  1],
               [ 6,  7],
               [ 8,  9],
               [10, 11],
               [12, 13],
               [14, 15]])
        >>> rankValues(x)
        array([[ 0. ,  0.5],
               [ 1. ,  2. ],
               [ 2. ,  0.5],
               [ 3. ,  3. ],
               [ 4. ,  4. ],
               [ 5. ,  5. ],
               [ 6. ,  6. ],
               [ 7. ,  7. ]])
        >>> rankValues(x,high=1)
        array([[ 7. ,  6.5],
               [ 6. ,  5. ],
               [ 5. ,  6.5],
               [ 4. ,  4. ],
               [ 3. ,  3. ],
               [ 2. ,  2. ],
               [ 1. ,  1. ],
               [ 0. ,  0. ]])
        >>>
        """

    if axis!=0:
        X=transpose(X)
    n,t = shape(X)
    T=range(t)
    N=range(n)
    arg = transpose(argsort(X,axis=0))
    rks = array([ nonzero(arg[t]==i)[0] for i in N for t in T]) *1.
    rks = reshape(rks,(n,t+1))
    if ties:
        arg = transpose(rks)
        z = zip(T,transpose(X))
        for j,col in z:
            nu = aUnique(col)
            if len(nu) < n:
                col = list(col)
                dups = unique([ val for val in col if col.count(val) > 1])
                col = array(col)
                ids =  [ nonzero(col==i) for i in dups ]
                for id in ids:
                    oldRanks = ([ rks[i,j] for i in id ])
                    avgRank = mean(oldRanks)
                    for i in id:
                        rks[i,j] = avgRank

    if high:
        rks = abs(rks - n ) - 1

    return rks

class Tau:
    """Classic Tau rank correlation

    Arguments:
        variable: STARS variable
        interval: integer for length of time interval (default=1)
        w:  STARS sparse weight matrix (optional)
        permutations: number of perumtations for inference (default=0)
    
    Attributes:
        concord: number of concordant pairs for each period
        discord: number of disconcordant pairs for each period
        T:  number of unique pairs
        tau:    tau statistic (concord/T) for each period

        (if w is specified)
        nContiguities: number of unique contiguous pairs
        contConcordCount: number of contiguous concordant pairs
        contTau:    tau statistic for contiguous pairs
        nonContConcordCount: number of noncontiguous concordant pairs
        nonContTau:    tau statistic for noncontiguous pairs

    Example Useage:
    >>> from stars import Project
    >>> s=Project('s')
    >>> s.ReadData('data/csiss')
    >>> y=s.getVariable('pcincome')
    >>> tau=Tau(y)
    >>> tau.tau
    array([ 0.94148936,  0.90780142,  0.93085106,  0.91489362,  0.91134752,  0.83687943,
                 0.88297872,  0.88829787,  0.91666667,  0.93971631,  0.96985816,
                 0.93262411,  0.85460993,  0.88297872,  0.89893617,  0.90248227,
                 0.88652482,  0.85815603,  0.83510638,  0.81737589,  0.91312057,
                 0.92730496,  0.92021277,  0.91843972,  0.94148936,  0.91666667,
                 0.94503546,  0.91666667,  0.91489362,  0.91843972,  0.93794326,
                 0.94858156,  0.91134752,  0.93085106,  0.93617021,  0.92553191,
                 0.95035461,  0.93439716,  0.95921986,  0.93439716,  0.93085106,
                 0.93794326,  0.93617021,  0.83333333,  0.88475177,  0.91312057,
                 0.89361702,  0.93971631,  0.91489362,  0.92198582,  0.87943262,
                 0.87411348,  0.92907801,  0.89893617,  0.91666667,  0.95035461,
                 0.91489362,  0.94148936,  0.92730496,  0.95567376,  0.91666667,
                 0.94326241,  0.95567376,  0.94326241,  0.93971631,  0.94326241,
                 0.93794326,  0.92553191,  0.95921986,  0.96276596,  0.93794326])
    >>> tau.zTau
    array([ 9.43909886,  9.10135333,  9.33244238,  9.17245765,  9.13690549,  8.3903101 ,
                 8.8524882 ,  8.90581644,  9.19023373,  9.42132278,  9.72351615,
                 9.35021846,  8.56807091,  8.8524882 ,  9.01247292,  9.04802509,
                 8.88804036,  8.60362307,  8.37253402,  8.19477321,  9.15468157,
                 9.29689022,  9.22578589,  9.20800981,  9.43909886,  9.19023373,
                 9.47465102,  9.19023373,  9.17245765,  9.20800981,  9.4035467 ,
                 9.51020318,  9.13690549,  9.33244238,  9.38577062,  9.27911414,
                 9.52797927,  9.36799454,  9.61685967,  9.36799454,  9.33244238,
                 9.4035467 ,  9.38577062,  8.35475794,  8.87026428,  9.15468157,
                 8.95914468,  9.42132278,  9.17245765,  9.24356197,  8.81693604,
                 8.76360779,  9.3146663 ,  9.01247292,  9.19023373,  9.52797927,
                 9.17245765,  9.43909886,  9.29689022,  9.58130751,  9.19023373,
                 9.45687494,  9.58130751,  9.45687494,  9.42132278,  9.45687494,
                 9.4035467 ,  9.27911414,  9.61685967,  9.65241183,  9.4035467 ])
    >>> 

    """

    def __init__(self,variable,interval=1,w=None,permutations=0):
        self.variable = variable
        self.interval = interval
        self.w = w
        ranks=rankValues(variable,0)
        self.ranks = ranks
        r1=ranks[:,interval:]
        r2=ranks[:,0:-interval]
        self.r1=r1
        self.r2=r2
        t=variable.t-interval
        n=variable.n
        n2=n*n
        T = (n2 - n) / 2
        results=zeros([t,n,n])
        rn = range(n)
        dom2s = []
        for period in range(t):
            r11=r1[:,period]
            r22=r2[:,period]
            dom1=array([r < r11 for r in r11])
            dom2=array([r < r22 for r in r22])
            dom2s.append(dom2) # keep for permutation tests
            results[period]=(dom1==dom2)
        self.results =results
        concord = array([sum(sum(x)) for x in results])
        self.concord = (concord - n) / 2
        self.discord = T - self.concord
        self.tau = (self.concord-self.discord)/(T*1.)
        self.T = T
        # asymptotic variance of tau
        vTau = ( 4. * n + 10) / ( 9. * n * (n-1))
        sTau = sqrt(vTau)
        zTau = self.tau/sTau
        self.zTau = zTau
        self.pzTau = array([ (1. - zprob(abs(zi))) for zi in zTau ]) 

        T1 = T * 1.
        self.permutations = permutations
        if permutations:
            ids = range(n)
            sim = []
            for perm in range(permutations):
                ids = permutate(ids)
                r1p = take(r1,ids)
                tres = []
                for period in range(t):
                    r11 = r1p[:,period]
                    dom1 = array([ r < r11 for r in r11])
                    dom2 = dom2s[period]
                    nc = sum(sum(dom1==dom2) - n ) / 2 
                    dc = T - nc
                    tau = (nc-dc) / T1
                    tres.append(tau)
                sim.append(tres)
            self.sim = sim
            evtau = mean(sim)
            stau =  std(sim)
            z = (self.tau - evtau) / stau
            self.perm_zTau = z
            self.perm_pzTau = array([ (1. - zprob(abs(zi))) for zi in z ]) 



        if w and self.permutations:
            self.regime = w.name
            w=w.full() > 0
            self.nContiguities = sum(sum(w))/2.
            contConcord = array([ w * r for r in results])
            contConcordCount = array([sum(sum(x))/2. for x in contConcord])
            self.contConcordCount = contConcordCount
            self.contTau= contConcordCount / self.nContiguities *1.
            self.nonContConcordCount = self.concord - self.contConcordCount
            self.nonContTau = self.nonContConcordCount / (self.T - self.nContiguities)
            presults = []
            n =len(w)
            ids = range(n)
            for perm in range(permutations):
                id = permutate(ids)
                wr = take(take(w,id),id,1)
                contC = array([ wr * r for r in results])
                cCount = array([sum(sum(x))/2. for x in contC])
                presults.append(cCount)
            self.presults = presults

            pvalues = presults < self.contConcordCount

            pvalues = sum(pvalues)/ (permutations * 1.)
            self.pvalues = pvalues
            mcount = mean(presults)
            scount = std(presults)
            d = self.contConcordCount - mcount
            z= d/scount
            zpvalues = array([ (1. - zprob(abs(zi))) for zi in z ])
            self.z = z
            self.zpvalues = zpvalues
            self.evalue = mcount

    def report(self):
        head = "Tau Rank Correlation\n"
        if self.permutations:
            tp = head,self.variable.name,self.interval,self.permutations
            mat = [self.tau,self.zTau,self.pzTau,self.perm_pzTau]
            head = "%s\nVariable: %s, Interval: %d, Permutations: %d"%tp

            colHead = ["Tau","z","p(n)","p(p)"]
        else:
            tp = head,self.variable.name,self.interval
            head = "%s\nVariable: %s, Interval: %d"%tp
            mat = [self.tau,self.zTau,self.pzTau]
            colHead = ["Tau","z","p(n)"]
        mat = transpose(array(mat))
        rowLabels = self.variable.timeString
        tab = Table(mat,head=head,colNames=colHead,
                rowNames=rowLabels,fmt=[[8,3]]).table


        if self.permutations and self.w:
            actual = self.contConcordCount
            evalue = self.evalue
            z = self.z
            pvalue = self.zpvalues
            mat = array([actual,evalue,z,pvalue])
            mat = transpose(mat)

            head="Tau and Spatial Tau Rank Concordance\n"
            tp=head,self.variable.name,self.interval,self.permutations
            head="%s\nVariable %s, Interval: %d, Permutations: %d"%tp
            head="%s\nRegime: %s"%(head,self.regime)
            head="%s\nStatistics for contiguous pairs"%head
            rowLabels = self.variable.timeString
            colLabels = ["# Concordant","Expected Value","z", "p-value"]
            body = mat
            self.body  = body
            taba = Table(body,head=head,
                rowNames=rowLabels,colNames=colLabels,
                fmt=[[8,0],[8,3],[8,3],[8,3]]).table
            tab = tab+"\n"+taba
        return tab

class Theta:
    """Spatial rank mobility decomposition

    Arguments:
        variable: STARS variable
        partition: STARS cs variable with regime membership ids
        interval: length of time interval (default = 1)  
    
    Attributes:
        variable: variable (csts/tscs)
        parition: variable defining the partitions (cs)
        ranks: ranks of variable within each time period
        rdp: rank changes within each regime
        tpd: total rank changes within each regime
        rd:  rank changes
        td: total rank changes
        theta: spatial rank mobility cohesion measure


    Example Useage:
    >>> from stars import Project
    >>> s=Project('s')
    >>> s.ReadData('data/csiss')
    >>> y=s.getVariable('pcincome')
    >>> r=s.getVariable('bea')
    >>> t = Theta(y,r)
    >>> t.theta
    array([ 0.47368421,  0.67088608,  0.49206349,  0.61038961,  0.45205479,  0.74647887,
                 0.69724771,  0.62745098,  0.51388889,  0.38888889,  0.41935484,
                 0.39393939,  0.67692308,  0.38317757,  0.55813953,  0.37209302,
                 0.47572816,  0.53097345,  0.53731343,  0.67741935,  0.6       ,
                 0.55714286,  0.35064935,  0.54545455,  0.57142857,  0.625     ,
                 0.39622642,  0.57333333,  0.60526316,  0.79487179,  0.57692308,
                 0.42307692,  0.61445783,  0.328125  ,  0.80327869,  0.62857143,
                 0.48      ,  0.50819672,  0.51162791,  0.2       ,  0.53030303,
                 0.47272727,  0.76666667,  0.81081081,  0.74509804,  0.54545455,
                 0.69387755,  0.44444444,  0.58536585,  0.62857143,  0.91071429,
                 0.7962963 ,  0.66666667,  0.65957447,  0.76923077,  0.65306122,
                 0.57142857,  0.77777778,  0.78787879,  0.40909091,  0.66666667,
                 0.57142857,  0.72093023,  0.58490566,  0.67857143,  0.48148148,
                 0.81481481,  0.5625    ,  0.28571429,  0.42857143,  0.3559322 ])
        """
 
    def __init__(self,variable,partition,interval=1):
        ranks=rankValues(variable,0)
        self.ranks = ranks
        self.variable = variable
        self.partition = partition
        self.interval = interval
        r1=ranks[:,interval:]
        r2=ranks[:,0:-interval]
        self.r1=r1
        self.r2=r2
        rd=r1-r2
        self.rankDiff=rd
        #partition ids as ints
        pid = array([int(x) for x in partition[:,0]])
        p=sort(unique(pid))
        np = [sum(pid==x) for x in p]
        self.np = np
        # sum of signed rank changes within each partition
        rdp = array([sum(take(rd,nonzero(pid==r))) for r in p])
        self.rdp = rdp
        self.pid = pid
        # sum of unsigned rank changes within each partition
        ardp = array([sum(abs(take(rd,nonzero(pid==r)))) for r in p])
        self.ardp = ardp
        # total of partition rank changes
        tpd = sum(abs(rdp),0)
        self.tpd = tpd
        # total rank changes
        self.rd = rd
        td = sum(abs(rd),0)
        self.td=td
        # put in check for 0 rank changes in denominator
        td1=td + (td == 0)
        theta = tpd / (td1*1.)
        self.theta=theta

        # average rank change
        n = variable.n
        avgChange = td*1./n
        self.avgChange = avgChange
        self.nPartition = np
        expChange = array([avgChange * npp for npp in np])
        self.expChange = expChange

        # relative rank change
        relChange = ardp*1./(expChange + (expChange == 0))
        self.relChange = relChange

        # partition cohesion
        pCohesion = abs(rdp)*1./(ardp + (ardp==0))
        self.pCohesion = pCohesion

    def report(self):
        tabs=[]
        head="Spatial Rank Mobility Decomposition\nVariable: %s"%self.variable.name
        head="%s\nPartition: %s\nInterval %d"%(head,self.partition.name,self.interval)
        rowLabels = self.variable.timeString
        colLabels = ["Rank Changes","Partition Cohesive","Theta"]
        body = transpose(array([self.td/2,self.tpd/2,self.theta]))
        self.body  = body
        tab = Table(body,head=head,
            rowNames=rowLabels,colNames=colLabels,
            fmt=[[8,0],[8,0],[8,3]],
            origin="t0").table
        #tab = ""
        tabs.append(tab)
        head="Parition Mobility Summary"
        rowLabels = [str(x) for x in sort(unique(self.pid))]
        colLabels = [ "n","Relative Change","Cohesion"]
        mrel = mean(self.relChange,1)
        mcoh = mean(self.pCohesion,1)
        body = transpose(array([self.np,mrel,mcoh]))
        tab1 = Table(body,head=head,
            rowNames=rowLabels,colNames=colLabels,
            fmt=[[8,0],[8,3],[8,3]],origin="Partition").table
        tabs.append(tab1)
        tab="\n".join(tabs)
        return tab
        

def _test():
    import doctest, Mobility
    return doctest.testmod(Mobility)

if __name__ == "__main__":
    _test()
