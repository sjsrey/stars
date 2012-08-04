"""
GAL module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

Geographic Algorithm Library utilities for STARS
"""

import sets
def ReadGisFile(fileName):
    gis = open(fileName,'r')
    gisdata = gis.readlines()
    gis.close()
    nl = len(gisdata)
    row = 0
    cpolyDict = {}
    polyDict = {}
    pId = 0
    pcsDict = {}
    while row < nl:
        info = gisdata[row]
        info = info.split()
        info = [int(x) for x in info]
        csId = info[0]
        polyId = info[1]
        ncoord = info[2]
        pcsDict[pId] = [csId]
        r1 = row + 1
        r2 = row + ncoord + 1
        polyDict[pId] = [ float(coord.strip()) \
                               for coord in gisdata[r1:r2]]
        if cpolyDict.has_key(csId):
            cpolyDict[csId].append(pId)
        else:
            cpolyDict[csId] = [pId]
        pId = pId + 1
        row = row + ncoord + 1

    cs2poly = cpolyDict
    poly2cs=pcsDict
    coords=polyDict
    coordPolyList = [coords, poly2cs, cs2poly]
    return coordPolyList


def gis2Contiguity(coords,poly2cs,cs2poly):
    vert2cs = {} 
    polykeys = coords.keys()
    csids = cs2poly.keys()
    for poly in polykeys:
        vertices = coords[poly]
        n = len(vertices)
        r = range(0,n,2)

        pnts = [ (vertices[i],vertices[i+1])  for i in r]
        csid = poly2cs[poly][0]
        for pnt in pnts:
            if vert2cs.has_key(pnt):
                if csid not in vert2cs[pnt]:
                    vert2cs[pnt].append(csid)
            else:
                vert2cs[pnt] = [csid]
    galinfo = {}
    pnts = vert2cs.keys()
    for pnt in pnts:
        ids = vert2cs[pnt]
        nids = len(ids)
        rn = range(nids)
        if nids > 1:
            for i in rn[0:-1]:
                for j in rn[i:nids]:
                    idi = ids[i]
                    idj = ids[j]
                    if idi != idj:
                        if galinfo.has_key(idi):
                            if idj not in galinfo[idi]:
                                galinfo[idi].append(idj)
                        else:
                            galinfo[idi]=[idj]
    
                        if galinfo.has_key(idj):
                            if idi not in galinfo[idj]:
                                galinfo[idj].append(idi)
                        else:
                            galinfo[idj]=[idi]
            
    keys = galinfo.keys()
    island = [ csid  for csid in csids if csid not in keys]
    if island:
        print "unconnected observation(s): ",island
        for obs in island:
            galinfo[obs] = ()
    else:
        print "all observations connected"
    items = galinfo.items()
    g2 = dict( [(item[0],(len(item[1]),item[1])) for item in items  ] )
    return g2




def aggregateGal(gal,bridge):
    """
    aggregates a gal dictionary according to the bridging scheme in bridge.

    Example Usage:
    >>> from Gal import *
    >>> gal={}
    >>> gal[0]=[1,[1]]
    >>> gal[1]=[2,[0,2]]
    >>> gal[2]=[2,[1,3]]
    >>> gal[3]=[2,[2,4]]
    >>> gal[4]=[1,[3]]
    >>> bridge={}
    >>> bridge[0]=[0]
    >>> bridge[1]=[1]
    >>> bridge[2]=[2,4]
    >>> bridge[3]=[3]
    >>> res=aggregateGal(gal,bridge)
    >>> newGal=aggregateGal(gal,bridge)
    >>> gal
    {0: [1, [1]], 1: [2, [0, 2]], 2: [2, [1, 3]], 3: [2, [2, 4]], 4: [1, [3]]}
    >>> newGal
    {0: [1, [1]], 1: [2, [0, 2]], 2: [2, [1, 3]], 3: [1, [2]]}
    >>> bridge = {}                    
    >>> bridge[0]=[0,1,4]
    >>> bridge[1]=[2,3]
    >>> newGal2=aggregateGal(gal,bridge)
    >>> newGal2
    {0: [1, [1]], 1: [1, [0]]}
    """
    bkeys = bridge.keys()
    gkeys = gal.keys()
    ir = zip(range(len(bkeys)),bkeys)
    ig = zip(range(len(gkeys)),gkeys)
    new2old = bridge 
    old2new = {}

    for bkey in bkeys:
        ids = bridge[bkey]
        for id in ids:
            old2new[id] = bkey

    rn = range(len(bkeys))
    rn1 = rn[:-1]
    newGal = {}
    for key in bkeys:
        newGal[key] = [0,sets.Set()]
    for i in rn1:
        okey = bkeys[i]
        oset = sets.Set()
        okeys = bridge[okey]
        temp = []
        oset = [ temp.extend(gal[gid][1]) for gid in okeys ]
        oset = sets.Set(temp)
        for j in rn[i+1:]:
            dkey = bkeys[j]
            dset = sets.Set()
            dkeys = bridge[dkey]
            join = oset.intersection(dkeys)
            if join:
                a=newGal[okey][1].union([dkey])
                b=newGal[dkey][1].union([okey])
                newGal[okey][1]=a
                newGal[dkey][1]=b
    for key in newGal.keys():
        newGal[key][0] = len(newGal[key][1])
        newGal[key][1] = list(newGal[key][1])


    return newGal

def _test():
    import doctest, Gal
    return doctest.testmod(Gal)



if __name__ == '__main__':
    _test()


    from Gal import *
    gal={}
    gal[0]=[1,[1]]
    gal[1]=[2,[0,2]]
    gal[2]=[2,[1,3]]
    gal[3]=[2,[2,4]]
    gal[4]=[1,[3]]
    bridge={}
    bridge[0]=[0]
    bridge[1]=[1]
    bridge[2]=[2,4]
    bridge[3]=[3]
    res=aggregateGal(gal,bridge)
    newGal=aggregateGal(gal,bridge)

