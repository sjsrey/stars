"""
Exploratory spatial data analysis module for STARS
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Jared Aldstad aldstad@rohan.sdsu.edu
----------------------------------------------------------------------

OVERVIEW

Exploratory Spatial Data Analysis Module for STARS.

Classes:
    Moran         Moran's I statistic for spatial autocorrelation.
    LocalMoran    Location Specific Moran's I measures
    Geary         Geary's C statistic for spatial autocorrelation.
    LocalGeary    Location Specific Geary's c Measures
    GlobalG       Getis-Ord statistic for spatial association
    LocalG        Local versions of Getis-Ord statistics.
"""
import numpy as np
import esda as _esda
import libpysal.weights as _lpsw

# stars imports
from stars import *
from Data import *
from Messages import *
from Utility import *
from pysal_weights import spmatrix_to_w
import pdf
import Markov


class Moran:
    """Moran's I measure of global spatial autocorrelation.

    Arguments (3):
        y: STARS variable
        w: STARS weight matrix
        permutations: Number of random spatial permutations (optional)
        varAssumption: "normalization"(default) or "randomization" (optional)

    Attributes
        mi: Global Moran's I
        zi: z-value for mi
        ei: expected value
        vi: variance of I
        si: standard deviation of I
        npvalue: probability value based on normality assumption
        varAssumption: assumption used to calculate vi
        ppvalue: psuedo significance levels (if permutations != 0)

    Example Useage:
    """
    def __init__(self, y, w, permutations=0, varAssumption="normalization"):
        self.variable = y
        self.varAssumption = varAssumption
        self.permutations = permutations
        self.w = w

        pw = spmatrix_to_w(w)
        two_tailed = False
        transformation = 'r'

        mi_vals, zi_vals, npvalue_vals, ppvalue_vals = [], [], [], []
        for t_idx in range(y.t):
            yt = np.asarray(y[:, t_idx]).flatten()
            m_t = _esda.Moran(yt, pw, permutations=permutations,
                              transformation=transformation,
                              two_tailed=two_tailed)
            mi_vals.append(m_t.I)
            zi_vals.append(m_t.z_norm if varAssumption == "normalization"
                           else m_t.z_rand)
            npvalue_vals.append(m_t.p_norm if varAssumption == "normalization"
                                else m_t.p_rand)
            if permutations:
                ppvalue_vals.append(m_t.p_sim)

        self.mi = np.array(mi_vals)
        self.zi = np.array(zi_vals)
        self.ei = m_t.EI
        self.vi = m_t.VI_norm if varAssumption == "normalization" else m_t.VI_rand
        self.si = np.sqrt(self.vi)
        self.npvalue = npvalue_vals
        if permutations:
            self.ppvalue = np.reshape(ppvalue_vals, [1, y.t])

        # spatial lag for Moran scatter plots (row-standardized)
        wfull = w.full()
        self.ylag = Variable(wfull @ np.asarray(y))

    def report(self):
        """Pretty formatting of summary results"""
        head = "Moran's I"
        head = "%s\nVariable: %s\nWeight Matrix: %s" % (head, self.variable.name, self.w.name)
        rowLabels = self.variable.timeString
        colLabels = ["MI", "z", "p-(N)"]

        t = self.variable.t
        m = np.reshape(self.mi, [t, 1])
        p = np.reshape(self.npvalue, [t, 1])
        z = np.reshape(self.zi, [t, 1])
        res = np.concatenate((m, z, p), 1)
        self.junk = res
        if self.permutations:
            colLabels.append("p-(P)")
            pp = np.reshape(self.ppvalue, [t, 1])
            res = np.concatenate((m, z, p, pp), 1)
            head = "%s\nPermutations: %d" % (head, self.permutations)
        else:
            res = np.concatenate((m, z, p), 1)

        head = "%s\nExpected Value: %8.3f" % (head, self.ei)
        tab = Table(res, head=head,
                    rowNames=rowLabels,
                    colNames=colLabels).table
        return (tab)

    def extreme(self, mi):
        """Determines number of permutated mi values that are more
        extreme than original mi. To be used internally, not public.

        Arguments (1)
            mi: original mi value
        """
        # if zi - then inc if mi < self.mi
        # if zi + then inc if mi > self.mi
        zn = self.zi < 0
        mlt = mi < self.mi
        zp = self.zi > 0
        mgt = mi > self.mi
        return (zn * mlt) + (zp * mgt)

    def iMoments(self, w):
        "Moments for Moran's I under normality assumption."
        w = w.full()
        rs = np.sum(w, axis=1)
        cs = np.sum(w, axis=0)
        n, dum = w.shape
        s0 = np.sum(rs)
        t = rs + cs
        s2 = np.sum(t * t)

        wt = w.T
        wtw = wt + w
        wtw2 = wtw * wtw
        s1 = np.sum(wtw2) / 2.0
        ei = -1.0 / (n - 1)

        s02 = s0 * s0

        if self.varAssumption == "randomization":
            yd = self.variable - np.mean(self.variable, axis=0)
            k = (1 / np.sum(yd ** 4) * (np.sum(yd ** 2)) ** 2)
            vi = (1 / (((n - 1) ** 3) * s02)) * ((n * ((n * n - 3 * n + 3) * s1 - n * s2 + 3 * s02))
                                                   - (k * ((n * n - n) * s1 - 2 * n * s2 + 6 * s02)))
        else:
            vi = ((1 / (s02 * (n * n - 1)) * (n * n * s1 - n * s2 + 3 * s02)))

        vi = vi - ei * ei
        self.ei = ei
        self.vi = vi
        self.si = np.sqrt(vi)


class LocalMoran:
    """Moran's I measure of local spatial autocorrelation.

    Arguments (3):
        y: STARS variable
        w: STARS weight matrix
        permutations: Number of random spatial permutations (optional)

    Attributes
        mi: Local Moran's I (n by t array)
        expMi: expected mi value (n by 1 array)
        ppvalue: psuedo significance levels(if permutations != 0)(n by t array)

    Example Useage:
        >>> from stars import Project
        >>> s=Project("s")
        >>> s.ReadData("csiss")
        >>> income=s.getVariable("pcincome")
        >>> galstates = open("states48.gal",'r')
        >>> ws = galstates.readlines()
        >>> galstates.close()
        >>> galinfo = list(map(int,"".join(ws).split()))
        >>> wsp = spGalMatrix("wsp",galinfo)
        >>> np.random.seed(10)
        >>> ii = LocalMoran(income,wsp,permutations = 3)
        >>> print(ii.expMi[4])
        [-0.0212766]
        >>> print(ii.mi[4,3])
        -0.0142149120418
        >>> print(ii.ppvalue[4,3])
        0.75
    """

    def __init__(self, y, w, permutations=0):
        self.variable = y
        self.w = w
        self.permutations = permutations
        pw = spmatrix_to_w(w)
        mi_vals = np.zeros((y.n, y.t))
        q_vals = np.zeros((y.n, y.t), dtype=int)
        ppvalue_vals = np.zeros((y.n, y.t))
        for t_idx in range(y.t):
            yt = np.asarray(y[:, t_idx]).flatten()
            ml_t = _esda.Moran_Local(yt, pw, permutations=permutations)
            mi_vals[:, t_idx] = ml_t.Is
            q_vals[:, t_idx] = ml_t.q
            if permutations:
                ppvalue_vals[:, t_idx] = ml_t.p_sim
        self.mi = mi_vals
        self.expMi = np.full((y.n, 1), -1.0 / (y.n - 1))
        # qvalue: 1=HH, 2=LH, 3=LL, 4=HL (matches esda.q convention)
        self.qvalue = q_vals
        # dvalue: HH->4, LH->2, LL->1, HL->3 (diverging color scheme)
        dmap = np.array([4, 2, 1, 3])
        self.dvalue = dmap[q_vals - 1]
        if permutations:
            self.ppvalue = ppvalue_vals
        # Demeaned spatial lag
        wfull = w.full()
        yl = wfull @ np.asarray(y)
        self.ylag = Variable(yl - np.mean(np.asarray(y), axis=0))

    def getNum(self, yd):
        if yd.ndim == 1:
            ydprime = np.reshape(yd, (yd.n, yd.t)).T
        else:
            ydprime = yd.T

        # box is an array of shape (t,n,n) where y values are repeated
        # along the rows n times for each time period
        box = np.reshape(ydprime, (yd.t, yd.n, 1))
        box = np.repeat(box, yd.n, axis=2)

        # boxprime is an array of shape(t,n,n) where y values are
        # repeated along the columns n times for each time period
        boxprime = np.repeat(ydprime, yd.n, axis=0)
        boxprime = np.reshape(boxprime, (yd.t, yd.n, yd.n))

        # The last line of this method converts the results
        # back into a (n,t) array.
        return np.transpose(np.sum((box * boxprime * self.w), axis=2))

    def getDen(self, yd):
        if yd.ndim == 1:
            ydtemp = np.reshape(yd, (yd.n, yd.t))
        else:
            ydtemp = yd
        yd2 = ydtemp ** 2
        return (yd.n ** 2) / np.sum(yd2) / self.sumw

    def report(self):
        """Formatting of summary results."""

        q = self.qvalue
        q1 = q == 1
        q2 = q == 2
        q3 = q == 3
        q4 = q == 4

        n1 = np.sum(q1, axis=1)
        n2 = np.sum(q2, axis=1)
        n3 = np.sum(q3, axis=1)
        n4 = np.sum(q4, axis=1)
        n = np.zeros((len(n1), 4))
        n[:, 0] = n1
        n[:, 1] = n2
        n[:, 2] = n3
        n[:, 3] = n4
        rowNames = self.variable.regionNames
        colLabels = ["Q1", "Q2", "Q3", "Q4"]
        head = "Local Moran's I"
        head = "%s\nVariable: %s\nWeight Matrix: %s" % (head, self.variable.name, self.w.name)
        head = "%s\nCount of I's by Quadrant." % (head)
        tab = Table(n, colNames=colLabels,
                    rowNames=rowNames,
                    head=head, fmt=[[8, 0]]).table

        if self.permutations:
            p5 = self.ppvalue <= 0.05

            q1 = np.sum(p5 * q1, axis=1)
            q2 = np.sum(p5 * q2, axis=1)
            q3 = np.sum(p5 * q3, axis=1)
            q4 = np.sum(p5 * q4, axis=1)

            q = np.zeros((len(q1), 4))
            q[:, 0] = q1
            q[:, 1] = q2
            q[:, 2] = q3
            q[:, 3] = q4
            rowNames = self.variable.regionNames
            colLabels = ["Q1", "Q2", "Q3", "Q4"]
            head = "Local Moran's I"
            head = "%s\nVariable: %s\nWeight Matrix: %s" % (head, self.variable.name, self.w.name)
            head = "%s\nCount of Significant I's by Quadrant." % (head)
            head = "%s\n(p<=0.05, permutations: %7.0f)" % (head, self.permutations)
            tab1 = Table(q, colNames=colLabels,
                         rowNames=rowNames,
                         head=head, fmt=[[8, 0]]).table
            tab = "\n".join((tab, tab1))

        return (tab)


class Geary:
    """Geary's C global autocorrelation measure.

    Arguments (3):
        y: STARS variable
        w: STARS weight matrix
        permutations: Number of random spatial permutations (optional)
        varAssumption: "normalization"(default) or "randomization" (optional)

    Attributes
        gc: Global Geary's c
        zc: z-value for gc
        vc: variance of gc
        sc: standard deviation of gc
        zpvalue: probability value based on Z[gc]
        varAssumption: assumption used to calculate vi
        ppvalue: psuedo significance levels (if permutations != 0)

    Example Useage:
        >>> from stars import Project
        >>> s=Project("s")
        >>> s.ReadData("csiss")
        >>> income=s.getVariable("pcincome")
        >>> region=s.getVariable("bea")
        >>> w=spRegionMatrix(region)
        >>> gc = Geary(income,w)
        >>> print(gc.gc[70])
        0.598094478257
    """
    def __init__(self, y, w, permutations=0, varAssumption="normalization"):
        self.varAssumption = varAssumption
        self.w = w
        self.variable = y
        self.permutations = permutations
        pw = spmatrix_to_w(w)
        gc_vals, zc_vals, zpvalue_vals, ppvalue_vals = [], [], [], []
        for t_idx in range(y.t):
            yt = np.asarray(y[:, t_idx]).flatten()
            g_t = _esda.Geary(yt, pw, permutations=permutations,
                              transformation='r')
            gc_vals.append(g_t.C)
            if varAssumption == "normalization":
                zc_vals.append(g_t.z_norm)
                zpvalue_vals.append(g_t.p_norm)
            else:
                zc_vals.append(g_t.z_rand)
                zpvalue_vals.append(g_t.p_rand)
            if permutations:
                ppvalue_vals.append(g_t.p_sim)
        self.gc = np.array(gc_vals)
        self.zc = np.array(zc_vals)
        self.zpvalue = zpvalue_vals
        if varAssumption == "normalization":
            self.vc = g_t.VC_norm
            self.sc = g_t.seC_norm
        else:
            self.vc = g_t.VC_rand
            self.sc = g_t.seC_rand
        if permutations:
            self.ppvalue = np.reshape(ppvalue_vals, [1, y.t])

    def extreme(self, gc):
        """Determines number of permutated gc values that are more
        extreme than original gc. To be used internally, not public.

        Arguments (1)
            gc: permutation gc value
        """
        # if zi - then inc if mi < self.mi
        # if zi + then inc if mi > self.mi
        zn = self.zc < 0
        mlt = gc < self.gc
        zp = self.zc > 0
        mgt = gc > self.gc
        return (zn * mlt) + (zp * mgt)

    def cMoments(self, w):
        n = self.n
        w = self.w.full()
        rs = np.sum(w, axis=1)
        cs = np.sum(w, axis=0)
        self.n, dum = w.shape
        s0 = np.sum(rs)
        self.s0 = s0
        t = rs + cs
        s2 = np.sum(t * t)

        wt = w.T
        wtw = wt + w
        wtw2 = wtw * wtw
        s1 = np.sum(wtw2) / 2.0

        s02 = s0 * s0

        if self.varAssumption == "randomization":
            yd = self.variable - np.mean(self.variable, axis=0)
            k = (1 / np.sum(yd ** 4) * (np.sum(yd ** 2)) ** 2)
            vc = (1 / (n * ((n - 2) ** 2) * s02)) * ((((n - 1) * s1) * (n * n - 3 * n + 3 - (n - 1) * k))
                                                       - ((.25 * (n - 1) * s2) * (n * n + 3 * n - 6 - (n * n - n + 2) * k))
                                                       + (s02 * (n * n - 3 - ((n - 1) ** 2) * k)))
        else:
            vc = ((1 / (2 * (n + 1) * s02)) * ((2 * s1 + s2) * (n - 1) - 4 * s02))

        self.vc = vc
        self.sc = np.sqrt(vc)

    def calc(self, yt):
        w = self.w.full()
        yi = np.diag(yt) @ self.iMat
        yj = self.iMat @ np.diag(yt)
        yd = yt - np.mean(yt)
        yijd = yi - yj
        yd2 = yijd * yijd
        num = np.sum(w * yd2)
        den = (yd.T @ yd) * 2. * self.s0
        c = (self.n - 1) * num / den
        return c

    def report(self):
        """Pretty formatting of summary results"""
        head = "Global Geary's C Test for Spatial Autocorrelation"
        head = "%s\nVariable: %s\nWeight Matrix: %s" % (head, self.variable.name, self.w.name)
        rowLabels = self.variable.timeString
        gc = np.array(self.gc)
        body = np.transpose(np.array((gc, self.zc, self.zpvalue)))
        if self.permutations == 0:
            colLabels = ["Global C", "z", "p-value"]
        else:
            head = "%s\nPermutations: %d\n" % (head, self.permutations)
            colLabels = ["C", "pvalue"]
            n = self.ppvalue.shape[1]
            ppvalue = np.reshape(self.ppvalue, (n,))
            body = np.transpose(np.array((self.gc, ppvalue)))

        tab = Table(body, head=head,
                    rowNames=rowLabels,
                    colNames=colLabels).table
        return (tab)


class LocalGeary:
    """Geary's c measure of local spatial autocorrelation.

    Arguments (3):
        y: STARS variable
        w: STARS weight matrix
        permutations: Number of random spatial permutations (optional)

    Attributes
        ci: Local Geary's c (n by t array)
        expCi: expected ci value (n by 1 array)
        ppvalue: psuedo significance levels(if permutations != 0)(n by t array)

    Example Useage:
        >>> from stars import Project
        >>> s=Project("s")
        >>> s.ReadData("csiss")
        >>> income=s.getVariable("pcincome")
        >>> galstates = open("states48.gal",'r')
        >>> ws = galstates.readlines()
        >>> galstates.close()
        >>> galinfo = list(map(int,"".join(ws).split()))
        >>> wsp = spGalMatrix("wsp",galinfo)
        >>> np.random.seed(10)
        >>> ci = LocalGeary(income,wsp,permutations = 3)
        >>> print(ci.expCi[4])
        [ 1.]
        >>> print(ci.ci[4,3])
        0.186488440026
        >>> print(ci.ppvalue[4,3])
        0.5
    """

    def __init__(self, y, w, permutations=0):
        N = y.n * 1.0
        self.variable = y
        self.w = w.full()
        self.sumw = np.sum(self.w)
        self.expCi = (y.n / self.sumw) * \
                     np.reshape((np.sum(self.w, axis=1) - np.diag(self.w)), (y.n, 1))
        self.den = self.getDen(y)
        self.num = self.getNum(y)
        self.ci = self.num * self.den
        if permutations:
            count = np.ones((y.n, y.t))
            expBox = np.repeat(self.expCi, y.t, axis=1)
            for iter in range(permutations):
                yperm = Variable(permutate(y))
                permNum = self.getNum(yperm)
                count += (permNum > self.num) * (self.ci > expBox)
                count += (permNum < self.num) * (self.ci < expBox)
            self.ppvalue = count / (permutations + 1)
        self.w = w

    def getNum(self, y):
        if y.ndim == 1:
            yprime = np.reshape(y, (y.n, y.t)).T
        else:
            yprime = y.T

        # box is an array of shape (t,n,n) where y values are repeated
        # along the rows n times for each time period
        box = np.reshape(yprime, (y.t, y.n, 1))
        box = np.repeat(box, y.n, axis=2)

        # boxprime is an array of shape(t,n,n) where y values are
        # repeated along the columns n times for each time period
        boxprime = np.repeat(yprime, y.n, axis=0)
        boxprime = np.reshape(boxprime, (y.t, y.n, y.n))

        # The last line of this method converts the results
        # back into a (n,t) array.
        return np.transpose(np.sum(((box - boxprime) ** 2 * self.w), axis=2))

    def getDen(self, y):
        if y.ndim == 1:
            yt = np.reshape(y, (y.n, y.t))
        else:
            yt = y
        yd = (yt - np.mean(yt, axis=0)) ** 2
        return (y.n * (y.n - 1) / 2) / np.sum(yd) / self.sumw

    def report(self):
        rowNames = self.variable.regionNames
        colNames = self.variable.timeString
        colLabels = ["T0"]
        head = "Local Geary's C"
        head = "%s\nVarible: %s\nWeight Matrix: %s" \
               % (head, self.variable.name, self.w.name)

        n1, k1 = self.ci.shape
        if k1 < 13:
            tab = Table(self.ci, colNames=colNames,
                        rowNames=rowNames,
                        head=head, fmt=[[8, 3]]).table
        else:
            tab = ""
            cols = list(range(12, k1, 13))
            cols.insert(0, 0)
            if cols[-1] != k1:
                cols.append(k1)
            ij = [cols[i:i + 2] for i in range(len(cols) - 1)]
            for i, j in ij:
                body = self.ci[:, i:j]
                t = Table(body, head=head, rowNames=rowNames,
                          colNames=colNames[i:j]).table
                tab += "\n" + t

        return tab


class GlobalG:
    """Computes the global G statistic when passed a STARS variable and
    a weights matrix.

    Arguments:
    y: observations (STARS Variable)
    w: weights matrix (array)
    permutations: number of permutations (int)

    Atributes:
    g: observed global G values for each time period (array)
    expG: the expected G value (float)
    varG: the variance of G for each time period (array)
    zG: the z-score of G for each time period (array)
    pG: the corrsponding p-values for each time period (array)
    gp: results of G for each permutation (array)
    permZ: the z-values calculated from the distribution of
            permutation results (array)
    ppermZ: the corresponding p-values for each time period (array)
    permutations: the number of permutations (int)

    Example Usage:
    >>> from stars import *
    >>> s = Project("s")
    >>> s.ReadData("csiss")
    >>> income = s.getVariable("pcincome")
    >>> galstates = open("states48.gal",'r')
    >>> ws = galstates.readlines()
    >>> galstates.close()
    >>> galinfo = list(map(int,"".join(ws).split()))
    >>> wsp = spGalMatrix("wsp",galinfo)
    >>> gg = GlobalG(income,wsp)
    >>> print(gg.g[17])
    0.0213230137301
    """

    def __init__(self, y, w, permutations=0):
        self.w = w
        w = w.full()
        N = y.n * 1.0
        self.getVariance(y, w)
        self.g = self.getG(y, w)
        ZG = (self.g - self.expG) / pow(self.varG, 0.5)
        self.zG = ZG
        self.permutations = permutations
        pg = np.array(list(map(pdf.zprob, abs(ZG))))
        self.pG = 2 * (1.0 - pg)
        self.variable = y

        if permutations:
            gp = []
            for iter in range(permutations):
                randy = Variable(permutate(y))
                permg = self.getG(randy, w)
                gp.append(permg)
            gp = np.array(gp)
            self.gp = gp
            meang = np.mean(gp, axis=0)
            stdg = np.std(gp, axis=0)
            self.permZ = (self.g - meang) / stdg
            ppermZ = np.array(list(map(pdf.zprob, abs(self.permZ))))
            self.ppermZ = 2 * (1.0 - ppermZ)

            lg = np.sum(self.g < self.gp)
            gg = np.sum(self.g > self.gp)
            ex = (min((lg, gg)) + 1.) / (self.permutations + 1.)
            self.ppermZ = 2.0 * ex

    def getG(self, y, w):
        # Compute G values using 3 dimensional arrays
        if y.ndim == 1:
            yprime = np.reshape(y, (y.n, y.t)).T
        else:
            yprime = y.T

        # box is an array of shape (t,n,n) where y values are repeated
        # along the rows n times for each time period
        box = np.reshape(yprime, (y.t, y.n, 1))
        box = np.repeat(box, y.n, axis=2)

        # boxprime is an array of shape(t,n,n) where y values are
        # repeated along the columns n times for each time period
        boxprime = np.repeat(yprime, y.n, axis=0)
        boxprime = np.reshape(boxprime, (y.t, y.n, y.n))

        denominator = box * boxprime
        numerator = denominator * w

        # The zero axis is time, so summing along the other axes
        # yields values for each time period
        return np.sum(np.sum(numerator, axis=1), axis=1) / np.sum(np.sum(denominator, axis=1), axis=1)

    def getVariance(self, y, w):
        N = y.n * 1.0
        sumW = np.sum(w)
        self.expG = sumW / (N * (N - 1))
        wprime = w.T
        s1 = np.sum((w + wprime) ** 2) / 2.0
        s2 = np.sum((np.sum(w, axis=0) + np.sum(wprime, axis=0)) ** 2) * 1.0
        b0 = (N ** 2 - 3 * N + 3) * s1 - N * s2 + 3 * (sumW ** 2)
        b1 = -1.0 * ((N ** 2 - N) * s1 - 2 * N * s2 + 6 * (sumW ** 2))
        b2 = -1.0 * (2 * N * s1 - (N + 3) * s2 + 6 * (sumW ** 2))
        b3 = 4 * (N - 1) * s1 - 2 * (N + 1) * s2 + 8 * (sumW ** 2)
        b4 = s1 - s2 + sumW ** 2
        sumy = np.sum(y, axis=0)
        y2 = y ** 2
        sumy2 = np.sum(y2, axis=0)
        y3 = y2 * y
        sumy3 = np.sum(y3, axis=0)
        y4 = y2 * y2
        sumy4 = np.sum(y4, axis=0)
        numerator = b0 * (sumy2 ** 2) + b1 * sumy4 + b2 * (sumy ** 2) * sumy2 + \
                    b3 * sumy * sumy3 + b4 * (sumy ** 4)
        denominator = ((sumy ** 2 - sumy2) ** 2) * N * (N - 1) * (N - 2) * (N - 3)
        self.varG = numerator / denominator - (self.expG ** 2)

    def report(self):
        varName = self.variable.name

        g = self.g
        zg = self.zG
        pvalueG = self.pG
        head = "Global G"
        head = "%s\nVariable; %s\nWeight Matrix: %s" \
               % (head, varName, self.w.name)
        rowLabels = self.variable.timeString
        colLabels = ["G", "z", "p-(N)"]
        t = self.variable.t
        g = np.reshape(self.g, [t, 1])
        z = np.reshape(self.zG, [t, 1])
        p = np.reshape(self.pG, [t, 1])
        if self.permutations:
            colLabels.append("p-(P)")
            pp = np.reshape(self.ppermZ, [t, 1])
            res = np.concatenate((g, z, p, pp), 1)
            head = "%s\nPermutations: %d" % (head, self.permutations)
        else:
            res = np.concatenate((g, z, p), 1)
        tab = Table(res, head=head,
                    rowNames=rowLabels,
                    colNames=colLabels).table
        return (tab)


class LocalG:
    """Computes the local G statistics when passed a STARS variable and
    a weights matrix.  The weights matrix may be either contiguity or a
    distance matrix.  First converts the weights matrix to a binary
    weight. In the case of contiguity, every non zero weight is assigned
    a 1 and every zero weight remains a zero.  In the case of distance,
    every value less than or equal to the distance parameter is assigned
    a one, else zero.

    Arguments (6, 4 optional):
    y: observations (STARS Variable)
    w: weights matrix (array)
    star: values at points are included in analysis at that point (bool)
    permutations: number of permutations (int)
    matrix: the valid values are "contiguity" and "distance" (string)
    distance: the distance of study only used for distance matrix (number)

    Atributes:
    gi: observed local G values for each observation at each time (array)
    pgi: the corrsponding p-values for each gi (array)
    mcp: monte carlo p-values for each observation at each time (array)
    w: the binary weights matrix used to calculate the statistics (array)
    star: values at points are included in analysis at that point (bool)
    permutations: the number of permutations (int)

    Example Usage:
    >>> from stars import *
    >>> s = Project("s")
    >>> s.ReadData("csiss")
    >>> income = s.getVariable("pcincome")
    >>> galstates = open("states48.gal",'r')
    >>> ws = galstates.readlines()
    >>> galstates.close()
    >>> galinfo = list(map(int,"".join(ws).split()))
    >>> wsp = spGalMatrix("wsp",galinfo)
    >>> lg = LocalG(income,wsp)
    >>> print(lg.gi[4,15])
    -0.60894240796
    >>> print(lg.pgi[43,70])
    0.389521421787
    """
    def __init__(self, y, w, star=0, permutations=0, matrix='contiguity',
                 distance=0.0):
        N = y.n * 1.0
        self.w = self.getBinaryW(w.full(), N, star, matrix, distance)
        gi = self.getGi(y, star)

        if permutations:
            mcp = np.ones(y.shape)
            for iter in range(permutations):
                randy = Variable(permutate(y))
                permg = self.getGiPerm(randy, star)
                permg = np.where((permg * gi) > 0., abs(permg), 0.0)
                mcp += (permg > abs(gi))
            mcp /= (permutations + 1.)
            self.mcp = mcp

        pgi = np.array([list(map(pdf.zprob, abs(r))) for r in gi])
        self.pgi = 2.0 * (1.0 - pgi)
        self.permutations = permutations
        self.star = star
        self.gi = gi
        del [self.denominator, self.numerator, self.sumofw2, self.sumw,
             self.sumwsqrd, self.term1, self.term2, self.xbar]
        if self.star == 0:
            del self.revI

    def getGi(self, y, star):
        if y.ndim == 1:
            yprime = np.reshape(y, (y.n, y.t)).T
        else:
            yprime = y.T
        # boxprime is an array of shape(t,n,n) where y values are
        # repeated along the columns n times for each time period
        boxprime = np.repeat(yprime, y.n, axis=0)
        boxprime = np.reshape(boxprime, (y.t, y.n, y.n))

        # These are the weights matrix moments and sums
        sumw = np.reshape(np.sum(self.w, axis=1), (y.n, 1))
        self.sumw = sumw
        sumwsqrd = sumw ** 2
        self.sumwsqrd = sumwsqrd
        w2 = self.w * self.w
        sumofw2 = np.reshape(np.sum(w2, axis=1), (y.n, 1))
        self.sumofw2 = sumofw2

        # The numerator, denominator and intermediate arrays
        # are (t,n,1) arrays.
        # The last line of this method converts the results
        # back into a (n,t) array.
        if star:
            xbar = np.reshape(np.sum(boxprime, axis=2) / y.n, (y.t, y.n, 1))
            s = np.reshape(np.sum(boxprime ** 2, axis=2) / y.n, (y.t, y.n, 1))
            s = np.sqrt(s - xbar ** 2)
            denominator = s * np.sqrt((y.n * sumofw2 - sumwsqrd) / (y.n - 1))
        else:
            xbar = np.reshape(np.sum(boxprime * self.revI, axis=2) / (y.n - 1), (y.t, y.n, 1))
            s = np.reshape(np.sum((boxprime * self.revI) ** 2, axis=2) / (y.n - 1), (y.t, y.n, 1))
            s = np.sqrt(s - xbar ** 2)
            denominator = s * np.sqrt(((y.n - 1) * sumofw2 - sumwsqrd) / (y.n - 2))

        term1 = np.reshape(np.sum(boxprime * self.w, axis=2), (y.t, y.n, 1))
        term2 = sumw * xbar
        numerator = term1 - term2

        self.term1 = term1
        self.term2 = term2
        self.denominator = denominator
        self.numerator = numerator
        self.sumw = sumw
        self.xbar = xbar
        return np.reshape(numerator / denominator, (y.t, y.n)).T

    def getGiPerm(self, y, star):
        if y.ndim == 1:
            yprime = np.reshape(y, (y.n, y.t)).T
        else:
            yprime = y.T
        # boxprime is an array of shape(t,n,n) where y values are
        # repeated along the columns n times for each time period
        boxprime = np.repeat(yprime, y.n, axis=0)
        boxprime = np.reshape(boxprime, (y.t, y.n, y.n))

        # The numerator, denominator and intermediate arrays
        # are (t,n,1) arrays.
        # The last line of this method converts the results
        # back into a (n,t) array.
        if star:
            term1 = np.reshape(np.sum(boxprime * self.w, axis=2), (y.t, y.n, 1))
            numerator = term1 - self.term2
            return np.reshape(numerator / self.denominator, (y.t, y.n)).T
        else:
            xbar = np.reshape(np.sum(boxprime * self.revI, axis=2) / (y.n - 1), (y.t, y.n, 1))
            s = np.reshape(np.sum((boxprime * self.revI) ** 2, axis=2) / (y.n - 1), (y.t, y.n, 1))
            s = np.sqrt(s - xbar ** 2)
            denominator = s * np.sqrt(((y.n - 1) * self.sumofw2 - self.sumwsqrd) / (y.n - 2))
            term1 = np.reshape(np.sum(boxprime * self.w, axis=2), (y.t, y.n, 1))
            term2 = self.sumw * xbar
            numerator = term1 - term2
            return np.reshape(numerator / denominator, (y.t, y.n)).T

    def getBinaryW(self, w, N, star, matrix, distance):
        I = np.eye(int(N))
        if matrix == "contiguity":
            if star:
                neww = np.where((w + I) > 0.0, 1.0, 0.0)
            else:
                revI = np.where(I == 1, 0.0, 1.0)
                neww = np.where((w * revI) > 0.0, 1.0, 0.0)
                self.revI = revI
        elif matrix == "distance":
            if star:
                neww = np.where(w <= distance, 1.0, 0.0)
            else:
                revI = np.where(I == 1, 0.0, 1.0)
                neww = np.where(w <= distance, 1.0, 0.0) * revI
                self.revI = revI
                print(neww[0])
        return neww


class TraceTest:
    """Spatial autocorrelation test based on Quah's regional
    conditioning."""
    def __init__(self, variable, w, bins=[], permutations=0, nlag=0):
        self.variable = variable
        n, T = self.variable.shape
        self.w = w
        lag = slag(w, variable)
        regRel = variable / lag
        self.regRel = regRel
        self.lag = lag
        baseRel = variable / np.mean(variable, axis=0)
        self.baseRel = baseRel
        rangeT = np.arange(T)

        if bins:
            self.bins = bins
        else:
            self.quints = [Markov.Quintilizer(baseRel[:, time]).quintiles for time in range(T)]
            self.bins = self.quints
            bins = self.bins

        results = [self.traceValue(variable[:, t], lag[:, t], bins[t]) for t in rangeT]
        self.traces = [i[0] for i in results]
        self.tMats = [i[1] for i in results]
        self.tOrig = results
        comp = np.zeros([T, 1])
        if permutations:
            TP = []
            permRes = np.zeros([T, permutations])
            for p in range(permutations):
                variable = permutate(variable)
                wy = slag(w, variable)
                results = [self.traceValue(variable[:, t], wy[:, t], bins[t]) for t in rangeT]
                traces = [i[0] for i in results]
                test = traces < self.traces
                comp += test
                TP.append(traces)
            self.pvalue = comp
            self.TP = np.array(TP)
            comp = self.TP < self.traces
            self.comp = np.sum(comp)
            self.pvalue = self.comp * 1. / permutations
            self.permutations = permutations
        else:
            self.permutations = 0

    def traceValue(self, y, wy, bins):
        baseRel = y / np.mean(y)
        regRel = y / wy
        regRelClasses = np.searchsorted(bins, regRel)
        baseRelClasses = np.searchsorted(bins, baseRel)
        self.regClass = regRelClasses
        self.baseClass = baseRelClasses
        k = len(bins)
        k = max(baseRelClasses)
        T = len(regRelClasses)
        tMat = np.zeros([k + 1, k + 1])
        coord = zip(regRelClasses, baseRelClasses)
        for i, j in coord:
            tMat[i, j] += 1
        trace = np.sum(np.diag(tMat))
        return (trace, tMat)

    def report(self):
        """Pretty formatting of summary results"""
        head = "Trace Test for Spatial Autocorrelation"
        head = "%s\nVariable: %s\nWeight Matrix: %s" % (head, self.variable.name, self.w.name)
        rowLabels = self.variable.timeString
        traces = np.array(self.traces)
        traces = np.reshape(traces, [len(traces), 1])
        if self.permutations == 0:
            colLabels = ["Trace"]
            traces = np.array(self.traces)
            traces = np.reshape(traces, [len(traces), 1])
            body = traces
        else:
            head = "%s\nPermutations: %d\n" % (head, self.permutations)
            colLabels = ["Trace", "pvalue"]
            pvalues = np.array(self.pvalue)
            pvalues = np.reshape(pvalues, [len(pvalues), 1])
            body = np.concatenate((traces, pvalues), 1)

        tab = Table(body, head=head,
                    rowNames=rowLabels,
                    colNames=colLabels).table
        return (tab)


def transMat(localq, interval=1):
    """Returns a matrix recording the transitions of the local moran
    statsitic for an interval length over a given period."""
    n, t = localq.shape
    trans = np.zeros([4, 4])
    rn = range(n)
    for t1 in range(t - interval):
        t2 = t1 + interval
        a = localq[:, t1] - 1
        b = localq[:, t2] - 1
        first = np.unique(a)
        for i in first:
            rowmatch = np.nonzero(a == i)[0]
            c = np.take(b, rowmatch)
            cunique = np.unique(c)
            for j in cunique:
                jn = np.sum(c == j)
                trans[i, j] += jn
    return trans


class PolyChar:
    """Calculates Polygon Area and Centroid"""
    def __init__(self, coords):
        n = len(coords)
        xi = range(0, n, 2)
        x = [coords[i] for i in xi]
        y = [coords[i + 1] for i in xi]
        npts = len(x)
        nr = range(npts - 1)
        s = [x[i] * y[i + 1] - x[i + 1] * y[i] for i in nr]
        area = abs(sum(s) / 2.)
        scx = [(x[i] + x[i + 1]) * (x[i] * y[i + 1] - x[i + 1] * y[i]) for i in nr]
        scy = [(y[i] + y[i + 1]) * (x[i] * y[i + 1] - x[i + 1] * y[i]) for i in nr]
        try:
            cx = (1 / (6. * area)) * sum(scx)
            cy = (1 / (6. * area)) * sum(scy)
        except:
            cx = sum(x) / len(x)
            cy = sum(y) / len(y)
        bb = (min(x), min(y), max(x), max(y))
        self.bb = bb
        self.area = area
        self.centroid = (cx, cy)


def _test():
    import doctest
    import Esda
    return doctest.testmod(Esda)


if __name__ == "__main__":
    _test()
