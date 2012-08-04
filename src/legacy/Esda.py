"""
Exploratory spatial data analysis module for STARS 
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Jared Aldstad aldstad@rohan.sdsu.edu
----------------------------------------------------------------------
Copyright (c) 2000-2006 Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

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
from numpy.oldnumeric  import *
#from MLab import *

# stars imports
import numpy as np
from stars import *
from Data import *
from Messages import *
from Utility import *
from numpy.oldnumeric.random_array  import *
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
    def __init__(self,y,w,permutations=0,varAssumption = "normalization"):
        self.variable = y
        if y.t == 1: # check for cs variable
            n=y.n
            y = reshape(y,(n,1))
        self.varAssumption = varAssumption
        self.iMoments(w)
        self.permutations=permutations
        self.w = w
        yd = y - y.mean()
        den = np.dot(transpose(yd),yd)
        print sum(sum(den==0))
        # from here down changes for permutations (not done yet)
        # check for permutation and then permutate the yd
        ylag = lag(yd,w)
        self.ylag = lag(y,w)
        num = np.dot(transpose(yd),ylag)
        if len(shape(num)) > 1:
            self.mi = diag(num/den)
            self.zi = (self.mi - self.ei)/self.si
            n,t=shape(ylag)
        else:
            n=len(y)
            t=1
            self.mi = num/den
            self.zi = (self.mi - self.ei)/self.si
            
        self.npvalue = [ 1 - pdf.zprob(abs(x)) for x in self.zi]
        if permutations:
            Message("Moran's I, %d permutations for %d regions and %d time periods"
            %(permutations,n,t))
            mip = []
            count =zeros([1,t]) 
            for iter in range(permutations):
                ylag=lag(permutate(yd),w)
                num = dot(transpose(yd),ylag)
                if len(shape(num)) > 1:
                    mi = diag(num/den)
                else:
                    mi = num/den
                count += self.extreme(mi)
                mip.append(mi)
            self.ppvalue = count/(permutations * 1.0)
    def report(self):
        """Pretty formatting of summary results"""
        head="Moran's I"
        head = "%s\nVariable: %s\nWeight Matrix: %s"%(head,self.variable.name,self.w.name)
        rowLabels = self.variable.timeString
        colLabels = ["MI","z","p-(N)"]
 
        t=self.variable.t
        print t
        print self.mi.shape
        m=reshape(self.mi,[t,1])
        p=reshape(self.npvalue,[t,1])
        z=reshape(self.zi,[t,1])
        res=concatenate((m,z,p),1)
        self.junk = res
        if self.permutations:
            colLabels.append("p-(P)")
            pp =reshape(self.ppvalue,[t,1])
            res=concatenate((m,z,p,pp),1)
            head = "%s\nPermutations: %d"%(head,self.permutations)
        else:

            res=concatenate((m,z,p),1)

        head = "%s\nExpected Value: %8.3f"%(head,self.ei)
        tab = Table(res,head=head,
            rowNames = rowLabels,
            colNames = colLabels).table
        return(tab)
        



    def extreme(self,mi):
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
        


    def iMoments(self,w):
        "Moments for Moran's I under normality assumption."
        w = w.full()
        rs = sum(w,1)
        cs = sum(w)
        n,dum = w.shape 
        s0 = sum(rs)
        t= rs+cs
        s2 = sum(t*t)
        
        wt=transpose(w)
        wtw=wt+w
        wtw2=wtw*wtw
        s1=(sum(sum(wtw2)))/2.0
        ei = -1.0 / (n - 1) 

        s02 = s0*s0

        if self.varAssumption == "randomization":
            yd = self.variable - mean(self.variable)
            k = (1/(sum(yd**4)) * ((sum(yd**2))**2))
            vi = (1/(((n-1)**3)*s02)) * ((n*((n*n-3*n+3)*s1 - n*s2+3*s02)) \
                - (k*((n*n-n)*s1-2*n*s2+6*s02)))
        else:
            vi = (( 1/( s02*(n*n-1)) * ( n*n*s1 - n*s2 + 3 * s02  ) ) )

        vi = vi - ei*ei
        self.ei = ei
        self.vi = vi
        self.si = sqrt(vi)   

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
        >>> s.ReadData("data/csiss")
        >>> income=s.getVariable("pcincome")
        >>> galstates = open("data/states48.gal",'r')
        >>> ws = galstates.readlines()
        >>> galstates.close()
        >>> galinfo = map(int,"".join(ws).split())
        >>> wsp = spGalMatrix("wsp",galinfo)
        >>> seed(10,10)
        >>> ii = LocalMoran(income,wsp,permutations = 3)
        >>> print(ii.expMi[4])
        [-0.0212766]
        >>> print(ii.mi[4,3])
        -0.0142149120418
        >>> print(ii.ppvalue[4,3])
        0.75
    """

    def __init__(self,y,w,permutations=0):
        N = y.n * 1.0
        self.variable = y
        self.w = w.full()
        self.yd = Variable(y - mean(y))
        self.sumw = sum(sum(self.w * 1.0))
        self.expMi = ((y.n / self.sumw) * \
                     (reshape((diag(self.w)*y.n-sum(self.w,1)),(y.n,1)))) / \
                     (y.n - 1)
        self.den = self.getDen(self.yd)
        self.num = self.getNum(self.yd)
        self.mi = self.num * self.den

        yl = np.dot(self.w,y)
        self.ylag = Variable(yl - mean(y))

        lp = self.ylag > 0
        yp = self.yd > 0
        yn = self.yd <= 0
        lyn = self.ylag <= 0
        q1 = yp*lp * 1
        q2 = yn*lp * 2
        q3 = yn*lyn * 3
        q4 = yp*lyn * 4
        self.qvalue = q1+q2+q3+q4

        # for map diverging scheme
        d1 = yp*lp * 4  # hh
        d2 = yn*lp * 2  # lh
        d3 = yp*lyn * 3 # hl
        d4 = yn*lyn * 1 # ll

        self.dvalue = d1+d2+d3+d4


        if permutations:
            count = ones((y.n,y.t),Float)
            expBox = repeat(self.expMi,y.t,1)
            for iter in range(permutations):
                yperm = Variable(permutate(self.yd))
                permNum = self.getNum(yperm)
                count += multiply(greater(permNum,self.num), \
                                  greater(self.mi,expBox))
                count += multiply(less(permNum,self.num), \
                                  less(self.mi,expBox))
            self.ppvalue = count / (permutations + 1)
        self.permutations = permutations
        del [self.sumw, self.den, self.num, self.yd, self.w] 
        self.w = w
        
    def getNum(self,yd):
        if len(shape(yd)) == 1:
            ydprime = transpose(reshape(yd,(yd.n,yd.t)))
        else:
            ydprime = transpose(yd)

        #box is an array of shape (t,n,n) where y values are repeated
        #along the rows n times for each time period 
        box = reshape(ydprime,(yd.t,yd.n,1))
        box = repeat(box, yd.n, 2)
    
        #boxprime is an array of shape(t,n,n) where y values are
        #repeated along the columns n times for each time period
        boxprime = repeat(ydprime,yd.n,0)
        boxprime = reshape(boxprime,(yd.t,yd.n,yd.n))

        #The last line of this method converts the results
        #back into a (n,t) array.
        return transpose(sum((box * boxprime * self.w),2))

    def getDen(self,yd):
        if len(shape(yd)) == 1:
            ydtemp = reshape(yd,(yd.n,yd.t))
        else:
            ydtemp = yd
        yd2 = ydtemp**2
        return (yd.n**2) / sum(yd2) / self.sumw 

    def report(self):
        """Formatting of summary results."""

        q = self.qvalue
        q1 = q==1
        q2 = q==2
        q3 = q==3
        q4 = q==4

        n1 = sum(q1,1)
        n2 = sum(q2,1)
        n3 = sum(q3,1)
        n4 = sum(q4,1)
        n = zeros((len(n1),4))
        n[:,0]= n1
        n[:,1]= n2
        n[:,2]= n3
        n[:,3]= n4
        rowNames = self.variable.regionNames
        colLabels = ["Q1","Q2","Q3","Q4"]
        head="Local Moran's I"
        head="%s\nVariable: %s\nWeight Matrix: %s"%(head,self.variable.name,self.w.name)
        head="%s\nCount of I's by Quadrant."%(head)
        tab = Table(n,colNames=colLabels,
                    rowNames=rowNames,
                    head=head,fmt=[[8,0]]).table



        if self.permutations:
            p5 = self.ppvalue <= 0.05

            q1 = sum(p5 * q1,1)
            q2 = sum(p5 * q2,1)
            q3 = sum(p5 * q3,1)
            q4 = sum(p5 * q4,1)

            q=zeros((len(q1),4))
            q[:,0] = q1
            q[:,1] = q2
            q[:,2] = q3
            q[:,3] = q4
            rowNames = self.variable.regionNames
            colLabels = ["Q1","Q2","Q3","Q4"]
            head="Local Moran's I"
            head="%s\nVariable: %s\nWeight Matrix: %s"%(head,self.variable.name,self.w.name)
            head="%s\nCount of Significant I's by Quadrant."%(head)
            head="%s\n(p<=0.05, permutations: %7.0f)"%(head,self.permutations)
            tab1 = Table(q,colNames=colLabels,
                    rowNames=rowNames,
                    head=head,fmt=[[8,0]]).table
            tab = "\n".join((tab,tab1))

        return(tab)
        


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
        >>> s.ReadData("data/csiss")
        >>> income=s.getVariable("pcincome")
        >>> region=s.getVariable("bea")
        >>> w=spRegionMatrix(region)
        >>> gc = Geary(income,w)
        >>> print(gc.gc[70])
        0.598094478257
    """
    def __init__(self,y,w,permutations=0,varAssumption = "normalization"):
        self.varAssumption = varAssumption
        self.w=w
        self.variable = y
        n=y.n
        self.n=n
        self.cMoments(w)
        self.iMat=ones((n,n))
        res=map(self.calc,transpose(y))
        self.gc=array(res)
        self.zc = (self.gc - 1) / self.sc
        self.zpvalue = [ 1 - pdf.zprob(abs(x)) for x in self.zc]
        self.permutations = permutations
        if permutations:
            count = ones([1,y.t])
            resperm=[]
            iterations=range(permutations)
            for it in iterations:
                yp=permutate(y)
                gc = map(self.calc,transpose(yp))
                resperm.append(gc)
                count += self.extreme(gc)
            self.ppvalue = count/(permutations * 1.0 + 1.0)
        #del [self.w,self.n,self.s0,self.iMat]


    def extreme(self,gc):
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

    def cMoments(self,w):
        n = self.n
        w = self.w.full()
        rs = sum(w,1)
        cs = sum(w)
        self.n,dum = w.shape 
        s0 = sum(rs)
        self.s0 = s0
        t= rs+cs
        s2 = sum(t*t)
        
        wt=transpose(w)
        wtw=wt+w
        wtw2=wtw*wtw
        s1=(sum(sum(wtw2)))/2.0

        s02 = s0*s0

        if self.varAssumption == "randomization":
            yd = self.variable - mean(self.variable)

            k = (1/(sum(yd**4)) * ((sum(yd**2))**2))

            vc = (1/(n*((n-2)**2)*s02)) * ((((n-1)*s1) * (n*n-3*n+3-(n-1)*k)) \
                 - ((.25*(n-1)*s2) * (n*n+3*n-6-(n*n-n+2)*k)) \
                    + (s02* (n*n-3-((n-1)**2)*k)))
        else:
            vc = ((1 / (2 * (n+1) * s02)) * ((2*s1+s2) * (n-1) - 4 * s02))

        self.vc = vc
        self.sc = sqrt(vc)
        

        

    def calc(self,yt):
        w = self.w.full()
        yi=np.dot(diag(yt),self.iMat)
        yj=np.dot(self.iMat,diag(yt))
        yd=yt-mean(yt)
        yijd=yi-yj
        yd2=yijd*yijd
        num = sum(sum(w*yd2))
        den = np.dot(transpose(yd),yd) * 2. * self.s0
        c= (self.n - 1) * num/den
        return c

    def report(self):
        """Pretty formatting of summary results"""
        head="Global Geary's C Test for Spatial Autocorrelation"
        head = "%s\nVariable: %s\nWeight Matrix: %s"%(head,self.variable.name,self.w.name)
        rowLabels = self.variable.timeString
        gc=array(self.gc)
        body = transpose(array((gc,self.zc,self.zpvalue)))
        if self.permutations==0:
            colLabels = ["Global C","z","p-value"]
        else:
            head = "%s\nPermutations: %d\n"%(head,self.permutations)
            colLabels = ["C","pvalue"]
            n = shape(self.ppvalue)[1]
            ppvalue = reshape(self.ppvalue,(n,))
            body = transpose(array((self.gc,ppvalue)))


        tab = Table(body,head=head,
        rowNames = rowLabels,
        colNames = colLabels).table
        return(tab)
        

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
        >>> galinfo = map(int,"".join(ws).split())
        >>> wsp = spGalMatrix("wsp",galinfo)
        >>> seed(10,10)
        >>> ci = LocalGeary(income,wsp,permutations = 3)
        >>> print(ci.expCi[4])
        [ 1.]
        >>> print(ci.ci[4,3])
        0.186488440026
        >>> print(ci.ppvalue[4,3])
        0.5
    """

    def __init__(self,y,w,permutations=0):
        N = y.n * 1.0
        self.variable = y
        self.w = w.full()
        self.sumw = sum(sum(self.w * 1.0))
        self.expCi = (y.n / self.sumw) * \
                     (reshape((sum(self.w,1)-diag(self.w)),(y.n,1)))
        self.den = self.getDen(y)
        self.num = self.getNum(y)
        self.ci = self.num * self.den
        if permutations:
            count = ones((y.n,y.t),Float)
            expBox = repeat(self.expCi,y.t,1)
            for iter in range(permutations):
                yperm = Variable(permutate(y))
                permNum = self.getNum(yperm)
                count += multiply(greater(permNum,self.num), \
                                  greater(self.ci,expBox))
                count += multiply(less(permNum,self.num), \
                                  less(self.ci,expBox))
            self.ppvalue = count / (permutations + 1)
        #del [self.sumw, self.den, self.num, self.w]
        self.w=w
        
    def getNum(self,y):
        if len(shape(y)) == 1:
            yprime = transpose(reshape(y,(y.n,y.t)))
        else:
            yprime = transpose(y)

        #box is an array of shape (t,n,n) where y values are repeated
        #along the rows n times for each time period 
        box = reshape(yprime,(y.t,y.n,1))
        box = repeat(box, y.n, 2)
    
        #boxprime is an array of shape(t,n,n) where y values are
        #repeated along the columns n times for each time period
        boxprime = repeat(yprime,y.n,0)
        boxprime = reshape(boxprime,(y.t,y.n,y.n))

        #The last line of this method converts the results
        #back into a (n,t) array.
        return transpose(sum(((box - boxprime)**2 * self.w),2))

    def getDen(self,y):
        if len(shape(y)) == 1:
            yt = reshape(y,(y.n,y.t))
        else:
            yt = y
        yd = (yt - mean(yt))**2
        return (y.n*(y.n - 1)/2) / sum(yd) / self.sumw

    def report(self):
        rowNames = self.variable.regionNames
        colNames = self.variable.timeString
        colLabels = ["T0"]
        head = "Local Geary's C"
        head = "%s\nVarible: %s\nWeight Matrix: %s" \
                %(head,self.variable.name,self.w.name)
        
        n1,k1 = shape(self.ci)
        if k1 < 13:
            tab = Table(self.ci,colNames=colNames,
                    rowNames=rowNames,
                    head=head,fmt=[[8,3]]).table
        else:
            tab=""
            cols = range(12,k1,13)
            cols.insert(0,0)
            if cols[-1] !=(k1):
                cols.append(k1)
            ij = [ cols[i:i+2] for i in range(len(cols)-1) ]
            for i,j in ij:
                body = self.ci[:,i:j]
                t = Table(body,head=head,rowNames=rowNames,
                        colNames=colNames[i:j]).table
                tab+="\n"+t


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
    >>> galinfo = map(int,"".join(ws).split())
    >>> wsp = spGalMatrix("wsp",galinfo)
    >>> gg = GlobalG(income,wsp)
    >>> print gg.g[17]
    0.0213230137301
    """
    
    def __init__(self,y,w,permutations=0):
        self.w = w
        w = w.full()
        N = y.n * 1.0
        self.getVariance(y,w)
        self.g = self.getG(y,w)
        ZG = (self.g - self.expG) / pow(self.varG,0.5)
        self.zG = ZG
        self.permutations = permutations
        pg =array(map(pdf.zprob,abs(ZG)))
        self.pG = 2*(1.0-pg)
        self.variable = y

        if permutations:
            gp = [] 
            for iter in range(permutations):
                randy=Variable(permutate(y))
                permg = self.getG(randy,w)
                gp.append(permg)
            gp = array(gp)
            self.gp = gp
            meang = mean(gp)
            stdg = gp.std()
            self.permZ = (self.g - meang)/stdg
            ppermZ = array(map(pdf.zprob,abs(self.permZ)))
            self.ppermZ = 2*(1.0-ppermZ)

            lg = sum(self.g < self.gp)
            gg = sum(self.g > self.gp)
            ex = (min((lg,gg)) + 1.) / (self.permutations+1.)
            self.ppermZ = 2.0 * ex

    def getG(self,y,w):
        #Compute G values using 3 dimensional arrays
        if len(shape(y)) == 1:
            yprime = transpose(reshape(y,(y.n,y.t)))
        else:
            yprime = transpose(y)

        #box is an array of shape (t,n,n) where y values are repeated
        #along the rows n times for each time period 
        box = reshape(yprime,(y.t,y.n,1))
        box = repeat(box, y.n, 2)

        #boxprime is an array of shape(t,n,n) where y values are
        #repeated along the columns n times for each time period
        boxprime = repeat(yprime,y.n,0)
        boxprime = reshape(boxprime,(y.t,y.n,y.n))

        denominator = box * boxprime
        numerator = denominator * w

        #The zero axis is time, so summing along the other axes
        #yields values for each time period
        return sum(sum(numerator,1),1) / sum(sum(denominator,1),1)

    def getVariance(self,y,w):
        N = y.n * 1.0
        sumW = sum(sum(w))
        self.expG = sumW / (N*(N - 1))
        wprime = transpose(w)
        s1 = sum(sum(pow((w + wprime),2)))/2.0
        s2 = sum((sum(w) + sum(wprime))**2)*1.0
        b0 = (N**2 - 3*N + 3) * s1 - N*s2 + 3*(sumW**2)
        b1 = -1.0 * ((N**2 - N)*s1 - 2*N*s2 + 6*(sumW**2))
        b2 = -1.0 * (2*N*s1 - (N+3)*s2 + 6*(sumW**2))
        b3 = 4*(N-1)*s1 - 2*(N+1)*s2 + 8*(sumW**2)
        b4 = s1 - s2 + sumW**2
        sumy = sum(y)
        y2 = y**2
        sumy2 = sum(y2)
        y3 = y2 * y
        sumy3 = sum(y3)
        y4 = y2 * y2
        sumy4 = sum(y4)
        numerator = b0 * (sumy2**2) + b1 * sumy4 + b2 * (sumy**2) * sumy2 + \
                    b3 * sumy * sumy3 + b4 * (sumy**4)
        denominator = ((sumy**2 - sumy2)**2) * N * (N-1) * (N-2) * (N-3)
        self.varG = numerator / denominator - (self.expG**2)

    def report(self):
        varName = self.variable.name

        g = self.g
        zg = self.zG
        pvalueG = self.pG
        head = "Global G"
        head = "%s\nVariable; %s\nWeight Matrix: %s" \
                %(head,varName,self.w.name)
        rowLabels = self.variable.timeString
        colLabels = ["G","z","p-(N)"]
        t = self.variable.t
        g = reshape(self.g,[t,1])
        z = reshape(self.zG,[t,1])
        p = reshape(self.pG,[t,1])
        if self.permutations:
            colLabels.append("p-(P)")
            pp = reshape(self.ppermZ,[t,1])
            res=concatenate((g,z,p,pp),1)
            head = "%s\nPermutations: %d"%(head,self.permutations)
        else:
            res=concatenate((g,z,p),1)
        tab = Table(res, head=head,
                rowNames = rowLabels,
                colNames=colLabels).table
        return(tab)



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
    >>> s.ReadData("data/csiss")
    >>> income = s.getVariable("pcincome")
    >>> galstates = open("data/states48.gal",'r')
    >>> ws = galstates.readlines()
    >>> galstates.close()
    >>> galinfo = map(int,"".join(ws).split())
    >>> wsp = spGalMatrix("wsp",galinfo)
    >>> lg = LocalG(income,wsp)
    >>> print lg.gi[4,15]
    -0.60894240796
    >>> print lg.pgi[43,70]
    0.389521421787
    """
    def __init__(self,y,w,star = 0,permutations=0,matrix='contiguity',
                 distance = 0.0):
        N = y.n * 1.0
        self.w = self.getBinaryW(w.full(),N,star,matrix,distance)
        gi = self.getGi(y,star)

        if permutations:
            mcp =  ones(shape(y),Float)
            for iter in range(permutations):
                randy=Variable(permutate(y))
                permg = self.getGiPerm(randy,star)
                permg = where(greater((permg*gi),0.),abs(permg),0.0)
                add(mcp,greater(permg,abs(gi)),mcp)    
            divide(mcp,(permutations+1.),mcp)
            self.mcp = mcp

        pgi =array([map(pdf.zprob,abs(r)) for r in gi])
        self.pgi = 2.0*(1.0-pgi)
        self.permutations = permutations
        self.star = star
        self.gi = gi
        del [self.denominator,self.numerator,self.sumofw2,self.sumw,
             self.sumwsqrd,self.term1,self.term2,self.xbar]
        if self.star == 0:
            del self.revI
        
    def getGi(self,y,star):
        if len(shape(y)) == 1:
            yprime = transpose(reshape(y,(y.n,y.t)))
        else:
            yprime = transpose(y)
        #boxprime is an array of shape(t,n,n) where y values are
        #repeated along the columns n times for each time period
        boxprime = repeat(yprime,y.n,0)
        boxprime = reshape(boxprime,(y.t,y.n,y.n))

        #These are the weights matrix moments and sums
        sumw = reshape(sum(self.w,1),(y.n,1))
        self.sumw = sumw
        sumwsqrd = sumw**2
        self.sumwsqrd = sumwsqrd
        w2 = self.w * self.w
        sumofw2 = reshape(sum(w2,1),(y.n,1))
        self.sumofw2 = sumofw2

        #The numerator,denominator and intermediate  arrays
        #are (t,n,1) arrays.
        #The last line of this method converts the results
        #back into a (n,t) array.
        if star:
            xbar = reshape((sum((boxprime),2)/(y.n)),(y.t,y.n,1))
            s = reshape((sum((boxprime**2),2)/(y.n)),(y.t,y.n,1))
            s = sqrt(s-xbar**2)
            denominator = s * sqrt((y.n*sumofw2-sumwsqrd)/(y.n-1))
        else:
            xbar = reshape((sum((boxprime*self.revI),2)/(y.n-1)),(y.t,y.n,1))
            s = reshape((sum(((boxprime*self.revI)**2),2)/(y.n-1)),(y.t,y.n,1))
            s = sqrt(s-xbar**2)
            denominator = s * sqrt(((y.n-1)*sumofw2-sumwsqrd)/(y.n-2))
            
        term1 = reshape(sum((boxprime * self.w),2),(y.t,y.n,1))
        term2 = sumw * xbar
        numerator = term1 - term2

        self.term1 = term1
        self.term2 = term2
        self.denominator = denominator
        self.numerator = numerator
        self.sumw = sumw
        self.xbar = xbar
        return transpose(reshape((numerator / denominator),(y.t,y.n)))

    def getGiPerm(self,y,star):
        if len(shape(y)) == 1:
            yprime = transpose(reshape(y,(y.n,y.t)))
        else:
            yprime = transpose(y)
        #boxprime is an array of shape(t,n,n) where y values are
        #repeated along the columns n times for each time period
        boxprime = repeat(yprime,y.n,0)
        boxprime = reshape(boxprime,(y.t,y.n,y.n))

        #The numerator,denominator and intermediate  arrays
        #are (t,n,1) arrays.
        #The last line of this method converts the results
        #back into a (n,t) array.
        if star:
            term1 = reshape(sum((boxprime * self.w),2),(y.t,y.n,1))
            numerator = term1 - self.term2
            return transpose(reshape((numerator / self.denominator),(y.t,y.n)))
        else:
            xbar = reshape((sum((boxprime*self.revI),2)/(y.n-1)),(y.t,y.n,1))
            s = reshape((sum(((boxprime*self.revI)**2),2)/(y.n-1)),(y.t,y.n,1))
            s = sqrt(s-xbar**2)
            denominator = s * sqrt(((y.n-1)*self.sumofw2-self.sumwsqrd)/(y.n-2))
            term1 = reshape(sum((boxprime * self.w),2),(y.t,y.n,1))
            term2 = self.sumw * xbar
            numerator = term1 - term2
            return transpose(reshape((numerator / denominator),(y.t,y.n)))

    def getBinaryW(self,w,N,star,matrix,distance):
        I = eye(N)
        if matrix == "contiguity":
            if star:
                neww = where(greater((w+I),0.0),1.0,0.0)
            else:
                revI = where(equal(I,1),0.0,1.0)
                neww = where(greater((w*revI),0.0),1.0,0.0)
                self.revI = revI            
        elif matrix == "distance":
            if star:
                neww = where(less_equal(w,distance),1.0,0.0)
            else:
                revI = where(equal(I,1),0.0,1.0)
                neww = where(less_equal(w,distance),1.0,0.0)*revI
                self.revI = revI
                print neww[0]
        return neww
    
class TraceTest:
    """Spatial autocorrelation test based on Quah's regional
    conditioning."""
    def __init__(self,variable,w,bins=[],permutations=0,nlag=0):
        self.variable=variable
        n,T = self.variable.shape
        self.w = w
        lag = slag(w,variable)
        regRel = variable/lag
        self.regRel = regRel
        self.lag = lag
        baseRel = variable/mean(variable)
        self.baseRel = baseRel
        rangeT = arange(T)

        if bins:
            self.bins = bins
        else:
            self.quints = [Markov.Quintilizer(baseRel[:,time]).quintiles for time in range(T)]
            self.bins = self.quints
            bins = self.bins

        results=[self.traceValue(variable[:,t],lag[:,t],bins[t]) for t in rangeT]
        self.traces = [i[0] for i in results]
        self.tMats = [i[1] for i in results]
        self.tOrig = results 
        #self.tMats = tmat
        comp = zeros([T,1])
        if permutations:
            TP = []
            permRes = zeros([T,permutations])
            for p in range(permutations):
                variable = permutate(variable)
                wy = slag(w,variable)
                results=[self.traceValue(variable[:,t],wy[:,t],bins[t]) for t in rangeT]
                traces = [i[0] for i in results]
                test = traces < self.traces
                comp += test
                TP.append(traces)
            self.pvalue = comp
            self.TP = array(TP)
            comp = self.TP < self.traces
            self.comp = sum(comp)
            self.pvalue = self.comp*1./permutations
            self.permutations = permutations
        else:
            self.permutations = 0



    def traceValue(self,y,wy,bins):
        baseRel = y/mean(y)
        regRel = y/wy
        regRelClasses = searchsorted(bins,regRel)
        baseRelClasses = searchsorted(bins,baseRel)
        self.regClass = regRelClasses
        self.baseClass = baseRelClasses
        k=len(bins)
        k=max(baseRelClasses)
        T = len(regRelClasses)
        tMat = zeros([k+1,k+1])
        coord = zip(regRelClasses,baseRelClasses)
        for i,j in coord:
            #print k,i,j
            tMat[i,j]+=1
        trace = sum(diag(tMat))
        return (trace,tMat)

    def report(self):
        """Pretty formatting of summary results"""
        head="Trace Test for Spatial Autocorrelation"
        head = "%s\nVariable: %s\nWeight Matrix: %s"%(head,self.variable.name,self.w.name)
        rowLabels = self.variable.timeString
        traces=array(self.traces)
        traces=reshape(traces,[len(traces),1])
        if self.permutations==0:
            colLabels = ["Trace"]
            traces=array(self.traces)
            traces=reshape(traces,[len(traces),1])
            body = traces
        else:
            head = "%s\nPermutations: %d\n"%(head,self.permutations)
            colLabels = ["Trace","pvalue"]
            pvalues = array(self.pvalue)
            pvalues = reshape(pvalues,[len(pvalues),1])
            body = concatenate((traces,pvalues),1)


        tab = Table(body,head=head,
        rowNames = rowLabels,
        colNames = colLabels).table
        return(tab)
        


def transMat(localq,interval=1):
    """Returns a matrix recording the transitions of the local moran
    statsitic for an interval length over a given period."""
    n,t = localq.shape
    trans = zeros([4,4])
    rn = range(n)
    for t1 in range(t-interval):
        t2 = t1 + interval
        a = localq[:,t1] - 1
        b = localq[:,t2] - 1
        first = unique(a)
        for i in first:
            rowmatch = nonzero(a==i)
            c = take(b,rowmatch)
            cunique = unique(c)
            for j in cunique:
                jn = sum(c==j)  
                trans[i,j]+= jn
    return trans

class PolyChar:
    """Calculates Polygon Area and Centroid"""
    def __init__(self,coords):
        n=len(coords)
        xi = range(0,n,2)
        x = [ coords[i] for i in xi]
        y = [ coords[i+1] for i in xi]
        np = len(x)
        nr = range(np-1)
        s = [ x[i]*y[i+1] - x[i+1]*y[i] for i in nr]
        area = abs(sum(s)/2.)
        scx = [ (x[i] + x[i+1]) * (x[i]*y[i+1] - x[i+1]*y[i]) for i in nr]
        scy = [ (y[i] + y[i+1]) * (x[i]*y[i+1] - x[i+1]*y[i]) for i in nr]
        try:
            cx = (1/(6.*area)) * sum(scx)
            cy = (1/(6.*area)) * sum(scy)
        except:
            cx = mean(x)
            cy = mean(y)
        bb = (min(x),min(y),max(x),max(y))
        self.bb = bb
        self.area = area
        self.centroid = (cx,cy)


def _test():
    import doctest, Esda
    return doctest.testmod(Esda)

if __name__ == "__main__":
    _test()


