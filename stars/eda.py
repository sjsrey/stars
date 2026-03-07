"""
Exploratory and classic data analysis module for Space-Time Analysis
of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

This module implements the primitive graphics classes for STARS.


"""

import numpy as np

# stars imports
from stars import *
from Data import *
from Messages import *
from Utility import *
import pdf
import Markov


class Summary:
    """Summary statistics for a variable or matrix of variables. The
    latter need to be organized as columns in x"""
    def __init__(self, x):
        if isinstance(x, list):
            x = np.array(x)
            n = len(x)
            try:
                x = np.reshape(x, (n, 1))
            except:
                pass
        n, k = x.shape
        self.n = n
        self.k = k
        minx = np.min(x, axis=0)
        maxx = np.max(x, axis=0)
        medx = np.median(x, axis=0)
        meanx = np.mean(x, axis=0)

        self.minx = minx
        self.maxx = maxx
        self.median = medx
        self.mean = meanx
        xsorted = np.sort(x, axis=0)
        self.xsorted = xsorted
        if n % 2:
            mp = int(np.floor(n / 2.))
            x1 = np.take(xsorted, list(range(mp)), axis=0)
            self.q1 = np.median(x1, axis=0)
            x2 = np.take(xsorted, list(range(mp + 1, n)), axis=0)
            self.q3 = np.median(x2, axis=0)
        else:
            n2 = n // 2
            x1 = np.take(xsorted, list(range(n2)), axis=0)
            self.q1 = np.median(x1, axis=0)
            x2 = np.take(xsorted, list(range(n2, n)), axis=0)
            self.q3 = np.median(x2, axis=0)

        results = [minx, self.q1, self.median, self.mean, self.q3, maxx]
        self.results = np.transpose(np.array([x.tolist() for x in results]))
        self.colNames = "min", "q1", "median", "mean", "q3", "max"


class Dist:
    """Variance,s,cv skeweness, kurtosis """
    def __init__(self, x):
        if isinstance(x, list):
            x = np.array(x)
            n = len(x)
            try:
                x = np.reshape(x, (n, 1))
            except:
                pass
        n, k = x.shape
        self.n = n
        self.k = k
        sx = np.std(x, axis=0)
        vx = sx ** 2
        self.sd = sx
        self.var = vx
        cv = sx / np.mean(x, axis=0)
        self.cv = cv
        xd = x - np.mean(x, axis=0)
        xd3 = xd ** 3
        xd4 = xd ** 4
        sk = np.sum(xd3, axis=0) / (n * (sx ** 3))
        ku = (np.sum(xd4, axis=0) / (n * (sx ** 4))) - 3.
        self.skew = sk
        self.kurt = ku

        bj = n * ((sk ** 2) / 6. + (ku ** 2) / 24.)
        self.bj = bj
        pbj = np.array([pdf.chicdf(bji, 2) for bji in bj])
        self.bjp = pbj
        results = [sx, vx, cv, sk, ku, bj, pbj]
        self.results = np.transpose(np.array([x.tolist() for x in results]))
        self.colNames = "s", "s2", "cv", "sk", "kurt", "b-j", "p(b-j)"


if __name__ == '__main__':
    x = np.arange(100)
    x = np.reshape(x, (20, 5))
    s = Summary(x)
    print(s.n, s.k)
    y = list(range(20))
    sy = Summary(y)

    z = np.arange(27)
    z = np.reshape(z, (9, 3))
    sz = Summary(z)

    zv = Dist(z)
