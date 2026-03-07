#!/usr/bin/python

"""
spatial weights module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

This module implements spatial weights classes for STARS.

XXX PySAL

"""

import time
import numpy as np
from numpy.linalg import inv
from shapereader import *

import Gis  # for centroids on disconnected island polygons

# delta to get buckets right
DELTA = 0.000001
# constants for weights types
WT_UNKNOWN = 0
WT_ROOK = 1
WT_QUEEN = 2
# constants for bucket sizes
BUCK_SM = 8
BUCK_LG = 20
SHP_SMALL = 1000
# constant for spatial weights size
WT_SMALL = 1000


class spweight:
    """
    spweight data structure: list of lists
    [ metadata ], [key:obs dictionary] [obs:key dictionary]
    [number of neighbors] [neighbor id lists ] [neighbor weights lists]
    [characteristics ] [traces ] [eigvalues]
    need a dbf reader to use a "key" variable instead of sequence number
    sequence number is fine as long as "pure" shape files since the matching order
    is part of the ESRI shape file format
    when called without filename, initialize only, useful for grid cases
    """

    def __init__(self, filename="", wtType=WT_ROOK):
        # initialization here: check input file type and
        # call appropriate reader
        self.meta = []
        self.keyobs = {}
        self.obskey = {}
        self.numneigh = []       # number of neighbors
        self.neighbors = []      # neighbor ids
        self.weights = []
        self.characteristics = []
        self.traces = []
        self.eigvalues = []
        if filename:
            # only shape input implemented so far
            self.shp2wt(filename, wtType)
        else:   # must create shapefile from scratch grid only
            pass
        self.numneighbrs()    # computes the number of neighbors

    # constructors

    # read gal file and convert to wt data structure
    def wtfromgal(self):
        pass

    # read gwt file and convert to wt data structure
    def wtfromgwt(self):
        pass

    # read shp file and construct rook or queen contiguity
    def shp2wt(self, filename, wtType):
        raw_shape = shapefile(filename)
        if raw_shape.shptype == SHP_POINT:
            return       # need handler
        shapepoints = raw_shape.shplist    # list of lists
        shapebox = raw_shape.shpbox      # bounding box
        self.shapepoints = shapepoints

        numPoly = len(shapepoints)
        # bucket size
        if (numPoly < SHP_SMALL):
            bucketMin = numPoly // BUCK_SM + 2
        else:
            bucketMin = numPoly // BUCK_LG + 2
        # bucket length
        lengthX = ((shapebox[2] + DELTA) - shapebox[0]) / bucketMin
        lengthY = ((shapebox[3] + DELTA) - shapebox[1]) / bucketMin

        # initialize buckets
        bucketX = [[] for i in range(bucketMin)]
        bucketY = [[] for i in range(bucketMin)]
        polyXbucket = [[] for i in range(numPoly)]  # list with buckets for X
        polyYbucket = [[] for i in range(numPoly)]  # list with buckets for Y
        self.neighbors = [[] for i in range(numPoly)]      # list of lists for neighbors

        minbox = shapebox[:2] * 2  # minX,minY,minX,minY
        blen = [lengthX, lengthY] * 2  # lenx,leny,lenx,leny

        for i in range(numPoly):
            pb = [int((shapepoints[i][0][j] - minbox[j]) / blen[j]) for j in range(4)]
            for j in range(pb[0], pb[2] + 1):
                polyXbucket[i].append(j)
                bucketX[j].append(i)
            for j in range(pb[1], pb[3] + 1):
                polyYbucket[i].append(j)
                bucketY[j].append(i)

        # create candidate neighbors from buckets
        for i in range(numPoly):
            buckX = []
            for j in range(0, len(polyXbucket[i])):
                buckX += bucketX[polyXbucket[i][j]]
            buckY = []
            for j in range(0, len(polyYbucket[i])):
                buckY += bucketY[polyYbucket[i][j]]
            buckX = list(dict([(j, j) for j in buckX]).keys())
            buckY = list(dict([(j, j) for j in buckY]).keys())
            buckX.sort()
            buckY.sort()

            nb = []
            if len(buckX) < len(buckY):
                k = buckX.index(i) + 1
                nb = [buckX[jj] for jj in range(k, len(buckX))
                      if (buckX[jj] in buckY) and (shapepoints[i][0].bbcommon(shapepoints[buckX[jj]][0]))]
            else:
                k = buckY.index(i) + 1
                nb = [buckY[jj] for jj in range(k, len(buckY)) if (buckY[jj] in buckX)
                      and (shapepoints[i][0].bbcommon(shapepoints[buckY[jj]][0]))]
            for ii in range(0, len(nb)):
                ch = 0
                jj = 0
                kk = len(shapepoints[i][2]) - 1
                nbi = nb[ii]

                while not ch and jj < kk:
                    if wtType == WT_ROOK:
                        ch = (shapepoints[i][2][jj] in shapepoints[nbi][2]) and (shapepoints[i][2][jj + 1] in shapepoints[nbi][2])
                    else:   # queen
                        ch = shapepoints[i][2][jj] in shapepoints[nbi][2]
                    jj += 1
                if ch:
                    self.neighbors[i].append(nbi)
                    self.neighbors[nbi].append(i)

    # construct rook for grid
    def grid2rk(self, nrows, ncols):
        m = nrows * ncols
        self.neighbors = [[] for i in range(m)]  # initialize
        for i in range(nrows):
            for j in range(ncols):
                k = i * ncols + j
                # to left
                if j:
                    self.neighbors[k].append(k - 1)
                # to right
                if j < ncols - 1:
                    self.neighbors[k].append(k + 1)
                # above
                if i:
                    self.neighbors[k].append(k - ncols)
                # below
                if i < nrows - 1:
                    self.neighbors[k].append(k + ncols)
                self.neighbors[k].sort()
        self.numneighbrs()

    # construct rook - torus for grid
    def grid2rktor(self, nrows, ncols):
        m = nrows * ncols
        self.neighbors = [[] for i in range(m)]  # initialize
        for i in range(nrows):
            for j in range(ncols):
                k = i * ncols + j
                # to left
                if j:
                    self.neighbors[k].append(k - 1)
                else:
                    self.neighbors[k].append(k + ncols - 1)
                # to right
                if j < ncols - 1:
                    self.neighbors[k].append(k + 1)
                else:
                    self.neighbors[k].append(k - ncols + 1)
                # above
                if i:
                    self.neighbors[k].append(k - ncols)
                else:
                    self.neighbors[k].append((nrows - 1) * ncols + j)
                # below
                if i < nrows - 1:
                    self.neighbors[k].append(k + ncols)
                else:
                    self.neighbors[k].append(j)
                self.neighbors[k].sort()
        self.numneighbrs()

    # read/write methods

    def readwt(self):
        pass

    def wt2gal(self):
        pass

    def wt2gwt(self):
        pass

    def wt2pickle(self):
        pass

    # conversion from wt data structure to numpy weight matrix
    # gal form only so far
    def wt2mat(self):
        n = len(self.neighbors)
        w = np.zeros((n, n))
        for i in range(n):
            if self.numneigh[i]:
                kk = 1.0 / self.numneigh[i]
                for j in self.neighbors[i]:
                    w[i][j] = kk
        return w

    def mat2gal(self):
        pass

    def mat2gwt(self):
        pass

    # weights computations

    def numneighbrs(self):
        self.numneigh = []   # always reinitialize
        for i in range(len(self.neighbors)):
            self.numneigh.append(len(self.neighbors[i]))

    def wtchars(self):
        pass

    def wttraces(self):
        pass

    def wt2higher(self):
        pass

    def wteigen(self):
        pass

    def histogram(self):
        maxn = max(self.numneigh)
        counts = [self.numneigh.count(i) for i in range(maxn + 1)]
        return counts

    def islands(self):
        """returns ids of any island observations."""
        ij = zip(range(len(self.numneigh)), self.numneigh)
        return [i for i, j in ij if j == 0]

    def findNearestNeighbors(self, ids):
        """find nearest neighbors based on bounding box centroid distances.

        ids: list of shape ids to find neighbors for.
        """
        # bb centroids
        cent = [((s[0][0] + s[0][2]) / 2., (s[0][1] + s[0][3]) / 2.) for s in
                self.shapepoints]
        self.centroids = cent
        c = cent
        neighbors = []
        rn = range(len(self.shapepoints))
        for id in ids:
            x0, y0 = cent[id]
            di = [(x0 - c[j][0]) * (x0 - c[j][0]) + (y0 - c[j][1]) * (y0 - c[j][1])
                  for j in rn]
            maxd = max(di)
            di[id] = maxd
            nid = di.index(min(di))
            neighbors.append(nid)
        return neighbors

    def findIslandNeighbors(self):
        islands = self.islands()
        return zip(islands, self.findNearestNeighbors(islands))

    def fixIslands(self):
        """attaches island shapes to nearest neighbor and reconstructs gal
        information accordingly"""

        islandInfo = self.findIslandNeighbors()
        addedJoins = []
        if islandInfo:
            for i, j in islandInfo:
                ineigh = self.neighbors[i]
                jneigh = self.neighbors[j]
                if j not in ineigh:
                    ineigh.append(j)
                    ineigh.sort()
                    self.numneigh[i] = len(ineigh)
                    self.neighbors[i] = ineigh
                    addedJoins.append((i, j))
                if i not in jneigh:
                    jneigh.append(i)
                    jneigh.sort()
                    self.numneigh[j] = len(jneigh)
                    self.neighbors[j] = jneigh
                    addedJoins.append((j, i))
        self.islandInfo = islandInfo
        self.addedJoins = addedJoins

    # spatial lag for single variable
    # checks what is passed and initializes same
    # assumes gal form only so far
    def splag(self, x):
        n = len(x)
        if type(x) == list:
            wx = [0 for i in range(n)]
        elif isinstance(x, np.ndarray):
            wx = np.zeros(n)
        for i in range(n):
            if self.numneigh[i]:
                for j in self.neighbors[i]:
                    wx[i] += x[j]
                wx[i] /= self.numneigh[i]
        return wx

    # spatial AR transformation
    # force = 0 default let size determine
    # force = 1 always iterative
    # precis = DELTA precision criterion same as for buckets
    # precis set precision criterion
    def sartran(self, rho, x, force=0, precis=DELTA):
        n = len(x)
        listflag = 0
        if type(x) == list:
            x = np.array(x, dtype=float)
            listflag = 1
        sarx = np.zeros(n)
        if n > WT_SMALL or force:
            sarx = x
            wx = self.splag(x) * rho
            sarx += wx
            while max(wx) > precis:
                wx = self.splag(wx) * rho
                sarx += wx
        else:   # small weights full matrix inverse
            w = self.wt2mat()
            w *= -rho
            w += np.eye(n)
            wx = inv(w)
            sarx = wx @ x
        if listflag:
            return sarx.tolist()
        else:
            return sarx


if __name__ == "__main__":
    fname = input("Enter the shape file name (include .shp): ")
    t0 = time.time()
    w1 = spweight(fname, 1)
    t1 = time.time()
    print("-------------------------------------")
    print("using " + str(fname))
    print("time elapsed for rook: " + str(t1 - t0))
