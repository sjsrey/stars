"""
Gis module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

This module contains GIS functions for STARS.


"""

import math
    

class Polygon:
    """

    Attributes:
        coords: list of x,y coordinates in closed geographic form
        n: (int) number of vertices
        centroid: (tuple) of x,y coordinates for polygon centroid
        bb: (tuple) of x0,y0,x1,y1 bounding box coordinates for polygon
        area: (float) area of polygon

    Methods:
        getArea: returns of polygon area (float).
        getBB: returns tuple of (x0,y0,x1,y1) coordinates for polygon bounding
            box
        getCentroid: returns tuple of x,y coordinates for centroid
        getCoordinates: returns coordinates (tuple) of x,y coordinates in
            closed geographic form).
        getN: returns n (int) number of vertices
    """


    def __init__(self,coordinates):
        """
        coordinates: list of x,y coordinates in closed geographic form.
        """

        self.setCoordinates(coordinates)
        self.setN()
        self.__setAreaCentroids()

    def __setAreaCentroids(self):
        coords = self.getCoordinates()
        n = self.getN()
        xi = range(0,n,2)
        x = [ coords[i] for i in xi]
        y = [ coords[i+1] for i in xi]
        np = len(x)
        nr = range(np-1)
        s = [ x[i]*y[i+1] - x[i+1]*y[i] for i in nr]
        area = abs(sum(s)/2.)
        scx = [ (x[i] + x[i+1]) * (x[i]*y[i+1] - x[i+1]*y[i]) for i in nr]
        scy = [ (y[i] + y[i+1]) * (x[i]*y[i+1] - x[i+1]*y[i]) for i in nr]
        cx = (1/(6.*area)) * sum(scx)
        cy = (1/(6.*area)) * sum(scy)
        bb = (min(x),min(y),max(x),max(y))
        self.__bb = bb
        self.__area = area
        self.__centroid = (cx,cy)


    def setCoordinates(self,coordinates):
        x0,y0 = coordinates[0:2]
        x1,y1 = coordinates[-2:]
        if (x0==x1 and y0==y1):
            self.__coordinates = coordinates
        else:
            print """Warning: cooridantes forced to closed geographic form."""
            coordinates.extend([x0,y0])
            self.__coordinates = coordinates

    def setN(self):
        self.__n = len(self.getCoordinates())

    def getCentroid(self):
        return self.__centroid

    def getArea(self):
        return self.__area

    def getBB(self):
        return self.__bb

    def getN(self):
        return self.__n

    def getCoordinates(self):
        return self.__coordinates



def nearestNeighbor(pointA,points,full=0):
    """
    find nearestNeighbor to pointA in points.

    pointA: tuple of x,y coordinate for a point
    points: tupe of tuple of x,y coordinates

    returns tuple of index of nearest neighbor and distance if full is
        true, otherwise returns the integer id of nearestNeighbor

    """
    dists = [ distance(pointA,b) for b in points ]
    minD = min(dists)
    i = dists.index(minD)
    if full:
        return (i,minD)
    return i


def distance(pointA,pointB):
    x0,y0 = pointA
    x1,y1 = pointB
    xd = x0 - x1
    yd = y0 - y1
    return math.sqrt(xd*xd + yd*yd)


if __name__ == '__main__':

    c = [ 1,1, 2,1, 2,2, 1,2, 1,1 ]
    p = Polygon(c)
    a = c[0:2]
    points = [ c[i:i+2] for i in range(1,len(c)-3) ]


