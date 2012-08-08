"""
Map projections for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Jared Aldstadt aldstadt@users.sourceforge.net
            Serge Rey sjrey@users.sourceforge.net
            Tong Zhang leibi@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:
top module for stars gui. all modules should be imported into this module.
methods can be attached to menu callbacks.

"""

from Tkinter import *
from math import *
import CanvasCoords
import ArcView as av
import Common
options = Common.Options()
def screenSize():
    root = Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return (width, height)

def screenInfo():
    width,height = screenSize()
    aspect = width * 1. / height
    if width > 1280:
        width = 1280
        aspect = width * 1. / height
    return (width, height, aspect)

def viewSize():
    width, height, aspect = screenInfo()
    width = int(width/2.2)
    height = int(height/2.2)
    # square the bounding box
    if width > height:
        width = height
    else:
        height = width
    return (width, height)


def AlbersEqualAreaProj(xRad,yRad,bboxRad):
    """Albers Equal Area projection of long/lat points.

    xRad (float): longitude in radians
    yRad (float): latitude in radians
    bboxRad (list of floats): bounding box coordinates in radians (West,South,East,North)

    Code based on formulas from:
    Eric W. Weisstein. "Albers Equal-Area Conic Projection."
    From MathWorld--A Wolfram Web Resource.
    http://mathworld.wolfram.com/topics/MapProjections.html
    """
    
    West, South, East, North = bboxRad
    centralMeridian = (West+East)/2.
    centralParallel = (South+North)/2.
    standardParallel1 = South + (North-South)*(1./3.)
    standardParallel2 = South + (North-South)*(2./3.)
    try:
        n = 0.5*(sin(standardParallel1)+sin(standardParallel2))
        theta = n*(xRad - centralMeridian)
        C = cos(standardParallel1)**2 + 2.*n*sin(standardParallel1)
        rho = sqrt(C-2.*n*sin(yRad))/n
        rho0 = sqrt(C-2.*n*sin(centralParallel))/n
        x = rho*sin(theta)
        y = rho0 - rho*cos(theta)
    except:
        return (1,1)
    return (x,y)

def MercatorProj(xRad,yRad,bboxRad):
    """Mercator projection of long/lat points.

    xRad (float): longitude in radians
    yRad (float): latitude in radians
    bboxRad (list of floats): bounding box coordinates in radians (West,South,East,North)

    Code based on formulas from:
    Eric W. Weisstein. "Mercator Projection."
    From MathWorld--A Wolfram Web Resource.
    http://mathworld.wolfram.com/topics/MapProjections.html
    """
    
    West, South, East, North = bboxRad
    centralMeridian = (West+East)/2.
    centralParallel = (South+North)/2.
    try:
        x = xRad - centralMeridian
        y = log(tan(yRad)+(1/cos(yRad)))-log(tan(centralParallel)+(1/cos(centralParallel)))
    except:
        return (1,1)
    return (x,y)

def TransverseMercatorProj(xRad,yRad,bboxRad):
    """Transverse Mercator projection of long/lat points.

    xRad (float): longitude in radians
    yRad (float): latitude in radians
    bboxRad (list of floats): bounding box coordinates in radians (West,South,East,North)

    Code based on formulas from:
    Eric W. Weisstein. "Mercator Projection."
    From MathWorld--A Wolfram Web Resource.
    http://mathworld.wolfram.com/topics/MapProjections.html
    """
    West, South, East, North = bboxRad
    centralMeridian = (West+East)/2.
    centralParallel = (South+North)/2.
    try:
        B = cos(yRad)*sin(xRad-centralMeridian)
        x = 0.5*log((1+B)/(1-B))
        y = atan(tan(yRad)/cos(xRad-centralMeridian)) - centralParallel
    except:
        return (1,1)
    return (x,y)

def CylindricalEquidistantProj(xRad,yRad,bboxRad):
    """Cylindrical Equidistant projection of long/lat points.

    xRad (float): longitude in radians
    yRad (float): latitude in radians
    bboxRad (list of floats): bounding box coordinates in radians (West,South,East,North)

    Code based on formulas from:
    Eric W. Weisstein. "Cylindrical Equidistant Projection."
    From MathWorld--A Wolfram Web Resource.
    http://mathworld.wolfram.com/topics/MapProjections.html
    """
    West, South, East, North = bboxRad
    centralMeridian = (West+East)/2.
    centralParallel = (South+North)/2.
    try:
        x = (xRad-centralParallel)*cos(centralParallel) - (centralMeridian-centralParallel)*cos(centralParallel)
        y = yRad - centralParallel
    except:
        return (1,1)
    return (x,y)    

class Map:
    """Basic class to demonstrate how to project coordinates.
    
    Needs to be generalized for:
        - checking coordinate system
        - applying alternative projections.
        
    For now it simply uses mercator and assumes the coords from the shapeFile
    are in lat/lon"""

    def __init__(self,shapeFileName,Projection="None"):
        self.file = shapeFileName
        self.project = av
        self.screenWidth, self.screenHeight = screenSize() 
        project = av.ArcViewProject(self.file)
        shapes = project.shapeFile.shplist
        bbox = project.shapeFile.shpbox
        West, South, East, North = bbox
        self.projectionType = Projection
        poly2shape = {}
        poly2shape = {}
        shape2poly = {}
        if Projection == "None":
            pname = 'Unprojected'
            midX = (West + East) / 2.
            midY = (North + South) / 2.
            xrange = abs(West - East)
            yrange = abs(North - South)
            if xrange < yrange: xrange = yrange

            projected = {}
            shapeCount = 0
            polyCount = 0
            for shape in shapes:
                # check for multiple parts here
                coords = shape[2]
                nparts = shape[1]
                start = [ i for i in nparts]
                end = start[1:]
                end.append(len(coords)) 
                polys = []
                #print 'start,end',start,end
                n = len(coords)
                for partId in range(len(nparts)):
                    partCoords = coords[start[partId]:end[partId]]
                    nCoords = len(partCoords)
                    x = [ partCoords[i][0] - midX for i in range(0,nCoords) ]
                    y = [ partCoords[i][1] - midY for i in range(0,nCoords) ]
                    projected[polyCount] = zip(x,y)
                    polys.append(polyCount)
                    poly2shape[polyCount] = shapeCount
                    polyCount += 1
                shape2poly[shapeCount] = polys
                shapeCount+=1
            self.projected = projected
            self.xrange = xrange
            self.yrange = yrange
            self.bbox=((South,West),(North,East))
            self.poly2shape = poly2shape
            self.shape2poly = shape2poly
            self.shplist = shapes
            
        else:
            print Projection
            #pname = str(Projection).split()[1]
            bboxRad = [radians(i) for i in bbox]
            WestRad, SouthRad, EastRad, NorthRad = bboxRad
            mp = Projection

            bboxSW = mp(WestRad,SouthRad,bboxRad)
            bboxNE = mp(EastRad,NorthRad,bboxRad)

            midX = (bboxSW[0] + bboxNE[0] )/ 2.
            midY = (bboxSW[1] + bboxNE[1] )/ 2.

            xrange = abs(bboxSW[0] - bboxNE[0])
            yrange = abs(bboxSW[1] - bboxNE[1])
            if xrange < yrange: xrange = yrange
            
            projected = {}
            shapeCount = 0
            polyCount = 0
            for shape in shapes:
                coords = shape[2]
                nparts = shape[1]
                start = [ i for i in nparts]
                end = start[1:]
                end.append(len(coords)) 
                polys = []
                #print 'start,end',start,end
                n = len(coords)
                for partId in range(len(nparts)):
                    partCoords = coords[start[partId]:end[partId]]
                    nCoords = len(partCoords)
                    longitude = [ radians(partCoords[i][0]) for i in range(0,nCoords) ]
                    latitude = [ radians(partCoords[i][1]) for i in range(0,nCoords) ]
                    vertices = zip(longitude, latitude)
                    pvertices = [ mp(v[0], v[1], bboxRad) for v in vertices ]
                    projected[polyCount] = pvertices
                    polys.append(polyCount)
                    poly2shape[polyCount] = shapeCount
                    polyCount+=1
                shape2poly[shapeCount] = polys
                shapeCount+=1

            self.projected = projected
            #self.xrange = xrange          
            self.xrange = abs(bboxSW[0] - bboxNE[0])
            self.yrange = abs(bboxSW[1] - bboxNE[1])
            self.bbox = (bboxSW, bboxNE)
            self.poly2shape = poly2shape
            self.shape2poly = shape2poly

        self.projectionName = self.projectionType

class MapView:
        """Simple wrapper to display map"""
        def __init__(self,master,map,buffer=1.0):
            self.master = master
            self.map = map
            self.buffer = buffer

        def plot(self,width=None, height=None):
            if not width:
                width, height = viewSize()
            width = width - 2 * options.OUTERBOXPLOTS[1]
            height = width
            map = self.map
            c = Canvas(self.master,width=width,height=height)
            c.pack()
            C = CanvasCoords.CanvasCoords()
            xrange = map.xrange * self.buffer
            yrange = map.yrange * self.buffer
            viewRange = max(yrange,xrange)
            C.set_coordinate_system(width,height,width/2,height/2,viewRange)
            p2c2 = C.physical2canvas2
            screenCoords = {}
            for key in map.projected.keys():
                polygon = map.projected[key]
                pnts = [ p2c2(point) for point in polygon]
                if key % 2:
                    fill='yellow'
                else:
                    fill='blue'

                c.create_polygon(pnts,fill=fill,outline='black')
                screenCoords[key] = pnts
            self.canvas = c
            self.screenCoords = screenCoords
            self.screenHeight=self.map.screenHeight
            self.screenWidth=self.map.screenWidth

    





if __name__ == '__main__':

    
    fname = raw_input("Enter the shape file name (include .shp): ") 
    #fname = 'data/nat.shp'
    #fname = 'california.shp'
    #fname = 'data/us48.shp'
    root = Tk()
    map = Map(fname,Projection=MercatorProj)
    root.title('Mercator')
    v=MapView(root,map)
    v.plot()


   
    #for proj in [ MercatorProj, AlbersEqualAreaProj, TransverseMercatorProj,
    #    CylindricalEquidistantProj]:
    #        top = Toplevel(root)
    #        map = Map(fname, Projection=proj)
    #        v=MapView(top, map)
    #        top.title(map.projectionName)
    #        v.plot()

    #root.mainloop()
