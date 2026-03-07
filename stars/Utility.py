"""  Utility.py
Utility module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

This module implements various handy utilities for STARS.


"""
"""Utility functions for STARS"""
import numpy as np

def unique(y):
    """returns the unique values of an array."""
    uvals=[]
    for i in y:
        if i not in uvals:
            uvals.append(i)
    return(np.array(uvals))

def meandev(y):
    """Returns variable expressed in deviations from its mean."""
    dimy = y.shape
    meany = np.mean(y, axis=0)
    if len(dimy) > 1:
        n,t = dimy
        dev = y - np.diag(meany) @ np.ones([t,n])
        dev = dev.T
    else:
        dev = y - meany
    return dev

def permutate(y):
    """Returns a matrix (vector)  with rows (elements) permutated"""
    dimy = y.shape if hasattr(y, 'shape') else (len(y),)
    n = dimy[0]
    pid = np.random.permutation(n)
    yp = np.take(y, pid, axis=0)
    return yp

def slag(w,variable):
    """Sparse Spatial Lag"""
    n,k = variable.shape
    lag = np.zeros((n,k))
    for i in w.dict.keys():
        nn,ids = w.dict[i]
        den = 1./nn
        values = np.array(np.sum(np.take(variable,ids,axis=0), axis=0) * den)
        lag[i,:] = values
    return lag

def format(fmt,value):
    size = fmt[0]
    decimal = fmt[1]
    sv = str(value)
    com = "\"%"+str(size)+"."+str(decimal)+"f\"%("+sv+")"
    sv = eval(com)
    return sv

def TransposeList(m):
    """
    Transpose a list of lists: Author: gerhard@bigfoot.de
    """
    n = len(m)
    return [[m[j][i] for i in range(len(m[0])) for j in range(n)][k*n:k*n+n] for k in range(len(m[0]))]

def splitList(l):
    """Takes a list of values and makes each its own list within a list for
    csv writing.
    l = (list) = list of values
    """
    listOfLists = []
    [ listOfLists.append( [i] ) for i in l ]
    return listOfLists

def joinListValues(var1,var2,delim=""):
    """combines two character variables to make a new variable.
    use to identify unique records in a dbf - for example combining county
    fips with state fips into countystatefips"""
    try:
        v1=[ str(i) for i in var1 ]
        v2=[ str(i) for i in var2 ]
        vnew = [ a+delim+b for a,b in zip(v1,v2)]
        return vnew
    except:
        return 0

def applyDataTypes(listOfTypes,listOfValues):
    columns = range(len(listOfTypes))
    listOfValues = [ i.strip("\'") for i in listOfValues ]
    listOfValues = [ i.strip("\"") for i in listOfValues ]
    return [ eval(listOfTypes[i])(listOfValues[i]) for i in columns ]

def findDataTypes(listOfValues):
    dataTypes = []
    for i in listOfValues:
        try:
            dType = float(i)
            dataTypes.append('float')
        except:
            dataTypes.append('str')
    return dataTypes
