"""
Exploratory and classic data analysis module for Space-Time Analysis 
of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

This module implements the primitive graphics classes for STARS.


"""

from numpy.oldnumeric import *
from numpy.oldnumeric.mlab import *

# stars imports
from stars import *
from Data import *
from Messages import *
from Utility import *
from numpy.oldnumeric.random_array import *
import pdf
import Markov
import types


class Summary:
    """Summary statistics for a variable or matrix of variables. The
    latter need to be organized as columns in x"""
    def __init__(self,x):
        if isinstance(x,types.ListType):
            x = array(x)
            n = len(x)
            try:
                x = reshape(x,(n,1))
            except:
                pass
        n,k=shape(x)
        self.n = n
        self.k = k
        minx = min(x)
        maxx = max(x)
        medx = median(x)
        meanx = mean(x)

        self.minx = minx
        self.maxx = maxx
        self.median = medx
        self.mean = meanx
        xsorted = sort(x,0)
        self.xsorted = xsorted
        if n%2:
            #print "odd"
            mp = floor(n/2.)
            x1 = take(xsorted,range(mp))
            self.q1 = median(x1)
            x2 = take(xsorted,range(mp+1,n))
            self.q3 = median(x2)

        else:
            #print "even"
            n2 = n / 2
            x1 = take(xsorted,(range(n2)))
            self.q1 = median(x1)
            x2 = take(xsorted,(range(n2,n)))
            self.q3 = median(x2)

        results = [minx,self.q1,self.median,self.mean,self.q3,maxx]
        self.results = transpose(array([ x.tolist() for x in results]))
        self.colNames = "min","q1","median","mean","q3","max"

class Dist:
    """Variance,s,cv skeweness, kurtosis """
    def __init__(self,x):
        if isinstance(x,types.ListType):
            x = array(x)
            n = len(x)
            try:
                x = reshape(x,(n,1))
            except:
                pass
        n,k=shape(x)
        self.n = n
        self.k = k
        minx = min(x)
        maxx = max(x)
        sx = std(x)
        vx = sx**2
        self.sd=sx
        self.var=vx
        cv = sx / mean(x)
        self.cv = cv
        xd = x - mean(x)
        xd3 = xd**3
        xd4 = xd**4
        sk = sum(xd3) /( n * (sx**3))
        ku = (sum(xd4) / (n*(sx**4))) - 3.
        self.skew = sk
        self.kurt = ku

        bj = n * ( (sk**2)/6. +  (ku**2)/24. )
        self.bj = bj
        pbj = array([pdf.chicdf(bji,2) for bji in bj])
        self.bjp = pbj
        results = [sx,vx,cv,sk,ku,bj,pbj]
        self.results = transpose(array([x.tolist() for x in results]))
        self.colNames = "s","s2","cv","sk","kurt","b-j","p(b-j)"




if __name__ == '__main__':
    from numpy.oldnumeric import *

    
    x=arange(100)
    x=reshape(x,(20,5))
    s = Summary(x)
    print s.n,s.k
    y=range(20)
    sy = Summary(y)

    z = arange(27)
    z = reshape(z,(9,3))
    sz = Summary(z)

    zv = Dist(z)

    

