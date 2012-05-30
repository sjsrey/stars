"""
Distribution functions and probabilities module 
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006 Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================
Adapted from original stats.py by
Copyright (c) 1999-2000 Gary Strangman; All Rights Reserved.

This software is distributable under the terms of the GNU
General Public License (GPL) v2, the text of which can be found at
http://www.gnu.org/copyleft/gpl.html. Installing, importing or otherwise
using this module constitutes acceptance of the terms of this License.

Disclaimer

This software is provided "as-is".  There are no expressed or implied
warranties of any kind, including, but not limited to, the warranties
of merchantability and fittness for a given application.  In no event
shall Gary Strangman be liable for any direct, indirect, incidental,
special, exemplary or consequential damages (including, but not limited
to, loss of use, data or profits, or business interruption) however
caused and on any theory of liability, whether in contract, strict
liability or tort (including negligence or otherwise) arising in any way
out of the use of this software, even if advised of the possibility of
such damage.

Comments and/or additions are welcome (send e-mail to:
strang@nmr.mgh.harvard.edu).
 

OVERVIEW

"""


import math
from numpy.oldnumeric import *
import scipy.stats as STATS
def chicdf(chisq,df):
    """
Returns the (1-tailed) probability value associated with the provided
chi-square value and df.  Adapted from chisq.c in Gary Perlman's |Stat.

Usage:   chicdf(chisq,df)
"""
    BIG = 20.0
    def ex(x):
	BIG = 20.0
	if x < -BIG:
	    return 0.0
	else:
	    return math.exp(x)

    if chisq <=0 or df < 1:
	return 1.0
    a = 0.5 * chisq
    if df%2 == 0:
	even = 1
    else:
	even = 0
    if df > 1:
	y = ex(-a)
    if even:
	s = y
    else:
	s = 2.0 * zprob(-math.sqrt(chisq))
    if (df > 2):
	chisq = 0.5 * (df - 1.0)
	if even:
	    z = 1.0
	else:
	    z = 0.5
	if a > BIG:
	    if even:
		e = 0.0
	    else:
		e = math.log(math.sqrt(math.pi))
	    c = math.log(a)
	    while (z <= chisq):
		e = math.log(z) + e
		s = s + ex(c*z-a-e)
		z = z + 1.0
	    return s
	else:
	    if even:
		e = 1.0
	    else:
		e = 1.0 / math.sqrt(math.pi) / math.sqrt(a)
		c = 0.0
		while (z <= chisq):
		    e = e * (a/float(z))
		    c = c + e
		    z = z + 1.0
		return (c*y+s)
    else:
	return s


def zprob(z):
    """
Returns the area under the normal curve 'to the left of' the given z value.
Thus, 
    for z<0, zprob(z) = 1-tail probability
    for z>0, 1.0-zprob(z) = 1-tail probability
    for any z, 2.0*(1.0-zprob(abs(z))) = 2-tail probability
Adapted from z.c in Gary Perlman's |Stat.

Usage:   zprob(z)
"""
    return STATS.norm.pdf(z)


def fprob (dfnum, dfden, F):
    """
Returns the (1-tailed) significance level (p-value) of an F
statistic given the degrees of freedom for the numerator (dfR-dfF) and
the degrees of freedom for the denominator (dfF).

Usage:   fprob(dfnum, dfden, F)   where usually dfnum=dfbn, dfden=dfwn
"""
    p = betai(0.5*dfden, 0.5*dfnum, dfden/float(dfden+dfnum*F))
    return p


def betacf(a,b,x):
    """
This function evaluates the continued fraction form of the incomplete
Beta function, betai.  (Adapted from: Numerical Recipies in C.)

Usage:   betacf(a,b,x)
"""
    ITMAX = 200
    EPS = 3.0e-7

    bm = az = am = 1.0
    qab = a+b
    qap = a+1.0
    qam = a-1.0
    bz = 1.0-qab*x/qap
    for i in range(ITMAX+1):
	em = float(i+1)
	tem = em + em
	d = em*(b-em)*x/((qam+tem)*(a+tem))
	ap = az + d*am
	bp = bz+d*bm
	d = -(a+em)*(qab+em)*x/((qap+tem)*(a+tem))
	app = ap+d*az
	bpp = bp+d*bz
	aold = az
	am = ap/bpp
	bm = bp/bpp
	az = app/bpp
	bz = 1.0
	if (abs(az-aold)<(EPS*abs(az))):
	    return az
    print 'a or b too big, or ITMAX too small in Betacf.'

def betai(a,b,x):
    """
Returns the incomplete beta function:

    I-sub-x(a,b) = 1/B(a,b)*(Integral(0,x) of t^(a-1)(1-t)^(b-1) dt)

where a,b>0 and B(a,b) = G(a)*G(b)/(G(a+b)) where G(a) is the gamma
function of a.  The continued fraction formulation is implemented here,
using the betacf function.  (Adapted from: Numerical Recipies in C.)

Usage:   betai(a,b,x)
"""
    if (x<0.0 or x>1.0):
	raise ValueError, 'Bad x in lbetai'
    if (x==0.0 or x==1.0):
	bt = 0.0
    else:
	bt = math.exp(gammln(a+b)-gammln(a)-gammln(b)+a*math.log(x)+b*
		      math.log(1.0-x))
    if (x<(a+1.0)/(a+b+2.0)):
	return bt*betacf(a,b,x)/float(a)
    else:
	return 1.0-bt*betacf(b,a,1.0-x)/float(b)

def tpvalue(t,df):
    """Returns the upper tail area for a t variate with df degrees of
    freedom.

    Arguments:
        t: t-statistic (scalar)
        df: degrees of freedom parameter

    Returns:
        pvalue: complement of the cdf for a t with df degrees of
        freedom.

    Author:
        Serge Rey based on modification of code in stats.py by 
        Gary Strangman.

    """
    prob = betai(0.5*df,0.5,float(df)/(df+t*t))
    return(prob)



def gammln(xx):
    """
Returns the gamma function of xx.
    Gamma(z) = Integral(0,infinity) of t^(z-1)exp(-t) dt.
(Adapted from: Numerical Recipies in C.)

Usage:   gammln(xx)
"""

    coeff = [76.18009173, -86.50532033, 24.01409822, -1.231739516,
	     0.120858003e-2, -0.536382e-5]
    x = xx - 1.0
    tmp = x + 5.5
    tmp = tmp - (x+0.5)*math.log(tmp)
    ser = 1.0
    for j in range(len(coeff)):
	x = x + 1
	ser = ser + coeff[j]/x
    return -tmp + math.log(2.50662827465*ser)



def dnorm(x,sigma=1,xbar=0):
    """evaluate normal distribution at x
    Arguments:
        x
        sigma: standard deviation
        xbar: mean value of x
    Returns:
        pdf: height of normal pdf at x
    
    Notes:
        original by Serge Rey <serge@rohan.sdsu.edu>
    
    """
    z=(x-xbar)/sigma
    zp = z > 20.
    zn = z < -20.
    zok = zp + zn

    z = ( zp * 20. ) + ( zn  *  -20. ) +  z * (zok == 0)
    try:
        return (1./((2*pi)**(1/2.)) * exp(-(1/2.) * z**2))
    except:
        print max(z),min(z)
        return z
def iqr(x):
    """inter-quartile range
    Arguments:
        x: array of values
    Returns:
        iqr: inter-quartile range for x
    
    Notes:
        original by Serge Rey <serge@rohan.sdsu.edu>
    """
    sx=sort(x)
    n=len(sx)
    if (n%2 == 0):
        n2=n/2
    else:
        n2=(n+1)/2 - 1 # zero offset
    q1=median(sx[:n2+1])
    q2=median(sx[n2:])
    return q2-q1 


class Kde:
    """Kernel Density Estimation

    Arguments:
        y: one-dimensional array
        kernel: type of kernel: Gaussian or Uniform
        h: bandwidth: default h=1.06 (min(sy,iqr/1.34) n^(-1/5), where
        sy is standard deviation of y, iqr is inter-quartile range and n
        is sample size
        xmin: minimum value of x-axis: default = min(y)-0.35*min(y)
        xmax: maximum value of x-axis: default = max(y)+0.35*max(y)
        npoints: number of points on x-axis density is estimated at
   
    Attributes:
        h: bandwidth
        xmin: minimum value of x-axis
        xmax: maximum value of x-axis
        npoint: number of points on x-axis
        xgrid: xaxis
        fx: height of density at each point in xgrid

    Methods
        integrate:
            returns cdf for passed in value

    Notes:
        original by Serge Rey <serge@rohan.sdsu.edu>

    Example Useage:
    >>> from stars import *
    >>> s = Project("s")
    >>> s.ReadData("csiss")
    >>> inc=s.getVariable("pcincome")
    >>> i29=inc[:,0]
    >>> kde29=Kde(i29)
    >>> print "Estimated cdf for income of 650: %6.3f"%kde29.integrate(650)
    Estimated cdf for income of 650:  0.578
    """
    def __init__(self,y,kernel="Gaussian",h=0,xmin=None,xmax=None,npoints=100):
        if xmin or xmax:
            xrange=xmax-xmin
        else:
            xmax=max(y)
            xmin=min(y)
            xrange=xmax-xmin
            xmax=xmax + .35 * xrange
            xmin=xmin - .35 * xrange
            xrange=xmax-xmin
        xd = xrange*1./npoints
        xgrid=arange(xmin,xmax,xd)
        self.xgrid=xgrid    
        self.xmax=xmax      
        self.xmin=xmin
        self.xd = xd
        n=len(y)
        if h == 0:

            sy = reshape(y,(len(y),1)).std()
            iqr1 = iqr(y)/1.34
            if sy < iqr1:
                H = sy
            else:
                H = iqr1
            h = 1.06 * H * n**(-1/5.)
        self.h=h

        if kernel=="Gaussian":
            nh = n*h
    #        print (xgrid[0] - y)/h
    #        raw_input("pause")
            fx = [ sum(dnorm( (a-y)/h )/h )/n for a in xgrid]
            self.fx=fx
            
        elif kernel=="Uniform":
            nh2=n*h*2.
            fx = [ sum( (abs(a-y)/h <= 1.0))/nh2 for a in xgrid]
            self.fx=fx
            
        else:
            print "Non-recognized Kernel"

    def integrate(self,xval=None):
        "Integrate the empirical density from -inf up to xval."
        height=self.fx
        width=self.xd
        xgrid=self.xgrid
        if xval:
            n=sum(xgrid<=xval)
        else:
            n=len(height)
        cdf=sum([width*h for h in height[:n]])
        return cdf

    def createCDF(self):
        cdf = [ self.integrate(i) for i in self.xgrid ]
        return cdf
    


if __name__ == '__main__':
    import doctest,pdf
    doctest.testmod(pdf)

    chval=9.21
    dof = 2 
    pv = chicdf(chval,dof)
    print pv

    chval=3.84
    pv = chicdf(chval,1)
    print pv

    chval=8.55
    pv = chicdf(chval,15)
    print pv

    from stars import *
    s=Project("s")
    s.ReadData("csiss")
    inc = s.getVariable("pcincome")
    ky = Kde(inc[:,0])
