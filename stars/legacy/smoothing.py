
"""
Smoothing module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

Modification of SAL_Smoother.py by sjr.

This module implements smoothing techniques for STARS.


"""

def SrSmoother( weights, eventValue, baseValue):
    rn = range(len(eventValue))
    rateValues = [ SrRateCalc(weights, eventValue, baseValue,i) for i in rn]
    return rateValues

def SrRateCalc( weights, eventValue, baseValue, i):
    eValue = eventValue[i]
    bValue = baseValue[i]
    idValues =  weights.neighbors[i] #no longer 1 offset, assumes 0 offset
    eSum = sum( [ eventValue[id] for id in idValues] )
    bSum = sum( [ baseValue[id] for id in idValues] )
    rValue = (eValue + eSum) / (bValue + bSum)
    return rValue

def EbSmoother( eventValue, baseValue):
    eSum = sum(eventValue)
    bSum = sum(baseValue)
    mean = eSum / bSum
    rn = range(len(eventValue))
    b=baseValue
    e=eventValue
    v=sum([ (b[i] * ((e[i]/b[i]) - mean) * (e[i]/b[i] - mean))
           for i in rn] )
    variance = (v/bSum) - (mean / (bSum / len(e)))
    wi = [ variance / (variance + ( mean/baseValue[i])) for i in rn]
    u = [wi[i]*(eventValue[i]/baseValue[i]) + (1-wi[i])*mean for i in rn]
    return u 

def ErSmoother( eventValue, baseValue):
    rn = range(len(eventValue))
    eSum = sum(eventValue)
    bSum = sum(baseValue)
    mean = eSum/bSum
    r = [ eventValue[i]/baseValue[i] * mean for i in rn ]
    return r
