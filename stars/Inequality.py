"""
Inequality metrics for STARS
----------------------------------------------------------------------
Distributional inequalities  module for Space-Time Analysis of
Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Jared Aldstad aldstad@rohan.sdsu.edu
----------------------------------------------------------------------


OVERVIEW

Classes:
    Theil            Theils T Inequality Measure
    TheilD           Spatial (or other) Decomposition of T
    TheilDSim        Inference on TheilD based on permutations
    Gini             Gini Coefficient
    GiniD            Decomposition of Gini
    GiniS            Spatial Decomposition of Gini (Contiguity)

"""
from stars import *
import numpy as np
from Utility import *
from inequality.theil import Theil as _PyTheil, TheilD as _PyTheilD
SMALL = 0.0000001

class Theil:
    """Computes aggregate Theil measure when passed STARS Variable.

    Delegates to inequality.theil.Theil for computation.

    Example Usage:
    >>> from stars import Project
    >>> s=Project("s")
    >>> s.ReadData("csiss")
    >>> y=s.getVariable("pcincome")
    >>> yTheil = Theil(y)
    >>> len(yTheil.T)
    72
    >>> yTheil.T[0]
    0.062513504720263305
    >>> y0_3Theil = Theil(y[:,0:4])
    >>> y0_3Theil.T.shape
    (4,)
    >>> y0_3Theil.T
    array([ 0.0625135 ,  0.07029599,  0.07698629,  0.08187351])
    >>>

    """

    def __init__(self,y):
        self.T = _PyTheil(np.asarray(y)).T

class TheilD:
    """computes a decomposition of theil based on partionings into
    exhaustive and mutually exclusive groups. Partion id's have to be
    zero offset and increment from there (i.e., first id is 0, second is
    1....
    EXAMPLE USEAGE:
    >>> from stars import Project
    >>> s=Project("s")
    >>> s.ReadData("csiss")
    >>> y=s.getVariable("pcincome")
    >>> r=s.getVariable("bea")
    >>> td=TheilD(y,r)
    >>> dir(td)
    ['BG', 'T', 'WG', '__doc__', '__init__', '__module__', 'p', 'pid', 'sig', 'wgg', 'wgps', 'wgs']
    >>> td.T[0]
    0.062513504720263305
    >>> td.BG[0]
    0.04896375187589095
    >>> td.WG[0]
    0.013549752844372355
    """

    def __init__(self,y,partition, partitionName=None):
        self.variable = y
        if partitionName:
            self.partitionName=partitionName
        else:
            self.partitionName = partition.name
        regime = Regime(partition, self.partitionName)
        self.partition = regime.partition
        pid = np.array(self.partition)
        p = np.sort(unique(pid))

        _td = _PyTheilD(np.asarray(y), pid)
        self.T = _td.T
        self.BG = _td.bg
        self.WG = _td.wg
        self.ng = np.array([np.sum(pid==r) for r in p]) * 1.0
        self.maxT = np.log(y.n * 1.)
        self.p = p
        self.pid = pid
        self.sig = None
        self.wgg = None
        self.wgps = None
        self.wgs = None

    def report(self):
        head = "Theil Spatial Inequality Decomposition"
        head = "%s\nVariable: %s\nPartition: %s"%(head,self.variable.name,self.partitionName)
        body = np.transpose(np.array([self.T,self.WG,self.BG]))
        colLabels=["Global Inequality","Intraregional","Interregional"]
        rowLabels=self.variable.timeString
        origin="Period"
        tab = Table(body,head=head,colNames=colLabels,
            rowNames=rowLabels,
            origin=origin).table
        return tab



class TheilDSim:
    """Randomization testing of Theil's T decomposition.

    Tests whether the difference between the within and between groups
    components is significant.

    ARGUMENTS:
        y: observations (array)
        partition: regime assignment for each obs. (array or cs instance)
        realization: number of permutations (int, optional)

    ATTRIBUTES:
        Ts: random Theil's T values (array)
        BGs: random Theil's between group values (array)
        WGs: random Theil's w/i group values (array)
        realization: number of permutations used (int)

    EXAMPLE USEAGE:
        >>> from stars import Project
        >>> s=Project("s")
        >>> s.ReadData("csiss")
        >>> y=s.getVariable("pcincome")
        >>> r=s.getVariable("bea")
        >>> np.random.seed(10)
        >>> tds=TheilDSim(y,r,100)
        >>> dir(tds)
        ['BGP', 'BGPs', 'BGoriginal', 'BGs', 'Doriginal', 'Ds', 'Toriginal', 'Ts', 'WGP', 'WGPs', 'WGoriginal', 'WGs', '__doc__', '__init__', '__module__', 'meanBG', 'meanBGP', 'meanD', 'meanWG', 'meanWGP', 'realizations', 'stdBG', 'stdBGP', 'stdD', 'stdWG', 'stdWGP', 'z', 'zBGP', 'zWGP']
        >>> tds.zBGP[0]
        8.2763593048651387
        >>>

    """
    def __init__(self,y,partition,realizations=100):
        if type(partition)=='instance':
            n=partition.n
        else:
            n=len(partition)

        original = TheilD(y,partition)
        self.Ts = []
        self.BGs = []
        self.WGs = []
        self.Ds = []
        self.BGPs = []
        self.WGPs = []
        for i in range(realizations):
            randomp=permutate(partition)
            res=TheilD(y,randomp,partition.name)
            self.Ts.append(res.T)
            self.BGs.append(res.BG)
            self.WGs.append(res.WG)
            self.Ds.append(res.WG - res.BG)
            self.BGPs.append(res.BG/res.T)
            self.WGPs.append(res.WG/res.T)

        self.Toriginal = original.T
        self.WGoriginal = original.WG
        self.BGoriginal = original.BG
        self.Doriginal = original.WG - original.BG
        self.BGP = original.BG/original.T
        self.WGP = original.WG/original.T
        self.BGs = np.array(self.BGs)
        self.WGs = np.array(self.WGs)
        self.Ts = np.array(self.Ts)
        self.Ds = np.array(self.Ds)
        self.meanBG = np.mean(self.BGs)
        self.stdBG = np.std(self.BGs)
        self.meanWG = np.mean(self.WGs)
        self.stdWG = np.std(self.WGs)
        self.meanD = np.mean(self.Ds)
        self.stdD = np.std(self.Ds)
        z = (self.Doriginal - self.meanD)/self.stdD
        self.z = z
        self.BGPs = np.array(self.BGPs)
        self.meanBGP = np.mean(self.BGPs)
        self.stdBGP = np.std(self.BGPs)
        zBGP = (self.BGP - self.meanBGP)/self.stdBGP
        self.zBGP = zBGP
        self.WGPs = np.array(self.WGPs)
        self.meanWGP = np.mean(self.WGPs)
        self.stdWGP = np.std(self.WGPs)
        zWGP = (self.WGP - self.meanWGP)/self.stdWGP
        self.zWGP = zWGP

        self.realizations = realizations
        self.variable = y
        self.partitionName = partition.name
        self.T = original.T
        self.WG = original.WG
        self.BG = original.BG

    def report(self):
        head = "Theil Spatial Inequality Decomposition (Permutation based inference)"
        head = "%s\nVariable: %s\nPartition: %s"%(head,self.variable.name,self.partitionName)
        head = "%s\nPermutations: %d"%(head,self.realizations)
        body = np.transpose(np.array([self.T,self.WG,self.BG, self.meanBG, self.zBGP]))
        colLabels=["Global Inequality","Intraregional","Interregional"]
        colLabels += [ "E[Interregional]", "z" ]
        rowLabels=self.variable.timeString
        origin="Period"
        tab = Table(body,head=head,colNames=colLabels,
            rowNames=rowLabels,
            origin=origin).table
        return tab



class Gini:
    """Computes Gini coefficient(s) for each t when passed STARS Variable.

    Arguments (1):
    y: observations (STARS variable)

    Atributes:
    gini: gini coefficient for each time period (array)

    Example Usage:
    >>> from stars import Project
    >>> from Inequality import *
    >>> s=Project("s")
    >>> s.ReadData("csiss")
    >>> y=s.getVariable("pcincome")
    >>> yGini = Gini(y)
    >>> len(yGini.gini)
    72
    >>> "%5.3f"%yGini.gini[0]
    '0.201'
    """

    def __init__(self,y):
        n = y.n
        self.variable=y
        ybar = np.mean(y, axis=0)
        yd = np.sort(y - ybar, axis=0)
        fy = np.arange(1.0,(n+1)) / n - (1/2.0)
        self.gini = 2.0 * (fy @ yd) / n / ybar

    def report(self):
        head = "Gini Coefficient of Inequality"
        head = "%s\nVariable: %s"%(head,self.variable.name)
        rowLabels=self.variable.timeString
        origin="Period"
        colLabels=["Gini"]
        body = np.transpose(np.array([self.gini]))
        tab = Table(body,head=head,colNames=colLabels,
            rowNames=rowLabels,
            origin=origin).table
        return tab

class GiniD:
    """computes a decomposition of Gini based on partionings into
    exhaustive and mutually exclusive groups. Partion id's have to be
    zero offset and increment from there (i.e., first id is 0, second is
    1....

    ARGUMENTS:
        y: observations (array)
        partition: regime assignment for each obs. (array or cs instance)

    ATTRIBUTES:
        qi: stratification index for each region for each time (array)
        globalGini: global Gini coefficient for each time period (array)
        partitionGini: Gini coefficient for each region by time period (array)
        wgc: The within group component of Gini for each time period (array)
        strat: The stratification component of Gini for each time period (array)
        bgc: The between group component of Gini for each time period (array)

    Example Usage:
        >>> from stars import Project
        >>> from Inequality import *
        >>> s=Project("s")
        >>> s.ReadData("csiss")
        >>> y=s.getVariable("pcincome")
        >>> r =s.getVariable("bea")
        >>> yg = GiniD(y,r)
        >>> print ((yg.wgc[4]+yg.bgc[4]+yg.strat[4])-yg.globalGini[4])
        0.0
    """

    def __init__(self,y,partition):
        # total numer of observations
        n=y.n *1.0

        # partition ids as ints
        pid = np.array([int(x) for x in partition[:,0]])

        # unique partition ids
        p = np.sort(unique(pid))
        regions = len(p)

        # total income in partitions
        yg = np.array([np.sum(np.take(y, np.nonzero(pid==r)[0], axis=0), axis=0) for r in p])

        # number of obs in each partition
        ng = np.array([np.sum(pid==r) for r in p])*1.0

        # population share
        pg = ng/n

        # total income in system
        yt = np.sum(y, axis=0)

        # partition share's of income
        if len(yt.shape) > 1:
            sg = yg @ np.diag(1/yt)
        else:
            sg = yg/yt

        # global Gini
        globalGini = Gini(y).gini

        #calculate Qi and partition Ginis
        qi = np.zeros((regions,y.t))
        partitionGini = np.zeros((regions,y.t))
        regionCount = 0
        for r in p:
            fi = np.arange(1.0,(ng[regionCount]+1)) / ng[regionCount]
            regiony = np.sort(np.take(y, np.nonzero(pid==r)[0], axis=0), axis=0)
            partitionGini[regionCount,:] = Gini(Variable(regiony)).gini
            ny = np.sort(np.take(y, np.nonzero(pid!=r)[0], axis=0), axis=0)
            for t in range(y.t):
                fni = np.searchsorted(ny[:,t],regiony[:,t]) / (y.n - ng[regionCount])
                diff = fi - fni
                qi[regionCount,t] = self.covariance(diff,regiony[:,t])/self.covariance(fi,regiony[:,t])
            regionCount = regionCount + 1

        #calculate within group component
        wgc = np.sum(sg*partitionGini, axis=0)

        #calculate stratification component
        pgv = np.reshape(pg, (pg.shape[0],1))
        strat = np.sum(sg * partitionGini * qi * (pgv - 1), axis=0)

        #calculate between group component
        self.bgc = globalGini - wgc - strat

        self.qi = qi
        self.globalGini = globalGini
        self.partitionGini = partitionGini
        self.wgc = wgc
        self.strat = strat

    def covariance(self,a1,a2):
        a1 = a1 - np.mean(a1)
        a2 = a2 - np.mean(a2)
        cv = np.sum(a1*a2)
        return cv/a1.shape[0]

class GiniDSim:
    """Randomization testing of the Gini decomposition.

    Tests whether the values for inequality within, inequality between, and
    stratification for each time period are significant.

    ARGUMENTS:
        y: observations (array)
        partition: regime assignment for each obs. (array or cs instance)
        realizations: number of permutations (int, optional)

    ATTRIBUTES:
        original: GiniD object created with original dataset (GiniD)
        realizations: number of permutations performed (int)
        pqi: montecarlo p-values for qi values (array)
        ppg: montecarlo p-values for partition Gini values (array)
        zST: z values for stratification components based on simulations (array)
        zBG: z values for between group components based on simulations (array)
        zWG: z values for within group components based on simulations (array)

    Example Usage:
    >>> from stars import Project
    >>> from Inequality import *
    >>> s=Project("s")
    >>> s.ReadData("csiss")
    >>> y=s.getVariable("pcincome")
    >>> r =s.getVariable("bea")
    >>> np.random.seed(10)
    >>> yg = GiniDSim(y,r,realizations = 9)
    >>> print(yg.original.wgc[8])
    0.0930408458964
    >>> print(yg.original.strat[48])
    -0.0130304985249
    >>> print(yg.original.bgc[71])
    0.0435345431775
    >>> print(yg.zST[0])
    -11.0749820671
    """
    def __init__(self,y,partition,realizations=100):
        if type(partition)=='instance':
            n=partition.n
        else:
            n=len(partition)

        original = GiniD(y,partition)
        STs = []
        BGs = []
        WGs = []
        pqi = np.ones(original.qi.shape)
        ppg = np.ones(original.partitionGini.shape)

        for i in range(realizations):
            randomp=permutate(partition)
            randomp=np.array(randomp)
            res=GiniD(y,randomp)
            STs.append(res.strat)
            BGs.append(res.bgc)
            WGs.append(res.wgc)
            pqi += (original.qi < res.qi)
            ppg += (original.partitionGini > res.partitionGini)

        pqi /= (realizations+1.)
        ppg /= (realizations+1.)
        self.realizations = realizations

        self.STs = np.array(STs)
        self.meanST = np.mean(self.STs)
        self.stdST = np.std(self.STs)
        self.zST = (original.strat - self.meanST)/self.stdST

        self.BGs = np.array(BGs)
        self.meanBG = np.mean(self.BGs)
        self.stdBG = np.std(self.BGs)
        self.zBG = (original.bgc - self.meanBG)/self.stdBG

        self.WGs = np.array(WGs)
        self.meanWG = np.mean(self.WGs)
        self.stdWG = np.std(self.WGs)
        self.zWG = (original.wgc - self.meanWG)/self.stdWG

        self.pqi = pqi
        self.ppg = ppg
        self.original = original

class GiniS:
    """Spatial Gini """
    def __init__(self,y,w,permutations=0):
        W=w.full()!=0
        tw=np.transpose(y)
        self.variable=y
        self.w=w
        self.permutations=permutations
        self.res = [self.calc(y1,W)  for y1 in tw]
        self.G = np.array([x[0] for x in self.res])
        self.WG = np.array([x[1] for x in self.res])
        self.NG = np.array([x[2] for x in self.res])
        self.den = np.array([x[3] for x in self.res])
        self.gini = self.G/self.den
        self.n=self.variable.n
        self.nc = np.sum(W)
        self.n2 = self.n*self.n
        self.nn = self.n2 - self.nc
        if permutations:
            self.WGcount = np.zeros(y.t)
            print("perms")
            for perm in range(permutations):
                py=permutate(y)
                permRes = [self.calc(y1,W) for y1 in np.transpose(py)]
                WG = np.array([x[1] for x in permRes])
                comp = WG < self.WG
                self.WGcount += comp
            self.pvalue = self.WGcount*1./self.permutations

    def calc(self,y1,w):
        n=len(y1)
        n2=n*n
        nc=np.sum(w)
        nn=n2-nc
        g=np.array([abs(y1-ya) for ya in y1])
        wg=w*g
        ng=g-wg
        G=np.sum(g)
        WG=np.sum(wg)
        NG=G-WG
        den=2*n2*np.mean(y1)
        avgD=G*1./(n2)
        EWG= avgD * nc
        ENG= avgD * nn
        rWG = WG/EWG
        rNG = NG/ENG
        return(np.array((G,WG,NG,den)))

    def report(self):
        head = "Spatial Gini"
        head = "%s\nVariable: %s\nWeight Matrix: %s"%(head,self.variable.name,self.w.name)
        rowLabels=self.variable.timeString
        origin="Period"
        if self.permutations==0:
            colLabels=["Gini","Non-Contiguous Pairs Share"]
            body = np.transpose(np.array([self.gini,self.NG/self.G]))
        else:
            colLabels=["Gini","Non-Contiguious Pairs Share","pvalue"]
            body = np.transpose(np.array([self.gini,self.NG/self.G,self.pvalue]))
        tab = Table(body,head=head,colNames=colLabels,
            rowNames=rowLabels,
            origin=origin).table
        return tab

if __name__ == '__main__':
    from stars import *
    from time import *
    s=Project("s")
    s.ReadData("data/geoda/nat")
    y=s.getVariable("blk")
    r =s.getVariable("STATE_FIPS")

    td = TheilD(y,r)
    tds= TheilDSim(y,r)
