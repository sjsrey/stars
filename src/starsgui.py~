## Automatically adapted for numpy.oldnumeric Jul 20, 2011 by ipython

"""
gui start file for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Serge Rey sjrey@users.sourceforge.net
            Mark V. Janikas janikas@users.sourceforge.net
            Boris Dev borisdev@users.sourceforge.net
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
import sys, os, string
from Tkinter import *                        # widget classes
from guimixin import *        # mix-in methods
from guimaker import *        # frame, plus menu/toolbar builder
from numpy import *
import pickle
import os.path
import version
import time

VERSION = version.VERSION
VERSIONDATE = version.DATE
from stars import *

import Esda
import Markov
import Inequality
import Mobility
import Data
import Markov
import eda
from Table import Table as RTable
from History import *
from SDialog import *
from pdf import *
import help
import DataViewer as DV
from kmean import Kmeans
import sdialogue as sd
import Utility
import STARSsmoothing as smooth

STARSHOME=options.getSTARSHOME()
PLATFORM=options.getPLATFORM()
ssTop = Tk()
ssTop.title("Welcome to STARS!")

ss=SplashScreen(master=ssTop)
# view modules
from gView import *

class SProject(Project):
    """Subclass to compose STARS project inside a GUI
   """
    def __init__(self,name,master,app):
        """Constructor

        name (string): name of project
        master (Tk): application top level window
        app (App): App instance
        """
        Project.__init__(self,name)
        self.master = master
        self.app = app
        self.fnt=("Times",10)
        self.screenHeight = self.app.winfo_screenheight()
        self.screenWidth = self.app.winfo_screenwidth()
        if self.screenWidth > 1280:
            self.screenWidth = 1280 # prevent spread across 2-extended displays
        s = str(self.screenWidth) + " " + str(self.screenHeight)
        self.screenDim = s


    def setInteractionVariable(self,mode):
        """Sets interaction mode

        mode (string): type of interaction to toggle
        """
        if hasattr(self,"viewController"):
            self.InteractionVar.set(mode)
        else:
            self.createViewController()
            self.InteractionVar.set(mode)

    def setMapLegend(self,mode):
        """Turn map legend on or off
        """
        if hasattr(self,"viewController"):
            self.mapLegendVar.set(mode)
        else:
            self.createViewController()
            self.mapLegendVar.set(mode)


    def createViewController(self):
        """Handler to create ViewController"""
        width = 141
        height = 300 
        left = self.screenWidth - width
        top = self.screenHeight - height
        viewController=Toplevel(self.master,width=width,height=height)
        viewController.geometry("141x300-10-15")
        self.InteractionVar = IntVar()
        fnt = (options.VIEWFONT, options.TITLEFONTSIZE)
        #if PLATFORM=='darwin':
        #    fnt = ("Times",12)
        #else:
        #    fnt = ("Times",10)
        self.rButtonIo=Radiobutton(viewController, text="Interaction Off", 
                variable=self.InteractionVar,font=fnt,
                justify=LEFT,
                wraplength=300,width=300,
                value=0,command=self.interactionOff).pack(anchor=W)
        self.rButtonIl=Radiobutton(viewController, text="Linking",
                    variable=self.InteractionVar,font=fnt,
                    value=1,command=self.interactionLinking).pack(anchor=W)
        self.rButtonIb=Radiobutton(viewController, text="Brushing", 
                    variable=self.InteractionVar,font=fnt,
                    value=2,command=self.interactionBrushing).pack(anchor=W)
        self.InteractionVar.set(0)
        self.mapLegendVar = IntVar()
        Radiobutton(viewController, text="Map Legends Off",
                variable=self.mapLegendVar,font=fnt,
                wraplength=300,width=300,
                value=0,command=self.mapLegendsOff).pack(anchor=W)
        Radiobutton(viewController, text="Map Legends Left",
                    variable=self.mapLegendVar,font=fnt,
                    wraplength=300,width=300,
                    value=1,command=self.mapLegendsLeft).pack(anchor=W)
        Radiobutton(viewController, text="Map Legends Right", 
                    variable=self.mapLegendVar,font=fnt,
                    value=2,command=self.mapLegendsRight,
                    wraplength=300,width=300).pack(anchor=W)
        self.vlvar = IntVar()
        Radiobutton(viewController, text="View List",
                    font = fnt,variable=self.vlvar,
                    value = 1,
                    command = self.listViews).pack(anchor=W)
        self.vlvar.set(0)
        self.iconvar = IntVar()
        Radiobutton(viewController, text="Iconify Views",
                    font = fnt,
                    variable = self.iconvar,
                    value = 0,
                    command = self.iconify).pack(anchor=W)
        Radiobutton(viewController, text="Raise Views",
                    font = fnt,
                    variable = self.iconvar,
                    value = 1,
                    command = self.raiseAll).pack(anchor=W)
        self.iconvar.set(1)
        self.appWindowVar = IntVar()
        Radiobutton(viewController, text="STARS Window",
                    font = fnt,
                    variable = self.appWindowVar,
                    value = 1,
                    command = self.appWindow).pack(anchor=W)
        self.appWindowVar.set(1)
        viewController.protocol("WM_DELETE_WINDOW",self.cleanup)
        self.viewController = viewController
        self.mapLegendVar.set(2)
        self.viewController.title("STARS: View Controller")

    def interactionOff(self):
        self.app.interactionOff()
    def interactionLinking(self):
        self.app.interactionLinking()
    def interactionBrushing(self):
        self.app.interactionBrushing()
    def mapLegendsOff(self):
        self.app.mapLegendsOff()
    def mapLegendsLeft(self):
        self.app.mapLegendsLeft()
    def mapLegendsRight(self):
        self.app.mapLegendsRight()
    def cleanup(self):
        self.closeController()
    def listViews(self):
        self.app.listViews()
        self.vlvar.set(0)
    def iconify(self):
        self.app.iconify()
    def raiseAll(self):
        self.app.raiseAll()
    def appWindow(self):
        self.app.master.tkraise()
        self.app.master.focus_set()
    
    def closeController(self):
        if hasattr(self,"viewController"):
            self.viewController.destroy()

    def setV(self):
        sc = Screen(self.app)
        self.vheight = int(sc.screenHeight/2.2)
        self.vwidth =  int(sc.screenWidth/2.2)

    def reScaleCoords(self):
        self.options["graphics"]["screen"]="xxxxx"
        self.scaleCoords()

    def scaleCoords1(self):
        pass
    def scaleCoords(self):
        self.setV()
        gisDim = self.options["graphics"]["screen"]
        #print gisDim,self.screenDim
        #if gisDim != [self.screenDim]:
        #gisDim  = "100000" # serge kludge for presentation
        #print gisDim, self.screenDim
        if gisDim != [self.screenDim]:
            print 'scaling coordinates, please wait'
            self.y1 = self.vheight * options.OUTERBOXPLOTS[0]
            self.y0 = self.vheight * options.OUTERBOXPLOTS[1]
            self.x1 = self.vwidth * options.OUTERBOXPLOTS[0]
            self.x0 = self.vwidth * options.OUTERBOXPLOTS[1]

            keys = self.coords.keys()
            allXs = []
            allYs = []

            for key in keys:
                coord = self.coords[key]
                xs = [coord[x] for x in range(0,len(coord),2)]
                ys = [coord[x] for x in range(1,len(coord),2)]
                allXs.extend(xs)
                allYs.extend(ys)

            maxx = max(allXs)
            minx = min(allXs)
            maxy = max(allYs)
            miny = min(allYs)
            width = maxx - minx
            height = maxy - miny
            adjY = adjX = 0

            if width > height:
                adjY = (width - height) / 2.
                size = width
            else:
                adjX = (height - width) / 2.
                size = height
            
            # center map in square canvas bb
            # new max dimension = old min dimension
            adjCanX = adjCanY = 0
            canH = self.y1 - self.y0
            canW = self.x1 - self.x0
            canX0 = self.x0
            canY0 = self.y0
            if canH > canW:
                canSize = canW
                Dy = (canH - canW)/2.
                canY0 = canY0 + Dy
            else:
                canSize = canH
                Dx = (canW - canH)/2.
                canX0 = canX0 + Dx

            #raw_input('wait')
            self.xMidPoint = canSize/2.
            scale = canSize/size
            self.newcoords = {}

            for key in keys:
                coord = self.coords[key]
                xs = [canX0 + (coord[x] - minx + adjX)*scale for x in range(0,len(coord),2)]
                ys = [canY0 + (coord[x] - miny + adjY)*scale for x in range(1,len(coord),2)]
                nc = range(len(xs))
                newcoords=[]
                for i in nc:
                    newcoords.append(xs[i])
                    newcoords.append(ys[i])
                self.newcoords[key] = newcoords
            self.calcCentroids()
            self.scaledCoords = self.newcoords
            self.oldCoords = self.coords
            self.coords = self.newcoords
            self.options["graphics"]["screen"] = [self.screenDim]
        else:
            self.newcoords = self.coords
            self.oldCoords = self.coords



    def calcCentroids(self):
            #print 'calcCentroids'
            coords = self.newcoords
            poly2cs = self.poly2cs
            cs2poly = self.cs2poly
            polyTemp={}
            for poly in coords.keys():
                xy = coords[poly]
                xyChar = PolyChar(xy)
                polyTemp[poly] = xyChar
            centroids = {}
            cs2polykeys = cs2poly.keys()
            cs2polykeys.sort()
            xvar = []
            yvar = []
            for csKey in cs2polykeys:
                #print csKey
                maxArea=0
                polyIds = cs2poly[csKey]
                for polyId in polyIds:
                    area = polyTemp[polyId].area
                    if area > maxArea:
                        maxArea = area
                        centroid = polyTemp[polyId].centroid
                centroids[csKey] = centroid
            self.centroids = centroids

            cs2polykeys = cs2poly.keys()
            cs2polykeys.sort()
            xvar = []
            yvar = []
            for csKey in cs2polykeys:
                centroid = self.centroids[csKey]
                xvar.append(centroid[0])
                yvar.append(centroid[1])
            #dmat = DistanceMatrix(xvar,yvar)
            n = len(xvar)
            x = SVariable(cs(xvar,n,1))
            x.setType("CS")
            x.setName("x")
            x.setRegionNames(self.regionNames)
            x.setTimeString(self.timeString)
            y = SVariable(cs(yvar,n,1))
            y.setType("CS")
            y.setName("y")
            y.setRegionNames(self.regionNames)
            y.setTimeString(self.timeString)
            self.dataBase.addVariable(x)
            self.dataBase.addVariable(y)
            #dmat.name = "distanceMatrix"
            #self.dataBase.addMatrix(dmat)
            #self.distMatOn = 1

    def calcDistanceMatrix(self):
        x = self.dataBase.getVariable('x')
        y = self.dataBase.getVariable('y')
        dmat = DistanceMatrix(x,y)
        dmat.name = "distanceMatrix"
        self.dataBase.addMatrix(dmat)
        self.distMatOn = 1


    def gabrielGraph(self):
        centroids = self.centroids
        try:
            dmat = self.dataBase.getMatrix("distanceMatrix").full()
        except:
            self.calcDistanceMatrix()
            dmat = self.dataBase.getMatrix("distanceMatrix").full()

        n = len(centroids)
        rn = range(n)
        keys = centroids.keys()
        neighbors = {}
        for i in rn[:-1]:
            for j in rn[i+1:]:
                keyI = keys[i]
                keyJ = keys[j]
                dij = dmat[i,j] / 2.
                pI = centroids[keyI]
                pJ = centroids[keyJ]
                px = (pI[0] + pJ[0]) / 2.
                py = (pI[1] + pJ[1]) / 2.
                keysLeft = [key for key in keys if (key != keyI and key != keyJ)]
                gabrielNeighbor = 1
                for key in keysLeft:
                    cx,cy = centroids[key]
                    d = sqrt( (cx-px)**2 + (cy-py)**2 )
                    if d <= dij:
                        gabrielNeighbor = 0
                        break
                if gabrielNeighbor:
                    if neighbors.has_key(keyI):
                        neighbors[keyI].append(keyJ)
                    else:
                        neighbors[keyI] = [keyJ]
                    if neighbors.has_key(keyJ):
                        neighbors[keyJ].append(keyI)
                    else:
                        neighbors[keyJ] = [keyI]
        gal = dict([ (item[0],[len(item[1]),item[1]]) for item in \
            neighbors.items() ])
        mat = spMatrix("Gabriel")
        mat.dict = gal
        self.dataBase.addMatrix(mat)

    def relativeProximity(self):
        try:
            dmat = self.dataBase.getMatrix("distanceMatrix").full()
        except:
            self.calcDistanceMatrix()
            dmat = self.dataBase.getMatrix("distanceMatrix").full()
        centroids = self.centroids
        n = len(centroids)
        rn = range(n)
        keys = centroids.keys()
        neighbors = {}
        for i in rn[:-1]:
            for j in rn[i+1:]:
                keyI = keys[i]
                keyJ = keys[j]
                dij = dmat[i,j] 
                di = dmat[i,:]
                dj = dmat[j,:]
                minmaxz = min([ max([di[z],dj[z]]) for z in range(n) ])
                if dij <= minmaxz:
                    if neighbors.has_key(keyI): 
                        neighbors[keyI].append(keyJ)
                    else:
                        neighbors[keyI] = [keyJ]
                    if neighbors.has_key(keyJ):
                        neighbors[keyJ].append(keyI)
                    else:
                        neighbors[keyJ] = [keyI]


        gal = dict([ (item[0],[len(item[1]),item[1]]) for item in \
            neighbors.items() ])
        mat = spMatrix("Relative")
        mat.dict = gal
        self.dataBase.addMatrix(mat)

    def sphereOfInfluence(self):
        try:
            dmat = self.dataBase.getMatrix("distanceMatrix").full()
        except:
            self.calcDistanceMatrix()
            dmat = self.dataBase.getMatrix("distanceMatrix").full()
        centroids = self.centroids
        n = len(centroids)
        rn = range(n)
        keys = centroids.keys()
        neighbors = {}
        for i in rn[:-1]:
            for j in rn[i+1:]:
                keyI = keys[i]
                keyJ = keys[j]
                dij = dmat[i,j] 
                di = sort(dmat[i,:])
                dj = sort(dmat[j,:])
                if dij <= di[1]+dj[1]:
                    if neighbors.has_key(keyI): 
                        neighbors[keyI].append(keyJ)
                    else:
                        neighbors[keyI] = [keyJ]
                    if neighbors.has_key(keyJ):
                        neighbors[keyJ].append(keyI)
                    else:
                        neighbors[keyJ] = [keyI]


        gal = dict([ (item[0],[len(item[1]),item[1]]) for item in \
            neighbors.items() ])
        mat = spMatrix("SOI")
        mat.dict = gal
        self.dataBase.addMatrix(mat)

class SBroadcast:
    """ """
    def __init__(self):
        self.sbroadcast = 1
    def interaction(self):
        mode = self.interactionVar.get()
        self.project.setInteractionVariable(mode)
        #self.project.InteractionVar.set(mode)

class SMap(Map,SBroadcast):
    """Application subclass of Map from gView.py"""
    def __init__(self,name,master,project,coords,
        values,varName,t,poly2cs,cs2poly,width=None,height=None,title=None,
        classification="percentiles",nBins=5,bins=[],legendType="sequential"):
        self.classification = classification
        self.nBins = nBins 
        self.bins = bins
        self.project = project
        tmp = self.project.getVariable(varName)
        self.variable = tmp
        regionNames = tmp.regionNames
        self.regionNames = regionNames
        lname = ["Map",self.variable.name,self.variable.timeString[t]]
        self.listName = (" ").join(lname)
        m=Map.__init__(self,name,master,coords,
        values,varName,t,poly2cs,cs2poly,width=None,
            height=None,title=None,
            classification=classification,nBins=nBins,bins=bins,
            legendType = legendType)
        SBroadcast.__init__(self)
        self.centroids = self.project.centroids
        self.canvas.bind("<Control-g>",self.drawContiguityGraph)
        self.canvas.bind("<Control-p>",self.drawPCovarGraph)
        self.xMidPoint = self.width / 2.0
        self.canvas.bind("<Control-c>",self.drawCovarGraph)
        self.canvas.bind("<Control-Button-2>",self.identifyWidget)


    def interactionBroadcast(self):
        SBroadcast.interaction(self)

    def updateTime(self,tsId):
        self.unhighlightCentroids()
        try:
            tsId = tsId[0]
            var = self.project.dataBase.getVariable(self.varName)
            title = "%s %s"%(self.varName,var.timeString[tsId])
            self.legendTitle = title
            self.top.title(title)
            #self.drawCanvasTitle(self.canvasTitle)
            x = var[:,tsId]
            self.values = array(x)
            self.binData()
            polyKeys = self.coords.keys()
            origColors = self.binIds

            for polyKey in polyKeys:
                colorId = origColors[self.poly2cs[polyKey]]
                try:
                    #color = MAPCOLORS[(colorId)]
                    color = self.mapColors[(colorId)]
                except:
                    color = "Black"
                pid = self.poly2widget[polyKey]
                self.origColors[pid] = color
                self.canvas.itemconfigure(pid,fill=color)
                self.canvas.itemconfigure(pid,outline="Black")

            observations = self.matcher.observations
            for observationKey in observations.keys():
                observation = observations[observationKey]
                observation.ts = [tsId]
                observations[observationKey] = observation
            self.matcher.observations = observations
        except:
            pass

    def ctrlMouseLeft(self,event):
        stat='coords:'+str(event.x)+','+str(event.y)
        self.lastx  = self.canvas.canvasx(event.x)
        self.lasty  = self.canvas.canvasy(event.y)
        oid = self.canvas.find_overlapping(self.lastx,self.lasty,self.lastx,self.lasty)
        if len(oid) > 0:
            for i in oid:
                if self.widget2poly.has_key(i):
                    wid = i
                else:
                    wid = ()
        else:
            wid = oid
        try:
            pid = self.widget2poly[wid]
            observation = self.matcher.observations[pid]
            ts = str(observation.ts)
            varNames = observation.variable
            variable = self.project.getVariable(varNames[0])
            var = self.project.dataBase.getVariable(self.varName)
            csNames = variable.regionNames
            csid = observation.cs[0]
            self.drawLEO(csid)
        except:
            pass

    def identifyWidget(self,event):
        stat='coords:'+str(event.x)+','+str(event.y)
        self.lastx  = self.canvas.canvasx(event.x)
        self.lasty  = self.canvas.canvasy(event.y)
        oid = self.canvas.find_overlapping(self.lastx,self.lasty,self.lastx,self.lasty)
        if len(oid) > 0:
            for i in oid:
                if self.widget2poly.has_key(i):
                    wid = i
                else:
                    wid = ()
        else:
            wid = oid
        try:
            pid = self.widget2poly[wid]
            observation = self.matcher.observations[pid]
            ts = str(observation.ts)
            varNames = observation.variable
            variable = self.project.getVariable(varNames[0])
            var = self.project.dataBase.getVariable(self.varName)
            csNames = variable.regionNames
            csid = observation.cs[0]
            csString = csNames[csid] + '\n'
            tsString = 'temporal id: ' + str(var.timeString[observation.ts[0]]) + '\n'
            value = variable[csid,observation.ts[0]]
            c = 0
            temps = ['X']
            xString = varNames[0] + "= " + str(value) + '\n'
            
            label = csString+tsString+xString
            oldcolor = self.canvas.itemcget(wid,"fill")
            self.oldcolor = oldcolor
            self.highlightSingleWidget(wid)
            self.tLabel = Label(self.canvas,text=label,bg='Yellow',font=('Times',
                options.AXISFONTSIZE))
            self.tempWID = wid
            if self.lastx < self.xMidPoint:
                self.identLabel = self.canvas.create_window(self.lastx+3, self.lasty, anchor=W, window=self.tLabel)
            else:
                self.identLabel = self.canvas.create_window(self.lastx-3, self.lasty, anchor=E, window=self.tLabel)            
        except KeyError:
            pass

    def mouseMiddleRelease(self,event):
        try:
            self.canvas.itemconfigure(self.tempWID,fill=self.oldcolor)
            self.canvas.delete(self.tLabel)
            self.canvas.delete(self.identLabel)
        except:
            pass

    def drawLEO(self,csId):
        y = self.variable[csId]
        v = self.variable
        x = self.project.timeClass.numeric
        tsLabels = self.tsIds
        xLabel = self.project.timeString
        yLabel = 'Relative '+ self.varName + ' -- ' + self.variable.regionNames[csId] 
        yLabel = self.varName + ' -- ' + self.variable.regionNames[csId]
        csIds = [csId]
        ts = STimeSeries(self.varName, self.project, self.master, x, y,
        self.varName, csIds, 'Y', yLabel=yLabel)
        ts.top.title("Map generated Time Series")

    def drawContiguityGraph(self,event):
        wNames = self.project.getMatrixNames()
        d = sd.SDialogue("Contiguity Graph")
        txt="""Choose a covariance matrix."""
        entries = ['Matrix']
        sd.MultiEntry(d,wNames, entries, title='Covariance Matrix',
                      helpText=txt)

        txt="""Choose a color for the contiguity links."""
        colors = ["black","white","red","blue","purple"]
        entries = ["Color"]
        sd.MultiEntry(d,colors, entries, title='Join Color',
                      helpText=txt)        

        d.draw()
        if d.status:
            wname = d.results[0]['Matrix']        
            color = d.results[1]['Color']
            w = self.project.dataBase.getMatrix(wname)
            centroids = self.project.centroids

            if w.matType == "sparse":
                dict = w.dict
                ids = dict.keys()
                for id in ids:
                    p1 = centroids[id]
                    neighbors = dict[id][1]
                    for neighbor in neighbors:
                        p2 = centroids[neighbor]
                        self.canvas.create_line(p1,p2,tag=("CENTROID"),fill=color)
                self.drawCentroids()
                self.centroidsOn = 1
            else:
                self.report("""You must choose a contiguity matrix.  Perhaps you
                chose a full distance or covariance matrix.""")

    def drawCovarGraph(self,event):
        wNames = self.project.getMatrixNames()
        d = sd.SDialogue("Covariance Graph")
        txt="""Choose a covariance matrix."""
        entries = ['Matrix']
        sd.MultiEntry(d,wNames, entries, title='Covariance Matrix',
                      helpText=txt)
        
        txt="""Choose a contiguity matrix."""
        entries = ['Matrix']
        sd.MultiEntry(d,wNames, entries, title='Contiguity Matrix',
                      helpText=txt) 

        d.draw()
        if d.status:
            wnameCV = d.results[0]['Matrix']        
            wnameCONT = d.results[1]['Matrix']        
            c = self.project.dataBase.getMatrix(wnameCV)
            w = self.project.dataBase.getMatrix(wnameCONT)
            b = c.binary
            centroids = self.project.centroids
            dict = w.dict
            keys = dict.keys()
            for key in keys:
                neighbors = dict[key][1]
                p1 = centroids[key]
                for neighbor in neighbors:
                    bij = b[key,neighbor]
                    if bij:
                        color="blue"
                    else:
                        color="red"
                    p2 = centroids[neighbor]
                    self.canvas.create_line(p1,p2,tag=("CENTROID"),fill=color)
            self.drawCentroids()
            self.centroidsOn = 1

    def drawPCovarGraph(self,event):
        #spider
        wNames = self.project.getMatrixNames()
        d = sd.SDialogue("Covariance Spider Graph")
        txt="""Choose a covariance matrix."""
        entries = ['Matrix']
        sd.MultiEntry(d,wNames, entries, title='Covariance Matrix',
                      helpText=txt)

        d.draw()
        if d.status:
            wname = d.results[0]['Matrix']        
            c = self.project.dataBase.getMatrix(wname)
            b = c.binary
            self.b = b
            centroids = self.project.centroids
            n = shape(b)[0]
            self.drawCentroids()
            self.centroidsOn = 1
            rn = range(n)
            # draw controllers for forward-backwards traveling
            self.canvas.create_rectangle(5,5,30,30,tag=("CONTROL",'forwardB',"CONTROLB"),fill='green')
            self.canvas.create_rectangle(35,5,60,30,tag=("CONTROL",'backwardB',"CONTROLB"),fill='white')
            self.canvas.create_rectangle(65,5,90,30,tag=("CONTROL",'closeB',"CONTROLB"),fill='red')


            self.canvas.tag_bind("forwardB","<Button-1>",self.cvForward)
            self.canvas.tag_bind("backwardB","<Button-1>",self.cvBackward)
            self.canvas.tag_bind("closeB","<Button-1>",self.cvClose)

            self.cvI = -1 
            self.rn = rn
            self.n = max(rn)

    def cvForward(self,event):
        self.cvI +=1
        if self.cvI not in self.rn:
            self.cvI = min(self.rn)
        self.canvas.delete("LINK")
        self.drawLinks()

    def cvBackward(self,event):
        self.cvI -=1
        if self.cvI not in self.rn:
            self.cvI = max(self.rn)
        self.canvas.delete("LINK")
        self.drawLinks()

    def drawLinks(self):
        p1 = self.project.centroids[self.cvI]
        name = self.project.regionNames[self.cvI]
        self.canvas.delete('cvname')
        self.canvas.create_text(95,17,text=name,tag=('cvname'),
            anchor=W)

        for j in self.rn:
            bij = self.b[self.cvI,j]
            if bij:
                color = 'blue'
                p2 = self.project.centroids[j]
                self.canvas.create_line(p1,p2,tag=("LINK"),fill=color)

    def cvClose(self,event):
        self.canvas.delete("CONTROL")
        self.canvas.delete("LINK")
        self.deleteCentroids()
        self.canvas.delete('cvname')

    def forwardEnter(self,event):
        self.canvas.itemconfig("forwardB",fill='green')
    def backwardEnter(self,event):
        self.canvas.itemconfig("backwardB",fill='yellow')
    def closeEnter(self,event):
        self.canvas.itemconfig("closeB",fill='red')
    def controlLeave(self,event):
        self.canvas.itemconfig("CONTROLB",fill='white')


class STable(Table,SBroadcast):
    """This is a comment"""
    def __init__(self,name,master,project, # project level options
            values,varName,tsid,csid,  # matcher options
            rowLabels,columnLabels,fmt=[12,8],type="table"):  # table options

        self.project = project
        self.name = name
        self.listName = "Table "+name
        Table.__init__(self,name,master,values,
                varName,tsid,csid,
                rowLabels,columnLabels,fmt=fmt,type=type)
        self.setName(name)
        SBroadcast.__init__(self)


class SMoranScatter(MoranScatter,SBroadcast):
    """Application subclass of MoranScatter from gView.py"""
    def __init__(self,name,master,project,allX,allLag,x,y,varName,variableX,variableY,t,
        xDelimiter=None,yDelimiter=None,title=None,
        xLabel=None, yLabel=None, xDecimal=None, yDecimal=None,
        ovalFill=None, ovalBorder=None,xPop='X',yPop='Y'):

        self.project = project
        self.allX = allX
        self.allLag = allLag
        self.varName = varName
        self.variableX = variableX
        self.variableY = variableY

        MoranScatter.__init__(self,name,master,x,y,varName,variableX,variableY,
            t,xDelimiter=None,yDelimiter=None,title=None,
            xLabel=xLabel, yLabel=yLabel, xDecimal=None, yDecimal=None,
            ovalFill=None, ovalBorder=None,xPop=xPop,yPop=yPop)
        SBroadcast.__init__(self)
        v = self.project.dataBase.getVariable(self.varName)
        ts = v.timeString[t]
        lname = ["Scatter",self.varName,ts]
        self.listName = (" ").join(lname)
        self.tsId = t
        self.canvas.bind("<Control-Button-2>",self.identifyWidget)

    def interactionBroadcast(self):
        SBroadcast.interaction(self)

    def updateTitle(self,titleString):
        self.setTitle(titleString)
        self.changeTitle()

    def updateTime(self,tsId):
        tsId=tsId[0]
        self.tsId = tsId
        var = self.project.dataBase.getVariable(self.varName)
        title = "%s %s"%(self.varName,var.timeString[tsId])
        self.updateTitle(title) 
        x = self.allX[:,tsId]
        y = self.allLag[:,tsId]
        self.x = x
        self.y = y
        timeStrings = var.timeString
        xLabel = "%s %s"%(self.varName,timeStrings[tsId])
        yLabel = "Spatial Lag %s %s"%(self.varName,timeStrings[tsId])
        self.canvas.delete('all')
        self.xLabel = xLabel
        self.yLabel = yLabel
        self.draw()
        #uncomment below if title is to remain constant
        self.drawCanvasTitle(self.canvasTitle)
        
    def drawLEO(self,csId):
        x = self.allX
        y = self.allLag
        avgY = mean(y)
        yr = mm(y,diag(1/avgY))
        avgX = mean(x)
        xr = mm(x,diag(1/avgX))
        x = x[csId,:]
        y = y[csId,:]
        varName = self.varName
        csLabels = self.allX.regionNames
        title="Spatial Lag Time Path"
        xLabel = "%s %s"%(varName,csLabels[csId])
        yLabel = "Spatial Lag %s %s"%(varName,csLabels[csId])

        tp = STimePath(varName,self.project,self.master,
            x=x,
            y=y,
            t=range(len(y)),
            title=title,
            csIds = [ csId ],
            tsLabels = range(len(x)),
            xLabel=xLabel,
            yLabel=yLabel)

    def identifyWidget(self,event):
        """
        Overrides Generic Plot Method
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        self.lastx  = self.canvas.canvasx(event.x)
        self.lasty  = self.canvas.canvasy(event.y)
        oid = self.canvas.find_overlapping(self.lastx,self.lasty,self.lastx,self.lasty)
        if len(oid) > 0:
            for i in oid:
                if self.widget2Id.has_key(i):
                    wid = i
                else:
                    wid = ()
        else:
            wid = oid
        try:
            cid = self.widget2Id[wid]
            tx = self.x[cid]
            ty = self.y[cid]
            variable = self.project.dataBase.getVariable(self.varName)
            csNames = variable.regionNames
            csString = csNames[cid] + '\n'
            tsString = 'temporal id: ' + str(variable.timeString[self.tsId]) + '\n'
            xString = self.varName + "= " + str(tx) + '\n'
            yString = "Spatial Lag of " + self.varName + "= " + str(ty) 
            label = csString+tsString+xString+yString

            self.highlightSingleWidget(wid)
            self.tLabel = Label(self.canvas,text=label,bg='Yellow',font=('Times', options.AXISFONTSIZE))
            self.tempWID = wid
            if self.lastx < self.xMidPoint:
                self.identLabel = self.canvas.create_window(self.lastx+3, self.lasty, anchor=W, window=self.tLabel)
            else:
                self.identLabel = self.canvas.create_window(self.lastx-3, self.lasty, anchor=E, window=self.tLabel)            
        except KeyError:
            pass

    def mouseMiddleRelease(self,event):
        """
        Overrides Generic Plot Method
        """
        try:
            self.unhighlightSingleWidget(self.tempWID)
            self.canvas.delete(self.tLabel)
            self.canvas.delete(self.identLabel)
        except:
            pass


class SDensity(Density,SBroadcast):
    def __init__(self,name,master,project,varName,y,csid=[],tsid=[],
        title="Kernel Density",xLabel='X',yLabel='f(x)',xmin=None,xmax=None):
        self.master = master
        self.project = project
        self.title = title
        SDensity.nden += 1
        name = "density_%d"%SDensity.nden
        Density.__init__(self,name,master,varName,y,csid=csid,tsid=tsid,
        title=title,xLabel=xLabel,yLabel=yLabel,xmin=xmin,
        xmax=xmax)
        self.canvas.pack(side=LEFT,anchor=W)
        self.type = "density"
        self.top.title(title)
        self.name =  name
        self.variable = self.project.getVariable(varName)
        SBroadcast.__init__(self)
        l=["Density",self.variable.name,self.variable.timeString[tsid[0]]]
        self.listName = (" ").join(l)
        #print self.listName

    def interactionBroadcast(self):
        SBroadcast.interaction(self)


class SCDF(CDF,SBroadcast):
    def __init__(self,name,master,project,varName,y,csid=[],tsid=[],
        title="CDF",xLabel='X',yLabel='F(x)',xmin=None,xmax=None):
        self.master = master
        self.project = project
        self.title = title
        SCDF.nden += 1
        name = "CDF_%d"%SDensity.nden
        CDF.__init__(self,name,master,varName,y,csid=csid,tsid=tsid,
        title=title,xLabel=xLabel,yLabel=yLabel,xmin=xmin,
        xmax=xmax)
        self.canvas.pack(side=LEFT,anchor=W)
        self.type = "CDF"
        self.top.title(title)
        self.name =  name
        self.variable = self.project.getVariable(varName)
        SBroadcast.__init__(self)
        l=["CDF",self.variable.name,self.variable.timeString[tsid[0]]]
        self.listName = (" ").join(l)

    def interactionBroadcast(self):
        SBroadcast.interaction(self)


class SHistogram(Histogram,SBroadcast):
    """Application subclass of Histogram from gView.py"""
    def __init__(self,name,master,varName,allX,project,
        x,y,xDelimiter=None,yDelimiter=None,title=None,
        xLabel=None, yLabel=None, xDecimal=None,yDecimal=None,  
        ovalFill=None, ovalBorder=None, csIds = [], tsIds = [],
        xPop='X',yPop='Observations in set',
        classification="sturges",nBins=5,bins=[]):

        self.project = project
        self.varName = varName
        self.allX = allX
        Histogram.__init__(self,name,master,x,y,title=varName,csIds=csIds,tsIds=tsIds,xLabel=xLabel,
            yLabel=yLabel,xPop=xPop,yPop=yPop,
            classification=classification,nBins=nBins,bins=bins)

        SBroadcast.__init__(self)
        v = self.project.dataBase.getVariable(self.varName)
        lname = ["Histogram",self.varName]
        self.listName = (" ").join(lname)

    def interactionBroadcast(self):
        SBroadcast.interaction(self)

    def updateTitle(self,titleString):
        self.setTitle(titleString)
        self.changeTitle()


    def updateTime(self,tsId):
        classification = self.matcher.classification
        if classification == "userDefined":
            bins = self.matcher.Bins
            nBins = 5
        elif classification == "equalWidth":
            bins = []
            nBins = self.matcher.nBins
        else:
            bins = []
            nBins = 5
        tsId = tsId[0]
        var = self.project.dataBase.getVariable(self.varName)
        title = "%s %s"%(self.varName,var.timeString[tsId])
        self.updateTitle(title)
        self.x = self.allX[:,tsId]
        csIds = range(len(self.x))
        self.matcher = IHistogram(self.xLabel,self.x,
                tsId,csIds,
                classification=classification,
                nBins=nBins,
                bins=bins)
        self.canvas.delete('all')
        self.draw()
        self.drawCanvasTitle(self.canvasTitle)
 
class STimeSeries(TimeSeries,SBroadcast):
    """Subclass of TimeSeries """
    def __init__(self, name, project, master, x, y,  varName, csids, allY,
                 xLabel='t', yLabel='Y', yPopUp=None, tsLabels=[], xPop='t',
                 yPop='Y'):

        self.name = name
        self.project = project 
        master = master
        self.allY = allY
        self.csIds = csids

        TimeSeries.__init__(self,name,master,x,y,
                        csIds = csids,
                        xLabel=xLabel,yLabel=yLabel,tsLabels=tsLabels,
                        xPop=xPop,yPop=yPop)

        SBroadcast.__init__(self)
        self.tsIds = y
        self.varName = varName
        self.yPopUp = yPopUp
        self.setPopUp()
        l = ["Time Series",varName]
        self.listName = (" ").join(l)
        #print self.listName
        
        self.canvas.bind("<Control-Button-2>",self.identifyWidget)

    def interactionBroadcast(self):
        mode = self.interactionVar.get()
        self.project.setInteractionVariable(mode)
    def setPopUp(self):
        if self.yPopUp == None:
            self.yPopUp = self.varName 
        else:
            pass
        
    def identifyWidget(self,event):
        stat='coords:'+str(event.x)+','+str(event.y)
        self.lastx  = self.canvas.canvasx(event.x)
        self.lasty  = self.canvas.canvasy(event.y)
        oid = self.canvas.find_overlapping(self.lastx,self.lasty,self.lastx,self.lasty)
        if len(oid) > 0:
            for i in oid:
                if self.widget2Id.has_key(i):
                    wid = i
                else:
                    wid = ()
        else:
            wid = oid
        try:
            cid = self.widget2Id[wid]
            observation = self.matcher.observations[cid]
            ts = str(observation.ts)
            varNames = observation.variable
            values = observation.value
            var = self.project.dataBase.getVariable(self.varName)
            tsString = self.xPop + ": " + str(var.timeString[observation.ts]) 
            yString =  self.yPop+ ": " + str(values) + '\n' 
            label = yString+tsString
            self.highlightSingleWidget(wid)
            self.tLabel = Label(self.canvas,text=label,bg='Yellow',font=('Times', options.AXISFONTSIZE))
            self.tempWID = wid
            if self.lastx < self.xMidPoint:
                self.identLabel = self.canvas.create_window(self.lastx+3, self.lasty, anchor=W, window=self.tLabel)
            else:
                self.identLabel = self.canvas.create_window(self.lastx-3, self.lasty, anchor=E, window=self.tLabel)            
        except KeyError:
            pass

    def mouseMiddleRelease(self,event):
        try:
            self.unhighlightSingleWidget(self.tempWID)
            self.canvas.delete(self.tLabel)
            self.canvas.delete(self.identLabel)
        except:
            pass
            
class SBoxPlot(BoxPlot,SBroadcast):
    """ """
    def __init__(self,name,project,master,x,csids,tsids,allX,
                 fence=1.5,stemPoints=1):
        self.name = name
        self.varName = name
        self.project = project
        self.allX = allX
        self.csids = csids
        self.tsids = tsids 
        varName = name
        BoxPlot.__init__(self,name,master,varName,x,tsids,csids,fence,
                         stemPoints)

        SBroadcast.__init__(self)
        var = self.project.getVariable(varName)
        title = "%s %s"%(self.varName,var.timeString[tsids[0]])
        self.top.title(title)
        lname = ["Box Plot",self.varName,var.timeString[tsids[0]]]
        self.listName = (" ").join(lname)
        #print self.listName

    def interactionBroadcast(self):
        SBroadcast.interaction(self)

    def updateTitle(self,titleString):
        self.changeTitle(titleString)

    def updateTime(self,tsId):
        tsId = tsId[0]
        var = self.project.dataBase.getVariable(self.varName)
        title = "%s %s"%(self.varName,var.timeString[tsId])
        self.updateTitle(title)
        self.x = self.allX[:,tsId]
        csIds = range(len(self.x))
        fence = self.fence
        self.matcher = IBox(self.varName,self.x,csIds,[tsId],fence=fence)
        self.canvas.delete('all')
        self.draw()

        title = "%s %s"%(self.varName,var.timeString[tsId])
        self.top.title(title)
        self.drawCanvasTitle(self.canvasTitle)

class SpaceTimeButtonMatrix(View):
    """ """
    stbm = 0
    def __init__(self,project,master,name,y,ylag):
        self.name = name
        self.varName = name
        self.master = master
        self.project = project
        View.__init__(self,name,master)
        self.type = "stbm"
        SpaceTimeButtonMatrix.stbm +=1
        self.name = "stbm_%d"%SpaceTimeButtonMatrix.stbm
        self.top.title(self.name)
        self.canvas.pack(side=LEFT,anchor=W)
        h = self.height * .9
        w = self.width * .9
        self.y=y
        self.ylag = ylag
        self.listName = "Space-Time Button Matrix "+name
        #print self.listName
        self.identificationLabels = ['Time-Time Lag', 'Spatial Lag', 'Space-Time Lag']

        variable = self.project.getVariable(name)
        self.variable = variable
        t = variable.t

        leftBound = self.width * 0.05
        topBound = self.height * 0.05
        self.leftBound = leftBound
        self.rightBound = self.width * .95
        self.xMidPoint = self.leftBound + ((self.rightBound - self.leftBound)/2.0)
        self.topBound = topBound

        cellWidth = w/t
        oldw = cellWidth
        h1 = h/t
        if (h1 > cellWidth):
            cellHeight = cellWidth
        else:
            cellHeight = h1
            cellWidth = cellHeight

        leftBound = (self.width - cellWidth * t)/2.

        rt = range(t)
        cellDict = {}
        widget2cell = {}
        self.canvas.unbind(ALL)
        coords = {}
        ab={}
        
        for i in rt:
            for j in rt:
                key = (i,j) 
                if i == j:
                    color = "white"
                elif i > j:
                    color = "blue"
                else:
                    color = "red"
                xo = leftBound + j * cellWidth
                x1 = xo + cellWidth
                yo = topBound + i * cellHeight
                y1 = yo + cellHeight
                cellTag = "%d_%d"%(i,j)
                cid=self.canvas.create_rectangle(xo,yo,x1,y1,fill=color,tag=(cellTag,"CELL"))
                coords[cellTag] = (xo,yo,x1,y1)
                cellDict[key] = cid
                widget2cell[cid] = key
                ab[cellTag] = (i,j)
        self.widget2cell = widget2cell
        self.cellDict = cellDict
        self.widgetKeys = self.cellDict.keys()
        self.coords=coords
        self.ab = ab

        self.canvas.tag_bind("CELL", "<Any-Enter>", self.enterCell)
        self.canvas.tag_bind("CELL", "<Any-Leave>", self.leaveCell)
        self.canvas.bind("<1>",self.mouseLeftButton)

    def enterCell(self,event):
        x1=self.canvas.canvasx(event.x)
        x2=x1
        y1=self.canvas.canvasy(event.y)
        y2=y1
        tags = self.canvas.gettags(CURRENT)
        coords = self.coords[tags[0]]
        cellId = self.ab[tags[0]]
        a,b=cellId
        self.canvas.itemconfig(tags[0],fill="yellow")
        ta = self.variable.timeString[a]
        tb = self.variable.timeString[b]
        if a>b:
            tsString = self.identificationLabels[2]+" -- ("+ta+", "+tb+")"
        elif a==b:
            tsString = self.identificationLabels[1]+" -- ("+ta+")"
        else:
            tsString = self.identificationLabels[0]+" -- ("+ta+", "+tb+")"
            
        self.tLabel = Label(self.canvas,text=tsString,bg='Yellow',font=('Times', 10))
        if x1 < self.xMidPoint:
            self.identLabel = self.canvas.create_window(x1+3, y1, anchor=W, window=self.tLabel)
        else:
            self.identLabel = self.canvas.create_window(x1-3, y1, anchor=E, window=self.tLabel)
                
    def leaveCell(self,event):
        tags = self.canvas.gettags(CURRENT)
        tagOff = tags[0]
        a,b=self.ab[tagOff]
        if a == b:
            self.canvas.itemconfigure(tagOff,fill="white")
        elif a > b:
            self.canvas.itemconfigure(tagOff,fill="blue")
        else:
            self.canvas.itemconfigure(tagOff,fill="red")
        self.canvas.delete(self.tLabel)
        self.canvas.delete(self.identLabel)

    def mouseLeftButtonRelease(self,event):
        # use for newSelection
        self.modButton = "none" 
        x1=self.canvas.canvasx(event.x)
        x2=x1
        y1=self.canvas.canvasy(event.y)
        y2=y1
        tg = self.canvas.find_below(CURRENT)
        tags = self.canvas.gettags(CURRENT)
        try:
            a,b=self.ab[tags[0]]
            self.processCell(a,b)
            self.canvas.itemconfig(tags[0],fill="yellow")
        except:
            pass

    def processCell(self,a,b):
        tp = "%d %d"%(a,b)
        if a>b:
            yt = self.y[:,a]
            ylt = self.ylag[:,b]
            tp = "%d %d"%(a,b)
            ta = self.variable.timeString[a]
            tb = self.variable.timeString[b]
            yLabel = "Spatial Lag %s  %s"%(self.varName,tb)
            xLabel = "%s  %s"%(self.varName,ta)
            s=SMoranScatter(tp,self.master,self.project,self.y,self.ylag,yt,ylt,varName=self.varName,
                     variableX=a,
                     variableY=b,
                     t=int(a),
                     yLabel=yLabel,
                     xLabel=xLabel)
            name = "space-time lag"
            s.top.title(name)

        elif a==b:
            yt = self.y[:,a]
            ylt = self.ylag[:,b]

            ta = self.variable.timeString[a]
            tb = self.variable.timeString[b]
            yLabel = "Spatial Lag %s  %s"%(self.varName,tb)
            xLabel = "%s  %s"%(self.varName,ta)
            s=SMoranScatter(tp,self.master,self.project,self.y,self.ylag,yt,ylt,varName=self.varName,
                     variableX=a,
                     variableY=b,
                     t=int(a),
                     yLabel=yLabel,
                     xLabel=xLabel)
            name = "spatial lag"
            s.top.title(name)
        else:
            yt = self.y[:,a]
            ylt = self.y[:,b]
            ta = self.variable.timeString[a]
            tb = self.variable.timeString[b]
            yLabel = "%s  %s"%(self.varName,tb)
            xLabel = "%s  %s"%(self.varName,ta)
            s=SMoranScatter(tp,self.master,self.project,self.y,self.ylag,yt,ylt,varName=self.varName,
                     variableX=a,
                     variableY=b,
                     t=int(a),
                     yLabel=yLabel,
                     xLabel=xLabel)
            name = "time lag"
            s.top.title(name)

class STimePath(TimePath):
    """ """
    def __init__(self,name,project,master,
        x,
        y,
        t,
        title,
        csIds=[],
        tsLabels=[],xLabel="X",yLabel="Y",xPop='X',yPop='Y'):

        self.project = project
        self.name = name
        self.master = master
        self.csIds = csIds
        TimePath.__init__(self,"TimePath",self.master,x,y,t,"TimePath",
            tsLabels=tsLabels,
            csIds=csIds,xLabel=xLabel,yLabel=yLabel,xPop=xPop,yPop=yPop)
        lname=["Time Path",xLabel,yLabel]
        self.listName = (" ").join(lname)
        #print self.listName

    def interactionBroadcast(self):
        mode = self.interactionVar.get()
        self.project.setInteractionVariable(mode)

class SPCP(PCP):
    """"""
    def __init__(self,name,project,master,varNames,y,t,z=[],zName=None):
        self.project = project
        self.name = name
        self.master = master
        PCP.__init__(self,"PCP",self.master,varNames,y,t,z,zName)
        self.listName = "PCP "+(" ").join(varNames)

    def interactionBroadcast(self):
        mode = self.interactionVar.get()
        self.project.setInteractionVariable(mode)

    def updateTime(self,tsId):
        tsId = tsId[0]
        newY = []
        time = []
        for i in self.varNames:
            try:   # for CSTS Variables
                xAll = self.project.dataBase.getVariable(i)
                x = xAll[:,tsId]
                newY.append(x)
                t = xAll.timeString[tsId]
                if t not in time:
                    time.append(t)
            except:   # for CS Variables
                xAll = self.project.dataBase.getVariable(i)
                x = xAll[:,0]
                newY.append(x)
        self.y = newY
        self.canvas.delete('all')
        self.draw()
        tstring = time[0]
        title = "%s %s"%('PCP',tstring)
        self.top.title(title)
        self.drawCanvasTitle(self.canvasTitle)
        
        
        
class App(GuiMixin, GuiMaker):   # or GuiMakerFrameMenu
    """application level class"""
    
    def start(self):
        #self.project = Project("temp")
        #self.project.directory = os.getcwd()
        #Splash = SplashScreen(self.master)
        self.hellos = 0
        self.master.title("STARS: Space-Time Analysis of Regional Systems")
        self.master.iconname("STARS")
        self.master.bind("<Control-q>", self.quit)
        h = self.winfo_screenheight()
        w = self.winfo_screenwidth()
        geom = "%dx%d"%(w,h)
        self.master.geometry("600x400+0+0")

        # set to toolBar to have a toolbar :)
        self.toolBarn = [ ('IO',self.interactionOff,{'side':LEFT}),
                        ('IL',self.interactionLinking,{'side':LEFT}),
                        ('IB',self.interactionBrushing,{'side':LEFT}),
                        ('LO',self.mapLegendsOff,{'side':LEFT}),
                        ('LL',self.mapLegendsLeft,{'side':LEFT}),
                        ('RL',self.mapLegendsRight,{'side':LEFT}),
                        ('RV',self.raiseAll,{'side':LEFT})
                        ]
        
        #define menus
        self.menuBar = [                               
          ('File', 0,                                  # (pull-down)
              [#('New Project ...',  0, self.newProject),           # [menu items list]
               ('Open Project ...', 0, self.openProject), 
               ('Project Summary',0,self.projectSummary),
               'separator',                            # add a separator
               ('Save Project ...', 0, self.saveProject),
               ('Save Project As ...',1, self.saveProjectAs),
               'separator',
               ('Exit  <CTRL-q>',    1, self.Quit)]              # label,underline,action
          ),
          ('Data', 0,
              [
                   ('Variable', 0,
                      [
                      ('List',0,
                         [('Variable Names and Types',0,self.listVariablesPartial),
                          #('Variable Names and Types',0,self.varSelector),
                          ('Observation Ids',0,self.listIds),
                          ('List Variable',0,self.listVariable),
                          ('List Variables (Noninteractive)',0,self.listVariablesNonInteractive )
                          ]),
                       'separator',
                       ('Create',0,
                       [
                        ('Spatial Lag',0,self.sLag),
                        ('Log',0,self.logTransform),
                        ('z',0,self.zTransform),
                        ('Transform',0,self.transform),
                        ('Raw Rate',0,self.rawRate),
                        ('Spatally Smoothed Rate',0,self.spatialRate),
                        ('Empirical Bayes Rate',0,self.eBayesRate)
                       ]),
                       ('Delete',0, self.deleteVariable),
                       ]
                   ),
                   ('Matrix', 0,
                      [
                      ('List Matrix Names',0,self.listMatrices),
                      ('List Matrix Values',1,self.listMatrix),
                      #('Characteristics',  0, self.matrixCharacteristics),
                       'separator',
                      ('Create', 1,
                                   [("Distance based",0,
                                      self.distanceMatrix),
                                    ("Regime based",0,self.regimeMatrix),
                                    ("Gabriel Proximity",0,self.gabriel),
                                    ("Relative Proximity",1,
                                      self.relativeProximity),
                                    ("Sphere of Influence Proximity",0,
                                      self.sphereOfInfluence),
                                    ('Gis Contiguity',1,self.gis2Gal),
                                    ('Covariance',0,self.covarMatrix),
                                    'separator',
                                    ('Spatial Multiplier',0,self.spatialMultiplier)
                                   ]
                      ), 
                        'separator',
                      ('Characteristics',0,self.weightCharacteristics),
                        'separator',
                      ('Delete',0, self.deleteMatrix)
                       ]
                   )
               ]
          ),
          ('Analysis', 0,
               [('Descriptive',0,
               [('Summary',0,
                [('Cross section',0,self.dscs),
                 ('Time series',0,self.dsts),
                 ('Pooled',0,self.dspool)]),
                ('Distribution',0,
                [('Cross section',0,self.ddcs),
                 ('Time series',0,self.ddts),
                 ('Pooled',0,self.ddpool)])]
               ),
               ('ESDA',   0,
               [('Moran Global', 0, self.moran),
                ('Moran Local', 1, self.localMoran), 
                ('Geary Global', 1, self.geary), 
                ('Geary Local', 8, self.localGeary), 
                ('G Global', 0, self.globalG), 
                ('G Local', 2, self.localG),
                ('Trace Test',0,self.traceTest)] 
               ),
               ('Inequality...',  0, 
                    [('Classic Gini',0,self.gini),
                     ('Spatial Gini',0,self.ginis),
                     ('Global Theil',0,self.theil),
                     ('Theil Decomp',6,self.theild)
                    ]
               ),
               ('Mobility',   0,
               [('Tau', 0, self.tau),
                ('Theta ', 2, self.theta),] 
               ),
               ('Markov',   1, 
               [('Classic',0,self.markov),
                ('Spatial',0,self.smarkov),
                ('Local Moran',0,self.localTrans)]
               ),
               ('Clustering',1,
                   [('Kmeans',0,self.kmeans)]
               )
               #('Econometrics', 3,
               #   [('Classic', 0, 
               #   [('Cross-section',0,self.notdone),
               #    ('Time-series',0,self.notdone),
               #    ('Panel',0,self.notdone)]
               #   ), 
               #    ('Spatial',  0, 
               #    [('Spatial Lag',8,self.notdone),
               #     ('Spatial Error',8,self.notdone)]
               #    )
               #    ]
               #)]
               ]
          ),
          ('Visualization', 0,
              [('Map',     0, 
              [('Quantile',0,self.quantileMap),
               ('Box Map',0,self.boxMap),
               ('Std. Deviation',0,self.stdmap),
               ('Diverging',1,self.divergingMap),
               ('Sequential User Defined',1,self.userDefinedC),
               'separator',
               ('Regime',2,self.regimeMap),
               ('Qualitative User Defined',2,self.userDefinedD)
               ]),
               ('Scatter Plot',0,self.scatter),
               ('Conditional Scatter Plot',0,self.cscatter),
              ('Histogram',    0, 
              [('Sturges Rule',0,self.histogramSturges),
               ('Equal Width',0,self.histogramEqualWidth),
               ('User Defined',0,self.histogramUserDefined)]),
               ('Regional Time Series',0,self.timeSeriesCs),
               ('Time Series',0,self.timeSeries),
               ('Time Path',5,self.timePath),
               ('Box Plot',0,self.boxPlot),
               ('Density',0,self.density),
               ('CDF',0,self.cdf),
               ('Parallel Coordinate Plot',1,self.pcp),
               'separator',
               ('Space Time Button Matrix',11,self.spaceTimeButtonMatrix),
               'separator',
               ('View Controller',6,self.createViewController)
               ]
          ),
          ('Window', 0,
              [('Iconify All',     0, self.iconify),
               ('DeIconify All', 0, self.deiconify),
               ('Raise All', 0, self.raiseAll),
               #('Arrange', 0, self.arrangeAll),
               'separator',
               ('List Views',0,self.listViews),
               ('Close All',0,self.closeWindows)
               ]
          ),
          ('Help',0,
            [('User Manual',0,self.userManual),
               #'separator',
               #('Movies',0,
               #    [('Visualization',0,
               #       [("Linking Views",0,self.notdone),
               #        ("Brushing Views",0,self.notdone),
               #        ("Spatial Roaming",0,self.notdone),
               #        ("Temporal Roaming",0,self.notdone),
               #        ("Spatial Traveling ",0,self.notdone),
               #        ("Temporal Traveling ",0,self.notdone),
               #        ]),
               #     ('Analysis',0,self.notdone),
               #     ('ESDA',1,self.notdone)]),
               'separator',
               ('Example Project',0,self.example),
             'separator',
             ('About',0,self.about),
             ('Credits',0,self.gcredits)
             ]
          )
          ] 
        time.sleep(1.0)
        ss.Destroy()
        #self.disableMenus()


    def error(self,string):
        so = "STARS Error: %s"%string
        self.report(so)


    def quit(self, event):
        self.Quit()

    def disableMenus(self):
        try:
            fileMenu = self.menus[0]
            menus = zipper(self.menus)
            for i,menu in menus:
                if i!=0 and i!=5:
                    menu['state']=DISABLED
            fileMenu=fileMenu.children.values()[0]
            fileMenu.entryconfigure(2,state=DISABLED)
            fileMenu.entryconfigure(4,state=DISABLED)
            fileMenu.entryconfigure(5,state=DISABLED)
            #fileMenu.entryconfigure(5,state=DISABLED)
        except:
            pass
        
    def enableMenus(self):
        try:
            fileMenu = self.menus[0]
            menus = zipper(self.menus)
            for i,menu in menus:
                menu['state']=NORMAL
            fileMenu=fileMenu.children.values()[0]
            fileMenu.entryconfigure(2,state=NORMAL)
            fileMenu.entryconfigure(4,state=NORMAL)
            fileMenu.entryconfigure(5,state=NORMAL)
        except:
            pass

    ######################################## 
    # File callbacks
    ######################################## 
    def Quit(self):
        # added to deal with shell+gui options
        self.quit
        self.master.destroy()
        sys.exit(0)

    def example(self):
        """canned loading of data files and matrices for debugging"""
        self.project = SProject("current",self.master,self)
        topDir = options.getSTARSHOME()
        self.project.directory = os.path.join(topDir,"data")
        projectFile = os.path.join(self.project.directory,"csiss.prj")
        t=self.project.ReadProjectFile(projectFile)
        if hasattr(self.project,"coords"):
            self.project.scaleCoords()
        else:
            self.report("no coords in project")
        #self.master.configure(cursor=options.DEFAULTCURSOR)
        #self.Editor.configure(cursor='crosshair')
        self.projectSummary()
        self.enableMenus()

    def newProject(self):
        options={}
        options[1] = ["Name",StringVar()]
        SDialog("New Project",options)
        #global project
        project = SProject(options[1][1].get(),self.master,self)
        self.project = project
        self.report("Created project: " + self.project.name)  
        so = "Project(\""+self.project.name+"\")"
        self.session = CommandHistory(self.project.name+".spj")
        self.session.addCommand(so)

    def openProject(self,projectName=None):
        # close any  existing projects
        try:
            self.closeWindows()
            self.saveProject()
        except:
            pass
        if projectName:
            fin=projectName
            projectDir = os.path.dirname(fin)
            txt="Opening project file, please wait."
            qd=sd.Warning(self.master,text=txt)
            self.project = SProject(fin,self.master,self)
            t=self.project.ReadProjectFile(fin)
            qd.destroy()
            if hasattr(self.project,"coords"):
                txt="Scaling coordinates, please wait."
                qd=sd.Warning(self.master,text=txt)
                self.project.scaleCoords()
                qd.destroy()
            else:
                self.report("no coords in project")
                self.projectSummary()
                self.enableMenus()
        else:

            fin = askopenfilename(filetypes=[("STARS Projects","*.prj")])
            if fin:
                projectDir = os.path.dirname(fin)
                # check if there is a session open and close it
            #    global project
                self.project = SProject(fin,self.master,self)
                self.project.directory = projectDir
                txt="Reading project file. Please wait."
                qd=sd.Warning(self.master,text=txt)
                t=self.project.ReadProjectFile(fin)
                qd.destroy()
                if hasattr(self.project,"coords"):
                    txt="Scaling coordinates, please wait."
                    qd=sd.Warning(self.master,text=txt)
                    self.project.scaleCoords()
                    qd.destroy()
                else:
                    self.report("no coords in project")
                self.projectSummary()
                self.enableMenus()

    def saveProject(self):
        self.project.writeProjectFile(self.project.name)

    def saveProjectAs(self):
        fin = asksaveasfilename(filetypes=[("STARS Projects","*.prj")])
        fileName = fin 
        self.project.name = fileName
        self.saveProject()

    def projectSummary(self):
        self.report(self.project.catalogue())
        #self.report(self.project.listRegionNames())

    ######################################## 
    # Data callbacks
    ######################################## 

    def importData(self):
        fileName = askopenfilename(filetypes=[("STARS Data", ".dat")])
        if fileName == "":
            return
        before = fileName.split(".")[0]
        self.project.ReadData(before)
        self.report("Imported Data File: " + fileName)
        self.report(self.project.catalogue())
        self.session.addCommand("ReadData(\""+fileName+"\")")

    def importMatrix(self):
        fileName = askopenfilename(filetypes=[("GAL matrices", ".gal")])
        if fileName == "":
            return
        before = fileName.split(".")[0]
        last = before.split("/")[-1]
        self.project.ReadGalMatrix(last)
        self.report("Imported GAL Matrix: " + fileName)
        self.report("Matrices Available: " + str(self.project.dataBase.matrices.keys()))
        self.session.addCommand("ReadGalMatrix(\""+last+"\")")

    def listVariablesPartial(self):
        self.report(self.project.listVariablesPartial())

    def listVariablesFull(self):
        self.report(self.project.listVariables(fmt=[[12,3]]))
    def varSelector(self):
        class VarSelector(ScrolledList):
            def on_select(self,index):
                print "select", self.get(index)
            def on_double(self,index):
                print "double", self.get(index)
        tmp = Toplevel(self.master)
        s = VarSelector(tmp,singleSelect=1)
        vnames = self.project.dataBase.getVariableNames()
        for vname in vnames:
            s.append(vname)
        print s.getSelections()

    def listVariable(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Variable Listing")
        txt="""Select the name of a variable to display in a table."""
        entries=['Variable']
        sd.MultiEntry(d, varNames, entries, title='Variable', helpText=txt)
        sd.SpinEntry(d, label="Width", values=range(1,16),
                     align="LEFT", title="Interval", default=7)
        sd.SpinEntry(d, label="Decimals", values=range(12),
                     align="LEFT", title="Decimals", default=3)
        d.draw()
        if d.status:
            variableName = d.results[0]['Variable']
            width = int(d.results[1])
            decimals = int(d.results[2])
            variable = self.project.dataBase.getVariable(variableName)
            fmt = [ width, decimals ]
            n = variable.n
            t= variable.t
            nt = n*t
            var=[[id] for id in [variableName]*nt]
            values = variable
            csids = array( [ [i] * t for i in range(n) ])
            csids = csids.ravel()
            ts =range(t)
            tsids = array(  ts * n )
            tsids = tsids.ravel()
            csids = [ [cs] for cs in csids]
            tsids = [ [ts] for ts in tsids]
            columnLabels = self.project.timeString
            columnLabels = [ columnLabels[id] for id in range(t) ]
            rowLabels = self.project.regionNames
            top = Toplevel(self.master)
            STable(variableName,top,self.project,
                    values,var,tsids,csids,rowLabels,columnLabels,fmt=fmt)

    def listVariablesNonInteractive(self):
        varNames = self.get_CS_CSTS_variable_names()
        dg = sd.SDialogue('List Variables')
        txt="The variable values will be listed in a table."
        entries = ['Variable']
        sd.DualListBoxes(dg,varNames,title="CS and CSTS Variables",
                         helpText=txt)
        tsVars = self.project.getTSVariableNames()
        sd.DualListBoxes(dg,tsVars,title='TS Variables',helpText=txt)
        sd.SpinEntry(dg, label="Width", values=range(1,16),
                     align="LEFT", title="Interval", default=7)
        sd.SpinEntry(dg, label="Decimals", values=range(12),
                     align="LEFT", title="Decimals", default=3)

        dg.draw()
        
        if dg.status:
            csTsVarNames = dg.results[0]
            tSVarNames = dg.results[1]
            width = int(dg.results[2])
            decimals = int(dg.results[3])
            c=0
            columnLabels = []
            tsids = []
            for variableName in csTsVarNames:
                variable = self.project.getVariable(variableName)
                if c:
                    table = concatenate((table,variable),1)
                else:
                    table = variable
                if variable.varType == "CSTS":
                    vn=variable.name
                    labels = ["%s_%s"%(vn,t) for t in variable.timeString] 
                else:
                    labels = [variable.name]
                c+=1
                tsids.extend(range(variable.t))
                columnLabels.extend(labels)
            tsids = array(tsids * variable.n)
            tsids = tsids.ravel()
            tsids = [ [ts] for ts in tsids]
            n=variable.n
            k = len(columnLabels)
            csids = array( [ [i] * k for i in range(n) ])
            csids = csids.ravel()
            csids = [ [cs] for cs in csids]
            fmt = [ int(width),int(decimals) ]
            title='CSTS Variables'
            rowLabels=self.project.regionNames
            top = Toplevel(self.master)
            DV.MixedDataTable(top,table,title,columnLabels=columnLabels,fmt=fmt)
    
    def createTableList(self,varNames):
        tableList = []
        varList = []
        for var in varNames:
            v = self.project.getVariable(var)
            vals = v
            if v.varType == 'CSTS':
                t = 0
                for time in v.timeString:
                    varList.append(var + ": " + time)
                    tableList.append(vals[:,t])
                    t = t+1
            else:
                varList.append(var)
                tableList.append(vals)
        tableList = Utility.TransposeList(tableList)
        return [varList, tableList]

    def listIds(self):
        self.report(self.project.listTimeIds())
        self.report(self.project.listRegionNames())

    def listMatrices(self):
        self.report("Matrices available: " + str(self.project.dataBase.matrices.keys()))

    def listData(self):
        self.listVariables()
        self.listMatrices()

    def sLag(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Spatial Lag Transformation')
        txt="""Choose a variable."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable',
                      helpText=txt)
        txt="""Choose a weights matrix for the lag."""
        entries = ['Weights Matrix']
        matNames = self.getMatrixNames() 
        sd.MultiEntry(d,matNames, entries, title='Weight Matrix',
                      helpText=txt)
        txt="Name for new rate variable."
        sd.UserEntry(d,label="New Variable Name (Optional)",helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            matName = d.results[1]['Weights Matrix']
            newName = d.results[2]
            variable = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(matName)
            result = lag(variable,w)
            varType = variable.varType
            newVariable = SVariable(result)
            newVariable.setType(varType)
            if newName == '':
                newName = varName+"_L"
            newVariable.setName(newName)
            newVariable.setRegionNames(variable.regionNames)
            newVariable.setTimeString(variable.timeString)
            self.project.dataBase.addVariable(newVariable)
            self.projectSummary()
            
    
    def logTransform(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Log Transformation')
        txt="""Choose a variable."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable',
                      helpText=txt)
        txt="Name for new rate variable."
        sd.UserEntry(d,label="New Variable Name (Optional)",helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            newName = d.results[1]
            variable = self.project.dataBase.getVariable(varName)
            result = log(variable)
            varType = variable.varType
            newVariable = SVariable(result)
            newVariable.setType(varType)
            if newName == '':
                newName = varName+"_LOG"
            newVariable.setName(newName)
            newVariable.setRegionNames(variable.regionNames)
            newVariable.setTimeString(variable.timeString)
            self.project.dataBase.addVariable(newVariable)
            self.projectSummary()

    def zTransform(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Z Transformation')
        txt="""Choose a variable."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable',
                      helpText=txt)
        txt="Name for new rate variable."
        sd.UserEntry(d,label="New Variable Name (Optional)",helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            newName = d.results[1]
            variable = self.project.dataBase.getVariable(varName)
            mx = mean(variable)
            sx = std(variable)
            xd = variable - mx
            result = xd/sx
            varType = variable.varType
            newVariable = SVariable(result)
            newVariable.setType(varType)
            if newName == '':
                newName = varName+"_Z"
            newVariable.setName(newName)
            newVariable.setRegionNames(variable.regionNames)
            newVariable.setTimeString(variable.timeString)
            self.project.dataBase.addVariable(newVariable)
            self.projectSummary()

    def transform(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('User Specified Transformation')
        txt="""Choose an X variable."""
        entries = ['Variable X']
        sd.MultiEntry(d,varNames, entries, title='Variable',
                      helpText=txt)
        txt="""Choose a Y variable."""
        entries = ['Variable Y']
        sd.MultiEntry(d,varNames, entries, title='Variable',
                      helpText=txt)
        txt="""f(X,Y) provide the function for X and Y.  E.g. X/Y or X*Y."""
        sd.UserEntry(d,label="f(X,Y)",helpText=txt)
        txt="Name for the transformed variable. A mandatory argument"
        sd.UserEntry(d,label="New Variable Name",helpText=txt)
        d.draw()
        if d.status:
            varNameX = d.results[0]['Variable X']
            varNameY = d.results[1]['Variable Y']
            function = d.results[2]
            newName = d.results[3]
            if newName == "":
                self.report("Please provide a name for your new variable!")
            else:
                X = self.project.dataBase.getVariable(varNameX)
                Y = self.project.dataBase.getVariable(varNameY)
                result = eval(function)
                newVariable = SVariable(result)
                newVariable.setType("CSTS")
                newVariable.setName(newName)
                newVariable.setRegionNames(X.regionNames)
                newVariable.setTimeString(X.timeString)
                self.project.dataBase.addVariable(newVariable)
                self.projectSummary()

    def rawRate(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Raw Rate Dialogue')
        txt="A rate is calculated on an EVENT variable and a BASE variable."
        txt+="You need to specify the names of the EVENT variable here."
        entries = ['Event']
        sd.MultiEntry(d,varNames, entries, title='Event Variable',
                      helpText=txt)
        txt="A rate is calculated on an EVENT variable and a BASE variable."
        txt+="You need to specify the names of the BASE variable here."
        entries = ['Base']
        sd.MultiEntry(d,varNames, entries, title='Base Variable',
                      helpText=txt)
        txt="Name for new rate variable."
        sd.UserEntry(d,label="New Variable Name",helpText=txt)
        d.draw()
        if d.status:
            print d.results
            eventName = d.results[0]['Event']
            baseName = d.results[1]['Base']
            event = self.project.dataBase.getVariable(eventName)
            base = self.project.dataBase.getVariable(baseName)
            sm = smooth.Smooth(event,base).smoothedRate
            rateName=d.results[2]
            v=SVariable(sm)
            v.setType("CSTS") #XXX need to check this for CS
            v.setName(rateName)
            v.setRegionNames(event.regionNames)
            v.setTimeString(event.timeString)
            self.project.dataBase.addVariable(v)
            self.projectSummary()

    def spatialRate(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Spatial Smoothed Rate Dialogue')
        txt="A rate is calculated on an EVENT variable and a BASE variable."
        txt+="You need to specify the names of the EVENT variable here."
        entries = ['Event']
        sd.MultiEntry(d,varNames, entries, title='Event Variable',
                      helpText=txt)
        txt="A rate is calculated on an EVENT variable and a BASE variable."
        txt+="You need to specify the names of the BASE variable here."
        entries = ['Base']
        sd.MultiEntry(d,varNames, entries, title='Base Variable',
                      helpText=txt)
        txt="""For Spatial smoothing you need to also specify a spatial weight
        matrix."""
        entries = ['Weight']
        matNames = self.getMatrixNames() 
        sd.MultiEntry(d,matNames, entries, title='Weight Matrix',
                      helpText=txt)
        txt="Name for new rate variable."
        sd.UserEntry(d,label="New Variable Name",helpText=txt)
        d.draw()
        if d.status:
            eventName = d.results[0]['Event']
            baseName = d.results[1]['Base']
            weightName = d.results[2]['Weight']
            event = self.project.dataBase.getVariable(eventName)
            base = self.project.dataBase.getVariable(baseName)
            weight = self.project.dataBase.getMatrix(weightName)
            sm = smooth.Smooth(event,base,weight,method='spatial').smoothedRate
            self.sm=sm
            rateName=d.results[3]
            v=SVariable(sm)
            v.setType("CSTS") #XXX need to check this for CS
            v.setName(rateName)
            v.setRegionNames(event.regionNames)
            v.setTimeString(event.timeString)
            self.project.dataBase.addVariable(v)
            self.projectSummary()

    def eBayesRate(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Empirical Bayes Rate Dialogue')
        txt="A rate is calculated on an EVENT variable and a BASE variable."
        txt+="You need to specify the names of the EVENT variable here."
        entries = ['Event']
        sd.MultiEntry(d,varNames, entries, title='Event Variable',
                      helpText=txt)
        txt="A rate is calculated on an EVENT variable and a BASE variable."
        txt+="You need to specify the names of the BASE variable here."
        entries = ['Base']
        sd.MultiEntry(d,varNames, entries, title='Base Variable',
                      helpText=txt)
        txt="Name for new rate variable."
        sd.UserEntry(d,label="New Variable Name",helpText=txt)
        d.draw()
        if d.status:
            eventName = d.results[0]['Event']
            baseName = d.results[1]['Base']
            event = self.project.dataBase.getVariable(eventName)
            base = self.project.dataBase.getVariable(baseName)
            sm = smooth.Smooth(event,base,method="bayes").smoothedRate
            rateName=d.results[2]
            v=SVariable(sm)
            v.setType("CSTS") #XXX need to check this for CS
            v.setName(rateName)
            v.setRegionNames(event.regionNames)
            v.setTimeString(event.timeString)
            self.project.dataBase.addVariable(v)
            self.projectSummary()

    def cstsVariable(self,name,values):
        var = SVariable(values)

    def deleteVariable(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Delete Variable')
        txt="""Choose a variable to delete from the project."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable',
                      helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            y = self.project.dataBase.getVariable(varName)
            self.project.dataBase.deleteVariable(y)
            self.projectSummary()
            
    ######################################## 
    # matrix  callbacks
    ######################################## 
    
    def listMatrix(self):
        wNames = self.getMatrixNames()
        d = sd.SDialogue("List Matrix Values")
        txt="""Choose a matrix to list."""
        entries = ['Matrix']
        sd.MultiEntry(d,wNames, entries, title='Matrix',
                      helpText=txt)
        
        values = range(5,9) 
        txt = """Choose the format for the matrix values."""
        sd.SpinEntry(d,title="Additional Options",label="Format",
                     values=values,helpText=txt)
        values = range(0,5)
        txt = """Choose the number of decimals for the matrix values."""
        sd.SpinEntry(d,title="Additional Options",label="Decimals",
                     values=values,helpText=txt)
        d.draw()
        if d.status:
            wname = d.results[0]['Matrix']
            format = int(d.results[1])
            dec = int(d.results[2])
            fmt = [ format,dec ]
            w = self.project.dataBase.getMatrix(wname)
            wf = w.full()
            n,k = shape(wf)
            rn = range(n)
            csids = [ (i,j) for i in rn for j in rn]
            tsids = [ [] for i in rn for j in rn]
            var = [ [] for i in rn for j in rn]
            top = Toplevel(self.master)
            rowLabels = self.project.regionNames
            columnLabels = self.project.regionNames
            STable(wname,top,self.project,
                    wf,var,tsids,csids,rowLabels,columnLabels,fmt=fmt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            wname = d.results[1]
            if wname == '':
                wname = "W_"+varName

    def distanceMatrix(self):
        d = sd.SDialogue("Inverse Distance Matrix Creation")
        txt="Provide a new name for your regime based matrix."
        sd.UserEntry(d,label="New Matrix Name (Optional)",helpText=txt)
        
        values = arange(.25,2.25,.25)
        txt = """Choose the value for the exponent."""
        sd.SpinEntry(d,title="Additional Options",label="Power",
                     values=values,helpText=txt)
        
        d.draw()
        if d.status: 
            wname = d.results[0]
            exp = d.results[1]
            if wname == '':
                wname = "distance_"+exp
            power = eval(exp)
            if not hasattr(self.project,"distMatOn"):
                self.createDistanceMatrix()
            iw = self.invertMatrix(power)
            mat = fMatrix(iw)
            mat.setName(wname)
            self.project.dataBase.addMatrix(mat)
            self.listMatrices() 

    def createDistanceMatrix(self):
        self.project.distMatOn = 1
        cs2poly = self.project.cs2poly
        cs2polykeys = cs2poly.keys()
        cs2polykeys.sort()
        xvar = []
        yvar = []
        for csKey in cs2polykeys:
            centroid = self.project.centroids[csKey]
            xvar.append(centroid[0])
            yvar.append(centroid[1])

        maxy = max(yvar)
        yvar = [maxy - y for y in yvar]
        n = len(cs2polykeys)
        x = SVariable(cs(xvar,n,1))
        x.setType("CS")
        x.setName("x")
        x.setRegionNames(self.project.regionNames)
        x.setTimeString(self.project.timeString)
        y = SVariable(cs(yvar,n,1))
        y.setType("CS")
        y.setName("y")
        y.setRegionNames(self.project.regionNames)
        y.setTimeString(self.project.timeString)
        self.project.dataBase.addVariable(x)
        self.project.dataBase.addVariable(y)
        dmat = zeros((n,n),Float)
        mat = DistanceMatrix(x,y)
        mat.setName("distanceMatrix")
        self.project.dataBase.addMatrix(mat)        

    def invertMatrix(self,power):
        # construct inverse distance matrix
        dmat = self.project.dataBase.getMatrix("distanceMatrix").full()
        n,k = shape(dmat)
        d0 = diag(ones(n))
        d1 = dmat + d0
        d2 = 1./((d1)**power)
        mat = d2 - d0
        # row standardize
        rs = sum(transpose(mat))
        rsd = rs + (rs==0)
        mat = matrixmultiply(diag(1./rsd),mat)
        return mat

    def regimeMatrix(self):
        varNames = self.get_CS_variable_names()
        d = sd.SDialogue("Regime Matrix Creation")
        txt="""Choose a regime variable."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Regime Variable',
                      helpText=txt)
        txt="Provide a new name for your regime based matrix."
        sd.UserEntry(d,label="New Matrix Name (Optional)",helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            wname = d.results[1]
            if wname == '':
                wname = "W_"+varName
            y = self.project.dataBase.getVariable(varName)        
            w = spRegionMatrix(y)
            w.setName(wname)
            self.project.dataBase.addMatrix(w)
            self.listMatrices()

    def gabriel(self):
        if not hasattr(self.project,"distMatOn"):
            self.createDistanceMatrix()
        y = self.project.gabrielGraph()
        self.listMatrices()
        
    def relativeProximity(self):
        if not hasattr(self.project,"distMatOn"):
            self.createDistanceMatrix()
        y = self.project.relativeProximity()
        self.listMatrices()

    def sphereOfInfluence(self):
        if not hasattr(self.project,"distMatOn"):
            self.createDistanceMatrix()
        y = self.project.sphereOfInfluence()
        self.listMatrices()

    def gis2Gal(self):
        # creates a contiguity matrix based on polygon vertices/edges
        coords = self.project.coords
        poly2cs = self.project.poly2cs
        cs2poly = self.project.cs2poly
        gal = self.project.gis2Contiguity(coords,poly2cs,cs2poly)
        if gal:
            mat = spMatrix("Joins")
            mat.dict = gal
            self.project.dataBase.addMatrix(mat)
            self.listMatrices()
        else:
            self.report("GIS file contains islands, no join matrix created")

    def covarMatrix(self):
        varNames = self.get_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Covariance Matrix Creation")
        txt="""Choose a variable."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable',
                      helpText=txt)
        txt="Provide a name for your covariance matrix (optional)."
        sd.UserEntry(d,label="New Matrix Name (Optional)",helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            newName = d.results[1]
            y = self.project.dataBase.getVariable(varName)       
            if newName == '':
                newName = y.name+"_CV"
            cmat = CorrMatrix(y)
            cmat.setName(newName)
            self.project.dataBase.addMatrix(cmat)
            self.listMatrices()
            
    def spatialMultiplier(self):
        wNames = self.getMatrixNames()
        d = sd.SDialogue("Create Spatial Multiplier")
        txt="""Choose a spatial weights matrix."""
        entries = ['Matrix']
        sd.MultiEntry(d,wNames, entries, title='Matrix', helpText=txt)

        values = arange(-.9,1,.1)
        txt="""Choose a value for the spatial autoregressive parameter (rho)."""
        sd.SpinEntry(d,title="Additional Options",label="rho",
                     values=values,helpText=txt)        
        
        graphTypes = ['Map']
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            wname = d.results[0]['Matrix']
            w = self.project.dataBase.getMatrix(wname)        
            self.report(w.name)
            rho = eval(d.results[1])
            wf = w.full()
            n = shape(wf)[0]
            A = inverse(eye(n) - rho * wf)
            multiplier = sum(A)
            n = shape(multiplier)[0]
            multiplier = reshape(multiplier,(n,1))
            multiplier = SVariable(multiplier)
            multiplier.setType("CS")
            multiplier.setName(w.name+"_SM")
            multiplier.setRegionNames(self.project.regionNames)
            multiplier.setTimeString(self.project.timeString[0])
            self.project.dataBase.addVariable(multiplier)
            self.projectSummary()
            A = A.tolist() # make array continguous
            A = array(A) #  
            mat = fMatrix(A)
            mat.setName(w.name+"_SM")
            self.project.dataBase.addMatrix(mat)
            graph_options = d.results[2]

            if sum([ x[1] for x in graph_options]):
                varName = w.name+"_SM"
                timePeriod = 0
                name = "%s %s"%("Spatial Multiplier for", wname)
            
                if graph_options[0][1]:
                    coords = self.project.coords
                    poly2cs = self.project.poly2cs
                    cs2poly = self.project.cs2poly
                    self.drawMap(name,coords,multiplier[:,0],multiplier.name,timePeriod,
                                 poly2cs,cs2poly)

    def weightCharacteristics(self):
        wNames = self.getMatrixNames()
        d = sd.SDialogue("Matrix Characteristics")
        txt="""Choose a matrix to describe."""
        entries = ['Matrix']
        sd.MultiEntry(d,wNames, entries, title='Matrix',
                      helpText=txt)

        d.draw()
        if d.status:
            wName = d.results[0]['Matrix']
            w = self.project.dataBase.getMatrix(wName)
            self.w=w
            id=w.dict.keys()
            id.sort()
            nneigh = [ w.dict[i][0] for i in id]
            maxn=max(nneigh)
            neighborCount = SVariable(nneigh)
            neighborCount.setType('CS')
            neighborCount.setName(w.name+"_Count")
            neighborCount.setTimeString(self.project.timeString[0])
            self.project.dataBase.addVariable(neighborCount)
            variable=neighborCount
            timeStrings = self.project.timeString
            timePeriodString="Histogram %s %s"%(variable.name,timeStrings[0])
            bins = range(maxn+1)
            h=SHistogram(timePeriodString,self.master, variable.name,
                         variable,
                         self.project,
                         variable,
                         [],
                         title=variable.name+" "+timeStrings[0],
                         xLabel=variable.name+" "+timeStrings[0],
                         csIds = range(variable.n),
                         tsIds=0,
                         classification="userDefined",
                         bins=bins)

    def deleteMatrix(self):
        wNames = self.getMatrixNames()
        d = sd.SDialogue('Delete Matrix')
        txt="""Choose a matrix to delete from the project."""
        entries = ['Matrix']
        sd.MultiEntry(d,wNames, entries, title='Matrix',
                      helpText=txt)
        
        d.draw()
        if d.status:
            wName = d.results[0]['Matrix']
            w = self.project.dataBase.getMatrix(wName)
            self.project.dataBase.deleteMatrix(w)
            self.projectSummary()


    ######################################## 
    # eda callbacks
    ######################################## 

    def dscs(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Cross-Sectional Summary Dialogue')
        txt="""Provides summary statistics for the variable selected across
        the cross-sections for each time period.  Works for a pure
        cross-sectional variable as well."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to Summarize',
                      helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            results = eda.Summary(variable)
            values = results.results.tolist()
            mxx = max(max(values))
            sl = len("%.3f"%mxx) + 1
            fmt = [sl,3]
            columnLabels = results.colNames
            if variable.varType == "CSTS":
                rowLabels = variable.timeString
            else:
                rowLabels = [varName]
            name ="Summary by CS %s"%(varName)
            top = Toplevel(self.master)
            DV.MixedDataTable(top,values,name,
                              columnLabels=columnLabels,rowLabels=rowLabels,
                              fmt=fmt)        
                

    def dsts(self):
        import sdialogue as sd
        varNames = self.get_TS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue('Time-Series Summary Dialogue')
        txt="""Provides the summary statistics for the variable selected
        across time for each cross-section."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to Summarize',
                      helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            if variable.varType == "CSTS":
                results = eda.Summary(transpose(variable))
                rowLabels = variable.regionNames
            else:
                results = eda.Summary(variable)
                rowLabels = [varName]
            values = results.results.tolist()
            mxx = max(max(values))
            sl = len("%.3f"%mxx) + 1
            fmt = [sl,3]
            columnLabels = results.colNames
            name ="Summary by TS %s"%(varName)
            top = Toplevel(self.master)
            DV.MixedDataTable(top,values,name,
                              columnLabels=columnLabels,rowLabels=rowLabels,
                              fmt=fmt)    
                

    def dspool(self):
        import sdialogue as sd
        varNames = self.get_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue('Pooled Summary Dialogue')
        txt="""Provides the summary statistics for the variable selected
        by pooling the data."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to Summarize',
                      helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            if variable.varType == "CSTS":
                n = variable.n
                k = variable.t
                v = reshape(variable,(n*k,1))
                results = eda.Summary(v)
                values = results.results.tolist()
                mxx = max(max(values))
                sl = len("%.3f"%mxx) + 1
                fmt = [sl,3]
                columnLabels = results.colNames
                rowLabels = [varName]
                name ="Summary by CSTS %s"%(varName)
                top = Toplevel(self.master)
                DV.MixedDataTable(top,values,name,
                                  columnLabels=columnLabels,rowLabels=rowLabels,
                                  fmt=fmt)       

    def ddcs(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Cross-Sectional Distribution Summary Dialogue')
        txt="""Provides a distribution summary for the variable selected across
        the cross-sections for each time period.  Works for a pure
        cross-sectional variable as well."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to Summarize',
                      helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            results = eda.Dist(variable)
            values = results.results.tolist()
            mxx = max(max(values))
            sl = len("%.3f"%mxx) + 1
            fmt = [sl,3]
            columnLabels = results.colNames
            if variable.varType == "CSTS":
                rowLabels = variable.timeString
            else:
                rowLabels = [varName]
            name ="Summary by CS %s"%(varName)
            top = Toplevel(self.master)
            DV.MixedDataTable(top,values,name,
                              columnLabels=columnLabels,rowLabels=rowLabels,
                              fmt=fmt)
            
    def ddts(self):
        import sdialogue as sd
        varNames = self.get_TS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue('Time-Series Distribution Summary Dialogue')
        txt="""Provides a distribution summary for the variable selected
        across time for each cross-section.  Works for pure time-series
        variables as well."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to Summarize',
                      helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            if variable.varType == "CSTS":
                results = eda.Dist(transpose(variable))
                rowLabels = variable.regionNames
            else:
                results = eda.Dist(variable)
                rowLabels = [varName]
            values = results.results.tolist()
            mxx = max(max(values))
            sl = len("%.3f"%mxx) + 1
            fmt = [sl,3]
            columnLabels = results.colNames
            name ="Summary by TS %s"%(varName)
            top = Toplevel(self.master)
            DV.MixedDataTable(top,values,name,
                              columnLabels=columnLabels,rowLabels=rowLabels,
                              fmt=fmt)
            
    def ddpool(self):
        import sdialogue as sd
        varNames = self.get_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue('Pooled Distribution Summary Dialogue')
        txt="""Provides a distribution summary for the variable selected
        by pooling the data."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to Summarize',
                      helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            n = variable.n
            k = variable.t
            v = reshape(variable,(n*k,1))
            results = eda.Dist(v)
            values = results.results.tolist()
            mxx = max(max(values))
            sl = len("%.3f"%mxx) + 1
            fmt = [sl,3]
            columnLabels = results.colNames
            rowLabels = [varName]
            name ="Summary by CSTS %s"%(varName)
            top = Toplevel(self.master)
            DV.MixedDataTable(top,values,name,
                              columnLabels=columnLabels,rowLabels=rowLabels,
                              fmt=fmt)
                

    ######################################## 
    # Esda callbacks
    ######################################## 
    def moran(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Global Moran's I")
        txt="""Computes Global Moran's I for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)

        types = ["Normality", "Randomization"]
        txt = """Choose a method for calculating the variance of the Global
        Moran's statistic.  Default = Normality"""
        sd.RadioButtons(d, title='Inference', label='Variance', values=types,
                        helpText=txt)

        values=[0,99,999,999,9999]
        txt = """Choose the number of permutations to use for inference."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)        
        
        graphTypes = 'Map','Scatter','Time Series','Box Plot'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)
        
        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            matrixName = d.results[1]['Matrix']
            variance = d.results[2]
            perms = d.results[3]
            variable = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(matrixName)
            permutations = int(perms)
            if permutations > 0:
                txt="Running %d permutations, please wait."%permutations
                qd=sd.Warning(self.master,txt)
                m = Esda.Moran(variable,w,permutations,variance)
                qd.destroy()
            else:
                m = Esda.Moran(variable,w,permutations,variance)
            self.report(m.report())
            varName = varName


            # do graphs 
            graph_options = d.results[4]

            if sum([ x[1] for x in graph_options]):
                csLabels = variable.regionNames
                varName = varName
                timeStrings = variable.timeString
                t=0
                timePeriodString = "Spatial Lag %s %s"%(varName,timeStrings[t])
                yLabel = timePeriodString
                xLabel = "%s %s"%(varName,timeStrings[t])
                name = "%s %s"%(varName,timeStrings[t])
                y=variable[:,0]
                timePeriod = 0
            
                if graph_options[0][1]:
                    coords = self.project.coords
                    poly2cs = self.project.poly2cs
                    cs2poly = self.project.cs2poly
                    self.drawMap(name,coords,variable[:,0],varName,timePeriod,
                                 poly2cs,cs2poly)

                if graph_options[1][1]:
                    ylag = array(m.ylag)
                    varLag=ylag[:,0]
                    name = "Moran Lag"
                    ycsts = variable 
                    x=variable[:,0]
                    y=varLag
                    allX = ycsts
                    allLag = ylag
                    p = SMoranScatter(timePeriodString,self.master,self.project,
                            allX,allLag,x,varLag,varName=varName,
                            variableX=varName,
                            variableY=varName+"Spatial Lag",
                            xLabel=xLabel,
                            yLabel=yLabel,
                            t=t,
                            xPop="Variable",yPop="Spatial Lag")

                if graph_options[2][1] and variable.varType=="CSTS":
                    mi = m.mi.tolist()
                    y =mi
                    timeDict={'Type':None}
                    x=self.project.timeClass.numeric
                    csIds = range(len(x))
                    moranVarName = "Moran's I Value"
                    ts = STimeSeries(varName,
                                 self.project,
                                 self.master,
                                 x,
                                 y,
                                 varName,
                                 csIds,
                                 'I',
                                 yPop="Moran's I Value",
                                 yLabel="Moran's I")

                if graph_options[3][1]:
                    x = variable[:,0]
                    b = SBoxPlot(varName,self.project,self.master,
                                  x=x,
                                  csids = range(len(x)),
                                  tsids = [0],
                                  allX=variable)
                    
    def localMoran(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Local Moran's I")
        txt="""Computes Local Moran's I for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)

        values=[0,99,999,999,9999]
        txt = """Choose the number of permutations to use for inference."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)        
        
        graphTypes = 'Regime Map','Local I Map','Box Plot I','Density I'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)
        
        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            matrixName = d.results[1]['Matrix']
            perms = d.results[2]
            y = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(matrixName)
            permutations = int(perms)

            if permutations > 0:
                txt="Running %d permutations, please wait."%permutations
                qd=sd.Warning(self.master,txt)
                results = Esda.LocalMoran(y,w,permutations)
                qd.destroy()
            else:
                results = Esda.LocalMoran(y,w,permutations)
            self.report(results.report())
            variable = SVariable(results.dvalue)
            variable.setType("CSTS")
            variable.setName(y.name+"_D")
            variable.setRegionNames(y.regionNames)
            variable.setTimeString(y.timeString)
            self.project.dataBase.addVariable(variable)
            variableI = SVariable(results.mi)
            variableI.setType("CSTS")
            variableI.setName(y.name+"_I")
            variableI.setRegionNames(y.regionNames)
            variableI.setTimeString(y.timeString)
            self.project.dataBase.addVariable(variableI)

            graph_options = d.results[3]
            if sum([ x[1] for x in graph_options]):
                coords = self.project.coords
                poly2cs = self.project.poly2cs
                cs2poly = self.project.cs2poly
                bins = range(1,5,1)
                timePeriod=0

                if graph_options[0][1]:
                    self.drawMap("Local Regime (Quadrant)",coords,variable[:,0],
                            variable.name,timePeriod,
                            poly2cs,cs2poly,classification="uniqueValues",
                            bins=bins,nBins=4,legendType="qualitative")

                if graph_options[1][1]:
                    self.drawMap("Local I",coords,variableI[:,0],
                            variableI.name,timePeriod,
                            poly2cs,cs2poly,classification="percentiles",
                            bins=bins,nBins=5,legendType="sequential")

                if graph_options[2][1]:
                    x = variableI[:,0]
                    bp = SBoxPlot(variableI.name,self.project,self.master,
                            x=x,
                            csids = range(len(x)),
                            tsids = [0],
                            allX = variableI)
                if graph_options[3][1]:
                    x = variableI[:,0]
                    title="Density %s"%variableI.name
                    tsids = [0] * len(x)
                    dp = SDensity(variableI.name,self.master,self.project,
                            variableI.name,x,csid=range(len(x)),
                            tsid=tsids,title=title,xLabel=variableI.name)


    def geary(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Geary's C")
        txt="""Computes Global Geary's C for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)

        values=[0,99,999,999,9999]
        txt = """Choose the number of permutations to use for inference."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)        
        
        graphTypes = 'Map','Time Series C', 'Time Series p-value'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            matrixName = d.results[1]['Matrix']
            perms = d.results[2]
            y = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(matrixName)
            permutations = int(perms)
            if permutations > 0:
                txt="Running %d permutations, please wait."%permutations
                qd=sd.Warning(self.master,txt)
                results = Esda.Geary(y,w,permutations)
                qd.destroy()
            else:
                results = Esda.Geary(y,w,permutations)
            self.report(results.report())
            variable = y

            graph_options = d.results[3]
            if sum([ x[1] for x in graph_options]): 
                    csLabels = variable.regionNames
                    timeStrings = variable.timeString
                    t=0
                    timePeriodString = "Spatial Lag %s %s"%(varName,timeStrings[t])
                    yLabel = timePeriodString
                    xLabel = "%s %s"%(varName,timeStrings[t])
                    name = "%s %s"%(varName,timeStrings[t])
                    y=variable[:,0]
                    timePeriod = 0
            
                    if graph_options[0][1]:
                        coords = self.project.coords
                        poly2cs = self.project.poly2cs
                        cs2poly = self.project.cs2poly
                        self.drawMap(name,coords,variable[:,0],varName,timePeriod,
                                    poly2cs,cs2poly)

                    if graph_options[1][1] and variable.varType=="CSTS":
                        y = results.gc
                        timeDict={'Type':None}
                        x=self.project.timeClass.numeric
                        csIds = range(len(x))
                        ts = STimeSeries(varName,self.project,self.master,
                                        x,y,varName,csIds,'C',yPop="C Value",
                                        yLabel="Geary's C")


                    if graph_options[2][1] and variable.varType=="CSTS":
                        y = results.zpvalue
                        timeDict={'Type':None}
                        x=self.project.timeClass.numeric
                        csIds = range(len(x))
                        varName = varName+"_pvalue"
                        ts = STimeSeries(varName, self.project, self.master,
                                 x, y, varName, csIds, 'C', yPop="C p-value",
                                 yLabel="Geary's C p-value")
                        
                        if results.permutations:
                            y = results.ppvalue
                            n = shape(y)[1]
                            y = reshape(y,(n,))
                            timeDict={'Type':None}
                            x=self.project.timeClass.numeric
                            csIds = range(len(x))
                            varName = varName+"_ppvalue"
                            ts = STimeSeries(varName, self.project, self.master,
                                     x, y, varName, csIds, 'C', yPop="C p-value (permutation)",
                                     yLabel="Geary's C p-value (permutation)")


    def localGeary(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Local Geary's C")
        txt="""Computes Local Geary's C for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)

        values=[0,99,999,999,9999]
        txt = """Choose the number of permutations to use for inference."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)        
        
        graphTypes = 'Map','Local C Map', 'Local C Density'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            matrixName = d.results[1]['Matrix']
            perms = d.results[2]
            y = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(matrixName)
            permutations = int(perms)
            if permutations > 0:
                txt="Running %d permutations, please wait."%permutations
                qd=sd.Warning(self.master,txt)
                results = Esda.LocalGeary(y,w,permutations)
                qd.destroy()
            else:
                results = Esda.LocalGeary(y,w,permutations)
            self.report(results.report())
            variable = y

            variable = SVariable(results.ci)
            variable.setType("CSTS")
            variable.setName(y.name+"_CI")
            variable.setRegionNames(y.regionNames)
            variable.setTimeString(y.timeString)
            self.project.dataBase.addVariable(variable)
            ci = variable
            variable = y
            
            graph_options = d.results[3]
            if sum([ x[1] for x in graph_options]):
                csLabels = variable.regionNames
                varName = variable.name
                timeStrings = variable.timeString
                t=0
                timePeriod=t
                if graph_options[0][1]:
                    name = "%s %s"%(varName,timeStrings[0])
                    coords = self.project.coords
                    poly2cs = self.project.poly2cs
                    cs2poly = self.project.cs2poly
                    self.drawMap(name,coords,variable[:,0],varName,timePeriod,
                                 poly2cs,cs2poly)
                if graph_options[1][1]:
                    variable=ci
                    varName = variable.name
                    name = "Local Geary %s %s"%(varName,timeStrings[0])
                    coords = self.project.coords
                    poly2cs = self.project.poly2cs
                    cs2poly = self.project.cs2poly
                    self.drawMap(name,coords,variable[:,0],varName,timePeriod,
                                 poly2cs,cs2poly)
                if graph_options[2][1]:
                    variable = ci
                    x = variable[:,0]
                    title="Density %s"%variable.name
                    tsids = [0] * len(x)
                    dp = SDensity(variable.name,self.master,self.project,
                            variable.name,x,csid=range(len(x)),
                            tsid=tsids,title=title,xLabel=variable.name)


    def globalG(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Global G Statistic for Spatial Association")
        txt="""Computes the Global G Statistic for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)

        values=[0,99,999,999,9999]
        txt = """Choose the number of permutations to use for inference."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)        
        
        graphTypes = 'Map','Time Series C', 'Time Series p-value'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            matrixName = d.results[1]['Matrix']
            perms = d.results[2]
            y = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(matrixName)
            permutations = int(perms)
            if permutations > 0:
                txt="Running %d permutations, please wait."%permutations
                qd=sd.Warning(self.master,txt)
                results = Esda.GlobalG(y,w,permutations)
                qd.destroy()
            else:
                results = Esda.GlobalG(y,w,permutations)
            self.report(results.report())
            variable = y

            graph_options = d.results[3]
            if sum([ x[1] for x in graph_options]): 
                    csLabels = variable.regionNames
                    timeStrings = variable.timeString
                    t=0
                    name = "%s %s"%(varName,timeStrings[t])
                    y=variable[:,0]
                    timePeriod = 0
                
                    if graph_options[0][1]:
                        coords = self.project.coords
                        poly2cs = self.project.poly2cs
                        cs2poly = self.project.cs2poly
                        self.drawMap(name,coords,variable[:,0],varName,timePeriod,
                                     poly2cs,cs2poly)

                    if graph_options[1][1] and variable.varType=="CSTS":
                        y = results.g
                        timeDict={'Type':None}
                        x=self.project.timeClass.numeric
                        csIds = range(len(x))
                        ts = STimeSeries(varName, self.project, self.master,
                                     x, y, varName, csIds, 'G', yPop="G Value",
                                     yLabel="Global G")
                        
                    if graph_options[2][1] and variable.varType=="CSTS":
                        y = results.pG
                        timeDict={'Type':None}
                        x=self.project.timeClass.numeric
                        csIds = range(len(x))
                        ts = STimeSeries(varName, self.project, self.master, 
                                     x, y, varName, csIds, 'G', yPop="G p-value",
                                     yLabel="Global G p-value")
                        
                        if results.permutations:
                            y = results.ppermZ
                            ts = STimeSeries(varName, self.project, self.master,
                                     x, y, varName, csIds, 'G', yPop="G p-value (permutation)",
                                     yLabel="Global G p-value (permutation)")
            

    def localG(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Local G Statistic for Spatial Association")
        txt="""Computes the Global G Statistic for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)

        values=[0,99,999,999,9999]
        txt = """Choose the number of permutations to use for inference."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)    

        values=[0,1]
        txt = """A Boolean argument where 0 indicates that the observation in
        question is not included as part of its cluster in the statistical
        analysis."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)          
        
        graphTypes = 'Map','Local G Map', 'Local G Density'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            wName = d.results[1]['Matrix']
            permutations = int(d.results[2])
            star = int(d.results[3])
            variable = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(wName)
            self.report("")
            self.report("Running Local G")
            self.report("Variable: " + varName)
            self.report("Weights Matrix: " + wName)
            self.report("Permutations: " + str(permutations))
            self.report("Local G values for each time period:")
            
            if permutations > 0:
                txt="Running %d permutations, please wait."%permutations
                qd=sd.Warning(self.master,txt)
                results = Esda.LocalG(variable,w,star=star,permutations=permutations)
                qd.destroy()
                self.report(str(results.gi))
                self.report("Psuedo-pvalues")
                self.report(str(results.mcp))               
            else:
                results = Esda.LocalG(variable,w,star=star,permutations=permutations)
                self.report(str(results.gi))
            self.report("")    

            variableGI = SVariable(results.gi)
            variableGI.setType("CSTS")
            variableGI.setName(variable.name+"_GI")
            variableGI.setRegionNames(variable.regionNames)
            variableGI.setTimeString(variable.timeString)
            self.project.dataBase.addVariable(variableGI)

            graph_options = d.results[4]
            if sum([ x[1] for x in graph_options]):
                csLabels = variable.regionNames
                varName = variable.name
                timeStrings = variable.timeString
                t=0
                timePeriod=t
                if graph_options[0][1]:
                    name = "%s %s"%(varName,timeStrings[0])
                    coords = self.project.coords
                    poly2cs = self.project.poly2cs
                    cs2poly = self.project.cs2poly
                    self.drawMap(name,coords,variable[:,0],varName,timePeriod,
                                 poly2cs,cs2poly)

                if graph_options[1][1]:
                    varName = variableGI.name
                    name = "Local G %s %s"%(variable.name,timeStrings[0])
                    coords = self.project.coords
                    poly2cs = self.project.poly2cs
                    cs2poly = self.project.cs2poly
                    self.drawMap(name,coords,variableGI[:,0],varName,timePeriod,
                                 poly2cs,cs2poly)
                    
                if graph_options[2][1]:
                    x = variableGI[:,0]
                    title="Density %s"%variableGI.name
                    tsids = [0] * len(x)
                    dp = SDensity(variableGI.name,self.master,self.project,
                            variableGI.name,x,csid=range(len(x)),
                            tsid=tsids,title=title,xLabel=variableGI.name)            

    def traceTest(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Trace Test")
        txt="""Computes a Trace Test for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)

        values=[0,99,999,999,9999]
        txt = """Choose the number of permutations to use for inference."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)        
        
        graphTypes = 'Trace','Nondiagonality','pvalue','Map'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            matName = d.results[1]['Matrix']
            permutations = int(d.results[2])
            self.report("")
            y = self.project.dataBase.getVariable(varName)            
            variable = y
            w = self.project.dataBase.getMatrix(matName)
            n = y.n
            if permutations > 0:
                txt="Running %d permutations, please wait."%permutations
                qd=sd.Warning(self.master,txt)
                results = Esda.TraceTest(y,w,permutations=permutations)
                qd.destroy()
            else:
                results = Esda.TraceTest(y,w,permutations=permutations)
            self.report(results.report())

            graph_options = d.results[3]
            if graph_options[0][1]:
                y = results.traces
                x = self.project.timeClass.numeric
                csIds = range(len(x))
                ts = STimeSeries(varName, self.project, self.master,
                    x, y, varName, csIds, 'Trace', yPop='Trace value',
                    yLabel="Trace value")
                
            if graph_options[1][1]:
                y = results.traces
                x = self.project.timeClass.numeric
                csIds = range(len(x))
                n=n/1.
                y = [1.-a/n for a in y]
                csIds = range(len(x))
                ts = STimeSeries(varName, self.project, self.master,
                    x, y, varName, csIds, 'Nondiagonality', yPop='Nondiagonality',
                    yLabel="Nondiagonality")
            
            if graph_options[2][1] and results.permutations:
                y = results.pvalue
                x = self.project.timeClass.numeric
                csIds = range(len(x))
                n=n/1.
                csIds = range(len(x))
                ts = STimeSeries(varName, self.project, self.master,
                    x, y, varName, csIds, 'Trace pvalue', yPop='Trace pvalue',
                    yLabel="Trace pvalue")
            
            if graph_options[3][1]:
                coords = self.project.coords
                poly2cs = self.project.poly2cs
                cs2poly = self.project.cs2poly
                timePeriod=0
                self.drawMap(varName,coords,variable[:,0],varName,timePeriod,
                             poly2cs,cs2poly)        



    ######################################## 
    # Inequality Callbacks
    ######################################## 

    def gini(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Gini Coefficient")
        txt="""Computes the Gini Coefficient for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        graphTypes = 'Map','Time Series','Box Plot'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable']         
            variable = self.project.dataBase.getVariable(varName)
            results = Inequality.Gini(variable)
            self.report(results.report())
    
            graph_options = d.results[1]
            if sum([ x[1] for x in graph_options]):
                csLabels = variable.regionNames
                timeStrings = variable.timeString
                t=0
                name = "%s %s"%(varName,timeStrings[t])
                y=variable[:,0]
                timePeriod = 0
            
                if graph_options[0][1]:   
                    coords = self.project.coords
                    poly2cs = self.project.poly2cs
                    cs2poly = self.project.cs2poly
                    self.drawMap(name,coords,variable[:,0],varName,timePeriod,
                               poly2cs,cs2poly)

                if graph_options[1][1]:
                    y = results.gini.tolist()
                    timeDict={'Type':None}
                    x = self.project.timeClass.numeric
                    csIds = range(len(x))
                    giniVarName = "Gini's Value"
                    ts = STimeSeries(varName, self.project, self.master,
                               x, y, varName, csIds, 'I', yPop="Gini's I Value",
                               yLabel="Gini's I")


                if graph_options[2][1]:              
                    x = variable[:,0]
                    b = SBoxPlot(varName,self.project,self.master,
                                x=x, csids = range(len(x)), tsids = [0], 
                                allX=variable)
 
    def ginis(self): 
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Spatial Gini")
        txt="""Computes the Spatial Gini Coefficient for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)

        values=[0,99,999,999,9999]
        txt = """Choose the number of permutations to use for inference."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)        
        
        graphTypes = 'Map','Time Series','Box Plot'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            matrixName = d.results[1]['Matrix']
            permutations = int(d.results[2])
            variable = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(matrixName)  
            y = variable
            
            if permutations > 0:
                txt="Running %d permutations, please wait."%permutations
                qd=sd.Warning(self.master,txt)
                results = Inequality.GiniS(y,w,permutations)
                qd.destroy()
            else:
                results = Inequality.GiniS(y,w,permutations)
            self.report(results.report())    

            graph_options = d.results[3]
            if sum([ x[1] for x in graph_options]):
                csLabels = variable.regionNames
                timeStrings = variable.timeString
                t=0
                name = "%s %s"%(varName,timeStrings[t])
                y=variable[:,0]
                timePeriod = 0
          
                if graph_options[0][1]:   
                    coords = self.project.coords
                    poly2cs = self.project.poly2cs
                    cs2poly = self.project.cs2poly
                    self.drawMap(name,coords,variable[:,0],varName,timePeriod,
                                 poly2cs,cs2poly)

                if graph_options[1][1]:
                    y = results.gini.tolist()
                    timeDict={'Type':None}
                    x = self.project.timeClass.numeric
                    csIds = range(len(x))
                    giniVarName = "Spatial Gini's Value"
                    ts = STimeSeries(varName, self.project, self.master,
                              x, y, varName, csIds, 'I', yPop="Spatial Gini's  Value",
                              yLabel="Spatial Gini's")

                if graph_options[2][1]:              
                    x= variable[:,0]
                    b = SBoxPlot(varName,self.project,self.master,
                                  x=x, csids = range(len(x)), tsids = [0],
                                  allX=variable)            


    def theil(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Theil's T")
        txt="""Computes Theil's T for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        graphTypes = ['Time Series']
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            thRes = Inequality.Theil(variable)
            self.report(thRes.T)
            graph_options = d.results[1]
            if sum([ x[1] for x in graph_options]): 
                timeStrings = variable.timeString
                t=0
                name = "%s %s"%(varName,timeStrings[t])
                y=variable[:,0]
                timePeriod = 0
                if graph_options[0][1] and variable.varType=="CSTS":
                    y = thRes.T
                    timeDict={'Type':None}
                    x=self.project.timeClass.numeric
                    csIds = range(len(x))
                    ts = STimeSeries(varName, self.project, self.master, 
                                     x, y, varName, csIds, 'Theil', yPop="Theil Value", 
				                     yLabel="Global Theil")
            
        
    def theild(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        regimeNames = self.get_CS_variable_names()
        d = sd.SDialogue("Theil Decomposition")
        txt="""Decomposes the Theil's T Coefficient by regime for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        entries = ['Regime']
        txt="""Choose a regime variable."""
        sd.MultiEntry(d,regimeNames, entries, title='Choose a Regime Variable',
                      helpText=txt)

        values=[0,99,999,999,9999]
        txt = """Choose the number of permutations to use for inference."""
        sd.SpinEntry(d,title="Additional Options",label="Permutations",
                     values=values,helpText=txt)        
        
        graphTypes = 'Map','Box plot','Interregional','Intraregional'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            regime_name = d.results[1]['Regime']
            permutations = int(d.results[2])
            variable = self.project.dataBase.getVariable(varName)
            regime = self.project.getVariable(regime_name)
            
            if permutations > 0:
                txt="Running %d permutations, please wait."%permutations
                qd=sd.Warning(self.master,txt)
                results = Inequality.TheilDSim(variable,regime,realizations=permutations)
                qd.destroy()
            else:
                results = Inequality.TheilD(variable,regime)
            self.report(results.report())    
            
            graph_options = d.results[3]            
            if sum([ x[1] for x in graph_options]):
                csLabels = variable.regionNames
                timeStrings = variable.timeString
                t=0
                name = "%s %s"%(varName,timeStrings[t])
                y=variable[:,0]
                timePeriod = 0
          
                if graph_options[0][1]:   
                    coords = self.project.coords
                    poly2cs = self.project.poly2cs
                    cs2poly = self.project.cs2poly
                    self.drawMap(name,coords,variable[:,0],varName,timePeriod,
                                 poly2cs,cs2poly)

                if graph_options[2][1]:
                      bg = results.BG/results.T
                      title = "Interregional Inequality: %s, Partition: %s"%(variable.name,regime.name)
                      csIds = range(variable.n)
                      tsIds = range(variable.t)

                      x=self.project.timeClass.numeric
                      ts = TimeSeries(title,self.master,x=x,y=bg,
                           title = title, xLabel = "Time",
                           yLabel = "Interregional\n Inequality %",
                           csIds = csIds)

                      ts.top.title(title)
                
                if graph_options[3][1]:
                     
                      wg = results.WG/results.T
                      title = "Intraregional Inequality: %s, Partition: %s"%(variable.name,regime.name)
                      csIds = range(variable.n)
                      tsIds = range(variable.t)
                      x=self.project.timeClass.numeric

                      ts = TimeSeries(title,self.master,x=x,y=wg,
                            title = title, xLabel = "Time",
                            yLabel = "Intraegional\n Inequality %",
                            csIds = csIds)

                      ts.top.title(title)
   

                if graph_options[1][1]:              
                    x= variable[:,0]
                    b = SBoxPlot(varName,self.project,self.master,
                                  x=x, csids = range(len(x)), tsids = [0],
                                  allX=variable)


                     
    ######################################## 
    # Mobility Callbacks
    ######################################## 

    def tau(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Tau and Spatial Tau Mobility Metrics")
        txt="Variable for mobility analysis."
        entries=['Variable']
        sd.MultiEntry(d, varNames, entries, title='Tau Mobility', helpText=txt)
        txt="Variable name that defines spatial regimes."
        sd.MultiEntry(d, varNames, entries, title='Regime Variable', helpText=txt)
        sd.SpinEntry(d, label="Time Interval", values=range(1,10),
                     align="LEFT", title="Interval")
        sd.SpinEntry(d, label="Permutations", values=[0, 99, 999, 9999],
                     align="LEFT", title="Permutations")
        graphs = "Tau", "zvalue", "Spatial Tau", "zvalue", "Regime Map"
        txt="Select any graphical views."
        sd.CheckButtons(d, title="Graphs", label="Graphs", values=graphs, helpText=txt)

        d.draw()
        if d.status:
            print d.results
            variableName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable( variableName )
            regimeName = d.results[1]['Variable']
            regime = self.project.dataBase.getVariable( regimeName )
            w = Data.spRegionMatrix(regime)
            interval = int(d.results[2])
            permutations = int(d.results[3])
            results = Tau( variable, interval=interval, w=w,
                          permutations=permutations)

            self.report(results.report())
            graphOptions = d.results[4]
            on = [ x[0] for x in graphOptions if x[1] ]
            if on.count(0):
                tau = results.tau
                yLabel="Tau %d period interval"%(int(interval))
                x = self.project.timeClass.numeric[0:-interval]
                csIds=[]
                ts = STimeSeries(variableName,
                        self.project,
                        self.master,
                        x,
                        tau,
                        variableName,
                        csIds,
                        'Tau',
                        yPop="Tau",
                        yLabel=yLabel)
            if on.count(1):
                zvalue = results.zTau
                yLabel="Tau zvalue %d period interval"%(int(interval))
                x = self.project.timeClass.numeric[0:-interval]
                csIds=[]
                try:
                    ts = STimeSeries(variableName,
                            self.project,
                            self.master,
                            x,
                            zvalue,
                            variableName,
                            csIds,
                            'Tau',
                            yPop="zTau",
                            yLabel=yLabel)
                except:
                    self.report(zvalue)

            if on.count(2) and results.permutations:
                """Plots the concordant counts for neighboring observations,
                not scaled between +/-1 as regular tau."""
                y = results.contConcordCount
                yLabel="Spatial Tau %d period interval"%(int(interval))
                x = self.project.timeClass.numeric[0:-interval]
                csIds=[]
                ts = STimeSeries(variableName,
                        self.project,
                        self.master,
                        x,
                        y,
                        variableName,
                        csIds,
                        'Tau',
                        yPop="Tau",
                        yLabel=yLabel)


            if on.count(3) and results.permutations:
                """Plots the pvalue for the concordant counts for neighboring
                observations against null of concordant count for random spatially
                perumtated observations."""
                zvalue = results.z
                yLabel="Spatial Tau zvalue %d period interval"%(int(interval))
                x = self.project.timeClass.numeric[0:-interval]
                csIds=[]
                try:
                    ts = STimeSeries(variableName,
                            self.project,
                            self.master,
                            x,
                            zvalue,
                            variableName,
                            csIds,
                            'Tau',
                            yPop="zTau",
                            yLabel=yLabel)
                except:
                    self.report(pvalue)

            if on.count(4):
                """Regime Map"""
                regime = self.project.dataBase.getVariable(regimeName)
                timePeriod = 0
                coords = self.project.coords
                poly2cs = self.project.poly2cs
                cs2poly = self.project.cs2poly
                self.drawMap("Tau Regime",coords,regime[:,0],regime.name,timePeriod,
                        poly2cs,cs2poly,classification="uniqueValues",
                        legendType="qualitative")


    def theta(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        regimeNames = self.get_CS_variable_names()
        d = sd.SDialogue("Theta Mobility and Cohesion Metrics")
        txt="""Computes the Theta Mobility and Cohesion Metrics for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        entries = ['Regime']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,regimeNames, entries, title='Choose a Regime Variable',
                      helpText=txt)
        
        interval = len(self.project.timeString)-1 
        interval = range(1,interval)
        txt = """Choose the interval for analyzing mobility over time."""
        sd.SpinEntry(d,title="Additional Options",label="Interval",
                     values=interval,helpText=txt)        
        
        graphTypes = 'Theta','Regime Map'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            regimeName = d.results[1]['Regime']
            interval = int(d.results[2])
            var = self.project.getVariable(varName)
            regime = self.project.getVariable(regimeName)            
            results = Res = Mobility.Theta(var,regime,interval=interval)
            self.report(Res.report())

            graph_options = d.results[3]
            interval = results.interval
            if graph_options[0][1]:
                theta = results.theta
                yLabel="Theta %d period interval"%(int(interval))
                x = self.project.timeClass.numeric[0:-interval]
                csIds=[]
                ts = STimeSeries(varName, self.project, self.master,
                        x, theta, varName, csIds, 'Theta', yPop="Theta",
                        yLabel=yLabel)

            if graph_options[1][1]:
                """Regime Map"""
                timePeriod = 0
                coords = self.project.coords
                poly2cs = self.project.poly2cs
                cs2poly = self.project.cs2poly
                self.drawMap("Theta Regime",coords,regime[:,0],regime.name,timePeriod,
                        poly2cs,cs2poly,classification="uniqueValues",
                        legendType="qualitative")
            


    ######################################## 
    # Markov Callbacks
    ######################################## 

    def markov(self):
        import sdialogue as sd
        varNames = self.get_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Classic Markov Analysis")
        txt="""Computes a classic Markov transition matrix analysis for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        interval = len(self.project.timeString)-1 
        interval = range(1,interval)
        txt = """Choose the interval for analyzing transitions over time."""
        sd.SpinEntry(d,title="Additional Option",label="Interval",
                     values=interval,helpText=txt)        
        
        bins = range(4,10)
        txt = """Choose the number of bins."""
        sd.SpinEntry(d,title="Additional Option",label="Bins",
                     values=bins,helpText=txt)   
        
        graphTypes = 'Map','Map (End Points)'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable'] 
            globalName = varName
            interval = int(d.results[1])
            bins = int(d.results[2])
            bins = range(1,bins,1)
            var = self.project.dataBase.getVariable(varName)

            # Regular Convergence Classification
            markovRes = Markov.ClMarkov(var,bins=[],interval=interval)
            self.report(markovRes.report())
            markovRes.convergeTable()
            ct = markovRes.conType
            variable = SVariable(ct)
            variable.setType("CS")
            variable.setName(varName+"_CT")  
            variable.setRegionNames(var.regionNames)
            variable.setTimeString(var.timeString)
            self.project.dataBase.addVariable(variable)
            varName = variable.name
            csLabels = variable.regionNames
            timeStrings = variable.timeString
            t=0
            timePeriodString = "Classic Markov %s %s"%(varName,timeStrings[t])
            yLabel = timePeriodString
            xLabel = "%s %s"%(varName,timeStrings[t])
            name = "%s %s"%(varName,timeStrings[t])
            timePeriod = 0            
            
            # Tables
            vals = markovRes.conTab
            mxx = float(max(max(vals)))
            sl = len("%.3f"%mxx) + 1
            fmt = [[sl,3]]
            colLabels = ["DD","UC","ST","DC","UD"]
            rowNames = variable.regionNames
            head = "Convergence Classification by Cross-sectional Unit %s"%(variable.name)
            tab = RTable(vals,head = head, fmt = fmt, rowNames = rowNames, colNames = colLabels).table
            self.report(tab)      

            # End Point Analysis
            cte = markovRes.conSumTableEnd
            variableE = SVariable(cte)
            variableE.setType("CS")
            variableE.setName(globalName+"_CTE")
            variableE.setRegionNames(var.regionNames)
            variableE.setTimeString(var.timeString)
            self.project.dataBase.addVariable(variableE)            
            vals = cte
            mxx = float(max(vals))
            sl = len("%.3f"%mxx) + 1
            fmt = [[sl,3]]
            colLabels = ["Class"]
            rowNames = variableE.regionNames
            vals = array(cte)
            vals = reshape(vals,(len(vals),1))
            head = "Convergence Classification by Cross-sectional Unit %s"%(variableE.name)
            tab = RTable(vals,head = head,
                fmt = fmt,
                rowNames = rowNames,
                colNames = colLabels).table
            self.report(tab)

            mat = markovRes.pMat
            ids = markovRes.match2listIds()
            top = Toplevel(self.master)
            rowLabels = markovRes.upperBounds
            rowLabels = [ "%8.3f"%(x) for x in rowLabels]
            name="Classic Markov: %s Interval: %d"%(var.name,markovRes.interval)
            varIds = [ [var.name] for id in ids[0] ]
            print "MAT", mat
            print "VARIDS", varIds
            print "ids", ids[2], ids[1]
            print "ids2\n", len(ids[2]), len(ids[1])
            tab=STable(name,top,self.project,
                    mat,varIds,ids[2],ids[1],
                    rowLabels=rowLabels,
                    columnLabels=rowLabels,
                    fmt=[8,3],type="mtable")
            
            graph_options = d.results[3]
            if sum([ x[1] for x in graph_options ]):
                coords = self.project.coords
                poly2cs = self.project.poly2cs
                cs2poly = self.project.cs2poly
            
                if graph_options[0][1]:
                    self.drawMap("Convergence Classification",coords,variable,
                                variable.name,timePeriod,poly2cs,cs2poly,
                                classification="uniqueValues",bins=bins,nBins=4,
                                legendType="diverging")
                    
                if graph_options[1][1]: 
                    bins = range(1,5,1)
                    self.drawMap("Convergence Classification (End Points)",coords,variableE,
                                variableE.name,timePeriod,poly2cs,cs2poly,
                                classification="uniqueValues",bins=bins,nBins=4,
                                legendType="diverging")


    def smarkov(self):            
        import sdialogue as sd
        varNames = self.get_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Spatial Markov Analysis")
        txt="""Computes a spatial Markov transition matrix analysis for the variable in question."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)
        
        interval = len(self.project.timeString)-1 
        interval = range(1,interval)
        txt = """Choose the interval for analyzing transitions over time."""
        sd.SpinEntry(d,title="Additional Option",label="Interval",
                     values=interval,helpText=txt)        
        
        bins = range(4,10)
        txt = """Choose the number of bins."""
        sd.SpinEntry(d,title="Additional Option",label="Bins",
                     values=bins,helpText=txt)   
        
        graphTypes = 'Map','Map (End Points)'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable']     
            globalName = varName
            w = d.results[1]['Matrix']
            interval = int(d.results[2])
            bins = int(d.results[3])
            bins = range(1,bins,1)
            var = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(w)
            markovRes = Markov.SpMarkov(var,w,bins=[],interval=interval)
            self.report(markovRes.report())

            sm=markovRes
            k=len(sm.upperBounds)
            classes = [ "%5.3f"% value for value in sm.upperBounds ]
            rowLabels = [ c+" | "+r for r in classes for c in classes ]
            mat = sm.pMat
            mat = reshape(mat,(k*k,k))
            ids = sm.match2listIds()
            varIds = [ [ var.name ] for id in ids[0] ]
            top=Toplevel(self.master)
            name = "Spatial Markov: %s Interval: %d"%(var.name,sm.interval)
            tab=STable(name,top,self.project,
                    mat,varIds,ids[2],ids[1],
                    rowLabels=rowLabels,
                    columnLabels=classes,
                    fmt=[8,3],type="mtable")

            graph_options = d.results[4]
            if sum([ x[1] for x in graph_options ]):
                coords = self.project.coords
                poly2cs = self.project.poly2cs
                cs2poly = self.project.cs2poly
            
                if graph_options[0][1]:
                    # Regular Convergence Classification
                    ct = markovRes.conType
                    variable = SVariable(ct)
                    variable.setType("CS")
                    variable.setName(varName+"_CT")  
                    variable.setRegionNames(var.regionNames)
                    variable.setTimeString(var.timeString)
                    self.project.dataBase.addVariable(variable)
                    timePeriod = 0                      
                    self.drawMap("Convergence Classification",coords,variable,
                                variable.name,timePeriod,poly2cs,cs2poly,
                                classification="uniqueValues",bins=bins,nBins=4,
                                legendType="diverging")
                    
                if graph_options[1][1]: 
                    # End Point Analysis
                    cte = markovRes.conSumTableEnd
                    variableE = SVariable(cte)
                    variableE.setType("CS")
                    variableE.setName(globalName+"_CTE")
                    variableE.setRegionNames(var.regionNames)
                    variableE.setTimeString(var.timeString)
                    self.project.dataBase.addVariable(variableE)
                    bins = range(1,5,1)
                    self.drawMap("Convergence Classification (End Points)",coords,variableE,
                                variableE.name,timePeriod,poly2cs,cs2poly,
                                classification="uniqueValues",bins=bins,nBins=4,
                                legendType="diverging")

            
   
    def localTrans(self):
        import sdialogue as sd
        varNames = self.get_CSTS_variable_names(exclude=['Time'])
        d = sd.SDialogue("Spatial Markov Analysis: Local Moran")
        txt="""Computes a spatial Markov transition matrix analysis for the
        variable in question based on local Moran's I classes."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Choose a Variable',
                      helpText=txt)
        
        matNames = self.getMatrixNames()
        entries = ['Matrix']
        txt="""Choose a weights matrix."""
        sd.MultiEntry(d,matNames, entries, title='Choose a Matrix',
                      helpText=txt)
        
        interval = len(self.project.timeString)-1 
        interval = range(1,interval)
        txt = """Choose the interval for analyzing transitions over time."""
        sd.SpinEntry(d,title="Additional Option",label="Interval",
                     values=interval,helpText=txt)        
        
        graphTypes = 'Map','Map (End Points)'
        txt = """Choose the graphs to display."""
        sd.CheckButtons(d, title='Graphs Options', label='Types', values=graphTypes,
                        helpText=txt)

        d.draw()
        if d.status:
            varName = d.results[0]['Variable']     
            globalName = varName
            w = d.results[1]['Matrix']
            interval = int(d.results[2])
            bins = range(1,5,1)
            var = self.project.dataBase.getVariable(varName)
            w = self.project.dataBase.getMatrix(w)        
            res = Markov.LocalTrans(var,w,interval=interval)
            self.report(res.report())

            # table
            mat = res.pmat
            ids = res.match2listIds()
            top = Toplevel(self.master)
            rowLabels = ["HH", "LH", "LL", "HL"]
            name="Local Markov: %s Interval: %d"%(var.name,res.interval)
            varIds = [ [var.name] for id in ids[0] ]
            tab=STable(name,top,self.project,
                    mat,varIds,ids[2],ids[1],
                    rowLabels=rowLabels,
                    columnLabels=rowLabels,
                    fmt=[8,3],type="mtable")

            graph_options = d.results[3]
            if sum([ x[1] for x in graph_options ]):
                coords = self.project.coords
                poly2cs = self.project.poly2cs
                cs2poly = self.project.cs2poly
            
                if graph_options[0][1]:
                    # Regular Convergence Classification
                    ct = res.conType
                    variable = SVariable(ct)
                    variable.setType("CS")
                    variable.setName(varName+"_CT")  
                    variable.setRegionNames(var.regionNames)
                    variable.setTimeString(var.timeString)
                    self.project.dataBase.addVariable(variable)
                    timePeriod = 0                      
                    self.drawMap("Convergence Classification",coords,variable,
                                variable.name,timePeriod,poly2cs,cs2poly,
                                classification="uniqueValues",bins=bins,nBins=4,
                                legendType="diverging")
                    
                if graph_options[1][1]: 
                    # End Point Analysis
                    cte = res.conSumTableEnd
                    variableE = SVariable(cte)
                    variableE.setType("CS")
                    variableE.setName(globalName+"_CTE")
                    variableE.setRegionNames(var.regionNames)
                    variableE.setTimeString(var.timeString)
                    self.project.dataBase.addVariable(variableE)
                    bins = range(1,5,1)
                    self.drawMap("Convergence Classification (End Points)",coords,variableE,
                                variableE.name,timePeriod,poly2cs,cs2poly,
                                classification="uniqueValues",bins=bins,nBins=4,
                                legendType="diverging")            


    def kmeans(self):
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('K-means Clustering')
        txt="The variable will be clustered in row order."
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='k-means variable',
                      helpText=txt)
        txt="Select one or more time periods for the clustering."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        
        sd.SpinEntry(d,label="Number of Clusters", values=range(2,50),
                     align="LEFT", title="Number")
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            periods = d.results[1]
            periodIds = [ self.project.timeString.index(t) for t in periods]
            nclusters = int(d.results[2])
            var = self.project.dataBase.getVariable(varName)
            y = take(var,periodIds,1)
            y = array(y)
            km = Kmeans(y,clusters=nclusters)
            v = reshape(km.ids,(len(km.ids),1))
            variable = SVariable(v)
            variable.setType("CS")
            clusterName = varName
            if clusterName:
                clusterName = varName+"_km_"+str(nclusters)
            variable.setName(clusterName)
            variable.setRegionNames(self.project.regionNames)
            variable.setTimeString(timePeriods)
            self.project.dataBase.addVariable(variable)
            coords = self.project.coords
            poly2cs = self.project.poly2cs
            cs2poly = self.project.cs2poly
            bins = range(1,5,1)
            bins = dict(zip(km.ids,km.ids)).keys()
            bins.sort()
            nbins = len(bins)
            timePeriod = 0
            self.drawMap("K-Means",coords,variable[:,0],varName,timePeriod,
                           poly2cs,cs2poly,classification="uniqueValues",
                           legendType="qualitative")




    ################################################################### 
    # Visualization callbacks
    ################################################################### 
    
    def drawMap(self,name,coords,variable,timePeriodString,timePeriod,
        poly2cs,cs2poly,classification="percentiles",nBins=5,bins=[],
        legendType="sequential"):
        """can be called outside of Viz menu, by geocomp and anaysis
        modules"""
        mp=SMap(name,self.master,self.project,coords,variable,timePeriodString,
                timePeriod,poly2cs,cs2poly,
                classification=classification,
                nBins=nBins,
                bins=bins,legendType=legendType)
        self.master.configure(cursor=options.CURSOR)

    def quantileMap(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Quantile Map Dialogue')
        txt="The variable will be mapped via designated quantiles."
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to map',
                      helpText=txt)
        sd.SpinEntry(d,label="Number of classes", values=range(2,10),
                     align="LEFT", title="Number")
        txt="Select one or more time periods for map(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            nClasses = int(d.results[1])
            periods = d.results[2]
            timeStrings = variable.timeString
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            coords = self.project.coords
            poly2cs = self.project.poly2cs
            cs2poly = self.project.cs2poly
            for t in timePeriods:
                timePeriodString = "%s %s"%(varName,timeStrings[t])
                y = variable[:,t]
                self.drawMap(timePeriodString,coords,y,varName,t,
                     poly2cs,cs2poly,classification="percentiles",nBins=nClasses)        
                
    def stdmap(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Standard Deviation Map Dialogue')
        txt="The variable will be mapped via standard deviations."
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to map',
                      helpText=txt)
        txt="Select one or more time periods for map(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            periods = d.results[1]
            timeStrings = variable.timeString
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            coords = self.project.coords
            poly2cs = self.project.poly2cs
            cs2poly = self.project.cs2poly
            for t in timePeriods:
                timePeriodString = "%s %s"%(varName,timeStrings[t])
                y = variable[:,t]
                self.drawMap(timePeriodString,coords,y,varName,t,
                         poly2cs,cs2poly,classification="stdev")
    
    def divergingMap(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Diverging Map Dialogue')
        txt="The variable will be mapped via designated classes."
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to map',
                      helpText=txt)
        sd.SpinEntry(d,label="Number of classes", values=range(4,10),
                     align="LEFT", title="Number")
        txt="Select one or more time periods for map(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            nClasses = int(d.results[1])
            periods = d.results[2]
            timeStrings = variable.timeString
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            coords = self.project.coords
            poly2cs = self.project.poly2cs
            cs2poly = self.project.cs2poly
            for t in timePeriods:
                timePeriodString = "%s %s"%(varName,timeStrings[t])
                y = variable[:,t]
                self.drawMap(timePeriodString,coords,y,varName,t,
                     poly2cs,cs2poly,classification="percentiles",nBins=nClasses,
                     legendType="diverging")

    def userDefinedC(self):
        import sdialogue as sd
        varNames = tuple(self.get_CS_CSTS_variable_names(exclude=['Time']))
        timePeriods = self.project.timeString
        d = sd.SDialogue('User Defined Map (Sequential) Dialogue')
        txt="""The variable will be mapped via designated cutoff values.  The
        color scheme is continuous."""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to map',
                      helpText=txt)
        txt="""The variable will be mapped via designated cutoff values.  Each
        cutoff provided in the entry must be seperated by a comma.  These
        cutoffs will serve as the maximum values for a corresponding bin.
        Please note that an additional maximum bin may be created if your
        highest cutoff is lower than the maximum of the actual values
        mapped.
        """        
        sd.UserEntry(d,label="Cutoff values for bins (max)", 
                     align="LEFT", title="User Defined Cutoffs",helpText=txt)
        txt="Select one or more time periods for map(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            bins = [ float(i) for i in d.results[1].split(",") ]
            periods = d.results[2]
            timeStrings = variable.timeString
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            coords = self.project.coords
            poly2cs = self.project.poly2cs
            cs2poly = self.project.cs2poly
            for t in timePeriods:
                timePeriodString = "%s %s"%(varName,timeStrings[t])
                y = variable[:,t]
                self.drawMap(timePeriodString,coords,y,varName,t,
                     poly2cs,cs2poly,classification="userDefined",bins=bins,
                     legendType='sequential')
        

    def regimeMap(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Regime Map Dialogue')
        txt="The discrete variable to be mapped."
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to map',
                      helpText=txt)
        txt="Select one or more time periods for map(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            try:
                varName = d.results[0]['Variable']
                variable = self.project.dataBase.getVariable(varName)
                periods = d.results[1]
                timeStrings = variable.timeString
                timePeriods = [ self.project.timeString.index(t) for t in periods]
                coords = self.project.coords
                poly2cs = self.project.poly2cs
                cs2poly = self.project.cs2poly
                for t in timePeriods:
                    timePeriodString = "%s %s"%(varName,timeStrings[t])
                    try:
                        y = variable[:,t]
                    except:
                        t = 0
                        y = variable[:,t]
                    self.drawMap(timePeriodString,coords,y,varName,t,
                             poly2cs,cs2poly,classification="uniqueValues",
                             legendType="qualitative")
            except:
                print "Error: You may be trying to map a continuous variable"

    def userDefinedD(self):
        import sdialogue as sd
        varNames = tuple(self.get_CS_CSTS_variable_names(exclude=['Time']))
        timePeriods = self.project.timeString
        d = sd.SDialogue('User Defined Map (Qualitative) Dialogue')
        txt="""The variable will be mapped via designated cutoff values.  The
        color scheme is categorical"""
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to map',
                      helpText=txt)
        txt="""The variable will be mapped via designated cutoff values.  Each
        cutoff provided in the entry must be seperated by a comma.  These
        cutoffs will serve as the maximum values for a corresponding bin.
        Please note that an additional maximum bin may be created if your
        highest cutoff is lower than the maximum of the actual values
        mapped.
        """        
        sd.UserEntry(d,label="Cutoff values for bins (max)", 
                     align="LEFT", title="User Defined Cutoffs",helpText=txt)
        txt="Select one or more time periods for map(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            bins = [ float(i) for i in d.results[1].split(",") ]
            periods = d.results[2]
            timeStrings = variable.timeString
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            coords = self.project.coords
            poly2cs = self.project.poly2cs
            cs2poly = self.project.cs2poly
            for t in timePeriods:
                timePeriodString = "%s %s"%(varName,timeStrings[t])
                y = variable[:,t]
                self.drawMap(timePeriodString,coords,y,varName,t,
                     poly2cs,cs2poly,classification="userDefined",bins=bins,
                             legendType="qualitative")

    def boxMap(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Box Map Dialogue')
        txt="The variable to be mapped."
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to map',
                      helpText=txt)
        txt="Select one or more time periods for map(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            periods = d.results[1]
            timeStrings = variable.timeString
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            coords = self.project.coords
            poly2cs = self.project.poly2cs
            cs2poly = self.project.cs2poly
            for t in timePeriods:
                timePeriodString = "%s %s"%(varName,timeStrings[t])
                try:
                    y = variable[:,t]
                except:
                    t = 0
                    y = variable[:,t]
                self.drawMap(timePeriodString,coords,y,varName,t,
                             poly2cs,cs2poly,classification="boxMap",
                             legendType="sequential")


    def rescaleMapCoords(self):
        self.project.reScaleCoords()

    def scatter(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Scatter Plot Dialogue')
        entries = ['X Variable','Y Variable']
        txt="This is a classic Scatter Plot for examining bivariate relationships."
        sd.MultiEntry(d,varNames,entries,title="Scatter Plot",
                helpText=txt)
        txt="Select one or more time periods for scatter(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varNameX =d.results[0]['X Variable'] 
            varNameY =d.results[0]['Y Variable'] 
            periods = d.results[1]
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            x = self.project.dataBase.getVariable(varNameX)
            y = self.project.dataBase.getVariable(varNameY)
            for t in timePeriods:
                ts = self.project.timeString[t]
                name ="%s %s and %s %s"%(varNameX,ts,varNameY,ts)
                s=SMoranScatter(name,self.master,self.project,
                        x,
                        y,
                        x[:,t],
                        y[:,t],
                        varName=varNameX,
                        variableX=str(t),
                        variableY=str(t),
                        t=t,
                        yLabel=varNameY+"_"+ts,
                        xLabel=varNameX+"_"+ts)
                s.updateTitle(name)

    def cscatter(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Conditional Scatter Plot Dialogue')
        entries = ['X Variable','Y Variable']
        txt="""
        A Conditional Scatter Plot shows two variables in an x-y plot, with individual
        observations colored according to the value of the conditional variable. This
        allows for an examination of how stable the bi-variate relationship between x
        and y is over the range of z values.

        """        
        sd.MultiEntry(d,varNames,entries,title="Conditional Scatter Plot",
                helpText=txt)
        txt = """
        This entry is for the variable that conditions the scatter plot.
        """
        varNames = self.get_CS_CSTS_variable_names()
        entries = ['Z Variable']
        sd.MultiEntry(d,varNames,entries,title="Conditional Variable",
                helpText=txt)
        d.draw()
        if d.status:
            varNameX = d.results[0]['X Variable'] 
            varNameY = d.results[0]['Y Variable']
            varNameZ = d.results[1]['Z Variable']
            #periods = d.results[2]
            #timePeriods = [ self.project.timeString.index(t) for t in periods]
            x = self.project.dataBase.getVariable(varNameX)
            y = self.project.dataBase.getVariable(varNameY)
            z = self.project.dataBase.getVariable(varNameZ)
            CScatterPlot("csp",self.master,x,y,z,xLabel=varNameX,yLabel=varNameY,
                zLabel = varNameZ)

    def histogramSturges(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Histogram Dialogue')
        entries = ['Variable']
        txt = """The chosen variable will be placed into histogram bins based on
        Sturges' Rule."""
        sd.MultiEntry(d,varNames,entries,title="Sturges Rule",
                helpText=txt)
        txt="Select one or more time periods for histogram(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varName =d.results[0]['Variable'] 
            variable = self.project.dataBase.getVariable(varName)
            timeStrings = variable.timeString
            periods = d.results[1]
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            for t in timePeriods:
                timePeriodString = "Histogram %s %s"%(varName,timeStrings[t])
                x = variable[:,t]
                y = []
                h = SHistogram(timePeriodString,self.master,varName,
                        variable,
                        self.project,
                        x,
                        y,
                        title=varName+" "+timeStrings[t],
                        xLabel=varName+" "+timeStrings[t],
                        csIds = range(len(x)),
                        tsIds = t)

    def histogramEqualWidth(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Histogram Dialogue')
        entries = ['Variable']
        txt = """The chosen variable will be placed into histogram bins based on
        Equal Widths."""
        sd.MultiEntry(d,varNames,entries,title="Equal Widths",
                helpText=txt)
        txt = "Defines the number of equal width bins for the Histogram."
        sd.SpinEntry(d,label="Number of classes", values=range(4,10),
                     align="LEFT", title="Number",helpText=txt)
        txt="Select one or more time periods for histogram(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varName =d.results[0]['Variable'] 
            variable = self.project.dataBase.getVariable(varName)
            timeStrings = variable.timeString
            nBins = int(d.results[1])
            periods = d.results[2]
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            for t in timePeriods:
                timePeriodString = "Histogram %s %s"%(varName,timeStrings[t])
                x = variable[:,t]
                y = []
                h = SHistogram(timePeriodString,self.master,varName,
                        variable,
                        self.project,
                        x,
                        y,
                        title=varName+" "+timeStrings[t],
                        xLabel=varName+" "+timeStrings[t],
                        csIds = range(len(x)),
                        tsIds = t,
                        classification="equalWidth",
                        nBins = nBins)

    def histogramUserDefined(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Histogram Dialogue')
        entries = ['Variable']
        txt = """The chosen variable will be placed into histogram bins based on
        user defined cutoffs."""
        sd.MultiEntry(d,varNames,entries,title="Equal Widths",
                helpText=txt)
        txt="""The variable will be mapped via designated cutoff values.  Each
        cutoff provided in the entry must be seperated by a comma.  These
        cutoffs will serve as the maximum values for a corresponding bin.
        Please note that an additional maximum bin may be created if your
        highest cutoff is lower than the maximum of the actual values
        mapped."""
        sd.UserEntry(d,label="Cutoff values for bins (max)", 
                     align="LEFT", title="User Defined Cutoffs",helpText=txt)
        txt="Select one or more time periods for histograms(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            bins = [ float(i) for i in d.results[1].split(",") ]
            periods = d.results[2]
            timeStrings = variable.timeString
            timePeriods = [ self.project.timeString.index(t) for t in periods]
            for t in timePeriods:
                timePeriodString = "Histogram %s %s"%(varName,timeStrings[t])
                x = variable[:,t]
                y = []
                h = SHistogram(timePeriodString,self.master,varName,
                        variable,
                        self.project,
                        x,
                        y,
                        title=varName+" "+timeStrings[t],
                        xLabel=varName+" "+timeStrings[t],
                        csIds = range(len(x)),
                        tsIds = t,
                        classification="userDefined",
                        bins=bins)
                
    def timeSeriesCs(self):
        import sdialogue as sd
        varNames = tuple(self.get_CS_CSTS_variable_names(exclude=['Time']))
        timePeriods = self.project.timeString
        d = sd.SDialogue('Regional Time-Series Dialogue')
        txt="The variable to be plotted over time."
        entries = ['Variable']
        sd.MultiEntry(d,varNames, entries, title='Variable to plot',
                      helpText=txt)
        regions = self.project.regionNames
        txt="Identify the cross-section(s) you want to plot over time."
        sd.DualListBoxes(d, regions, title='Cross-section(s) to plot', helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            csids = d.results[1]
            csids = [ regions.index(csid) for csid in csids ] 
            for csid in csids:
                y = variable[csid,:]
                timeDict={'Type':None}
                allY = variable
                x=range(len(y))
                x = self.project.timeClass.numeric
                yLabel = self.project.regionNames[csid]+" "+varName
                ts = STimeSeries(varName,
                            self.project,
                            self.master,
                            x,
                            y,
                            varName,
                            [csid],
                            allY,
                            yLabel=yLabel)

    def timeSeries(self):
        import sdialogue as sd
        varNames = tuple(self.get_TS_variable_names(exclude=['Time']))
        if len(varNames) > 0:
            timePeriods = self.project.timeString
            d = sd.SDialogue('Time-Series Dialogue')
            txt="Choose one or more time-series variable(s) to plot over time."
            sd.DualListBoxes(d,varNames, title='Variable(s) to plot', helpText=txt)
            d.draw()
            if d.status:
                varNames = d.results[0]
                for var in varNames:
                    variable = self.project.dataBase.getVariable(var)
                    t,n = variable.shape
                    y = reshape(variable,(t,))
                    y = y.tolist()
                    yAll = y
                    x = self.project.timeClass.numeric
                    yLabel = var
                    ts = STimeSeries(var,
                             self.project,
                             self.master,
                            x,
                            y,
                            var,
                            [0],
                            yAll,
                            yLabel=yLabel)
        else:
            self.report("There are no pure time-series variables to plot.")

    def timePath(self):
        import sdialogue as sd
        varNames = self.get_TS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        regions = self.project.regionNames
        d = sd.SDialogue('Time Path Dialogue')
        entries = ['X Variable', 'Y Variable']
        txt="""This is a Time Path for examining covariation over time:
        1.  Select the variable for the X axis.  
        2.  Select the variable for the Y axis. 
        """
        sd.MultiEntry(d,varNames,entries,title="Variables", helpText=txt)
        entries = ['X CS Unit', 'Y CS Unit']
        txt="""You need to select the cross-sections that correspond to each
        axis:
        1.  Select the cross-sectional name to correspond with the X axis.
        2.  Select the cross-sectional name to correspond with the Y axis.
        """
        sd.MultiEntry(d,regions,entries,title="CS Info", helpText=txt)
        d.draw()
        if d.status:
            varNameX = d.results[0]['X Variable'] 
            varNameY = d.results[0]['Y Variable'] 
            xcs = d.results[1]['X CS Unit']
            ycs = d.results[1]['Y CS Unit']
            csIds = [ regions.index(id) for id in (xcs,ycs) ]
            xAll = self.project.dataBase.getVariable(varNameX)
            yAll = self.project.dataBase.getVariable(varNameY)
            x = xAll[csIds[0],:]
            y = yAll[csIds[1],:]
            yLabel = "%s %s"%(varNameY,regions[csIds[1]])
            xLabel = "%s %s"%(varNameX,regions[csIds[0]])
            tp = STimePath("Time Path",self.project,
                self.master,
                x,
                y,
                t=range(len(y)),
                title="Time Path",
                tsLabels=[],
                csIds=csIds,xLabel=xLabel,yLabel=yLabel)

    def boxPlot(self):
        import sdialogue as sd
        varNames = self.get_CS_CSTS_variable_names(exclude=['Time'])
        timePeriods = self.project.timeString
        d = sd.SDialogue('Box Plot Dialogue')
        entries = ['Variable']
        txt = "Select the variable to analyze in the boxplot."
        sd.MultiEntry(d,varNames,entries,title="Variable", helpText=txt)
        pFence = ["1.5", "2.0", "2.5", "3.0"]
        txt = """The fences for the boxplot are based on the difference/sum of
        the upper and lower hinges and the product of the user defined value
        and the distance between the upper and lower hinges (H-spread):
            low fence = lower hinge - ( {1.5, 2.0, 2.5, 3.0} * H-spread )
            high fence = high hinge + ( {1.5, 2.0, 2.5, 3.0} * H-spread )
        """
        sd.SpinEntry(d,label="Fence",values=pFence,align="LEFT",title="Hinge Multiplier",
                     helpText=txt)
        txt="Select one or more time periods for histograms(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            fence = float(d.results[1])
            periods = d.results[2]
            timePeriods = [ self.project.timeString.index(t) for t in periods ]
            stemPoints = 1
            for t in timePeriods:
                x = variable[:,t]
                y = []
                h = SBoxPlot(varName,self.project,self.master,
                        x=x,
                        csids = range(len(x)),
                        tsids = [t],
                        allX = variable,
                        stemPoints = stemPoints,
                        fence = fence)

    def density(self):
        import sdialogue as sd
        varNames = tuple(self.get_CS_CSTS_variable_names(exclude=['Time']))
        timePeriods = self.project.timeString
        d = sd.SDialogue('Density Dialogue')
        entries = ['Variable']
        txt = "Select the variable to analyze through the kernel density estimator."
        sd.MultiEntry(d,varNames,entries,title="Variable", helpText=txt)
        txt="""The user has the option of defining the bounds for the density.
        By default the bounds will be the global minimum and maximum.  If you
        would like to change this please enter the new minimum and maximum
        seperated by a comma:
            minVal, maxVal """        
        sd.UserEntry(d,label="min, max", align="LEFT", 
                     title="User Defined Bounds* (Optional)",helpText=txt)
        txt="Select one or more time periods for density(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()

        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            try:
                userDefs = d.results[1].split(",")
                xmin,xmax = eval(userDefs)
                print 'User Defined Bounds'
            except:
                xmin = None
                xmax = None
            periods = d.results[2]
            timePeriods = [ self.project.timeString.index(t) for t in periods ]
            for t in timePeriods:
                y = variable[:,t]
                title = "Density %s %s"%(varName,variable.timeString[t])
                tsids = [t] * len(y)
                s = SDensity("Density",self.master,
                    self.project,varName,y,csid=range(len(y)),tsid=tsids,
                    title=title,xLabel=varName,xmin=xmin,xmax=xmax)

    def cdf(self):
        import sdialogue as sd
        varNames = tuple(self.get_CS_CSTS_variable_names(exclude=['Time']))
        timePeriods = self.project.timeString
        d = sd.SDialogue('CDF Dialogue')
        entries = ['Variable']
        txt = "Select the variable to analyze through the empirical CDF estimator."
        sd.MultiEntry(d,varNames,entries,title="Variable", helpText=txt)
        txt="""The user has the option of defining the bounds for the empirical CDF.
        By default the bounds will be the global minimum and maximum.  If you
        would like to change this please enter the new minimum and maximum
        seperated by a comma:
            minVal, maxVal """        
        sd.UserEntry(d,label="min, max", align="LEFT", 
                     title="User Defined Bounds* (Optional)",helpText=txt)
        txt="Select one or more time periods for CDF(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()

        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            try:
                userDefs = d.results[1].split(",")
                xmin,xmax = eval(userDefs)
                print 'User Defined Bounds'
            except:
                xmin = None
                xmax = None
            periods = d.results[2]
            timePeriods = [ self.project.timeString.index(t) for t in periods ]
            for t in timePeriods:
                y = variable[:,t]
                title = "CDF %s %s"%(varName,variable.timeString[t])
                tsids = [t] * len(y)
                s = SCDF("CDF",self.master,
                    self.project,varName,y,csid=range(len(y)),tsid=tsids,
                    title=title,xLabel=varName,xmin=xmin,xmax=xmax)
                
    def pcp(self):
        import sdialogue as sd
        varNames = tuple(self.get_CS_CSTS_variable_names(exclude=['Time']))
        timePeriods = self.project.timeString
        d = sd.SDialogue('PCP Dialogue')
        txt = "Select the variables to visualize in the Parallel Coordinate Plot."
        sd.DualListBoxes(d,varNames,title='Variables for PCP', helpText=txt)
        entries = ['Z Variable'] 
        txt = """You have the option of choosing a variable to condition the PCP
        on.  This will result in a color scheme for the connections in the
        view."""
        sd.MultiEntry(d,varNames,entries,title="Conditional Variable", helpText=txt)
        txt="Select one or more time periods for CDF(s)."
        sd.DualListBoxes(d,timePeriods,title='Time Periods', helpText=txt)
        d.draw()
        if d.status:
            varNames = d.results[0]
            variables = [ self.project.dataBase.getVariable(var) for var in varNames ]
            varNameZ = d.results[1]['Z Variable']
            variableZ = self.project.dataBase.getVariable(varNameZ)
            periods = d.results[2]
            timePeriods = [ self.project.timeString.index(t) for t in periods ]
            for t in timePeriods:
                y = []
                try:
                    for var in variables:
                        if var.varType == 'CSTS':
                            x = var[:,t]
                            y.append(x)
                        elif var.varType == 'CS':
                            x = var[:,0]
                            y.append(x)
                        else:
                            pass
                except:
                    pass
                try:
                    if variableZ.varType == 'CSTS':
                        z = variableZ[:,t]
                    elif variableZ.varType == 'CS':
                        z = variableZ[:,0]
                    else: #TIME not set
                        pass
                except:
                    varNameZ = None
                p = SPCP('pcp',self.project, self.master, varNames, y, t, z, varNameZ)

    def spaceTimeButtonMatrix(self):
        import sdialogue as sd
        varNames = tuple(self.get_CS_CSTS_variable_names(exclude=['Time']))
        timePeriods = self.project.timeString
        d = sd.SDialogue('Space-Time Button Matrix Dialogue')
        entries = ['Variable'] 
        txt = """The STBM will allow the user to quickly create views based on
        spatial lags, space-time lags, and time-time lags.  Choose the
        variable that you would like to explore."""
        entries = ['Variable'] 
        sd.MultiEntry(d,varNames,entries,title="Variable",helpText=txt)
        matNames = self.getMatrixNames()
        txt = """Choose the weights matrix that you would like to use for the
        representation of the spatial lag."""
        entries = ["W"]
        sd.MultiEntry(d,matNames,entries,title="Weights Matrix",helpText=txt)
        d.draw()
        if d.status:
            varName = d.results[0]['Variable']
            variable = self.project.dataBase.getVariable(varName)
            matName = d.results[1]['W']
            w = self.project.dataBase.getMatrix(matName)
            m = Esda.Moran(variable,w)
            ylag = array(m.ylag)
            s = SpaceTimeButtonMatrix(self.project,self.master,
                                      varName,variable,ylag)

#################### End of Visualization Menu Callbacks ###################

    def setMenuState(self):
        self.disableMenus()

    def iconify(self):
        for key in viewObserver.items.keys():
            view = viewObserver.items[key]
            view.iconify()

    def deiconify(self):
        for key in viewObserver.items.keys():
            view = viewObserver.items[key]
            view.deiconify()

    def raiseAll(self):
        self.iconify()
        self.deiconify()
    def arrangeAll(self):
        self.report("arrangeAll called")

    def closeWindows(self):
        for key in viewObserver.items.keys():
            view = viewObserver.items[key]
            view.Quit()
        self.project.closeController()
    def listViewsE(self,event):
        self.listViews()
    def listViews(self):
        lnames = {}
        for key in viewObserver.items.keys():
            view = viewObserver.items[key]
            lnames[view.listName] = key
        keys = lnames.keys()
        keys.sort()
        class dialogScrolledList(ScrolledList):
            def __init__(self,master,entries):
                ScrolledList.__init__(self,master)
                self.entries = entries
                self.master = master
            def on_select(self,index):
                item = self.get(index)
                key = lnames[item]
                view = viewObserver.items[key]
                view.iconify()
                view.deiconify()
                self.master.destroy()

        master = Toplevel(self.master) 
        s = dialogScrolledList(master,keys)
        for item in keys:
            s.append(item)

    def mapLegendsOff(self):
        for key in viewObserver.items.keys():
           view = viewObserver.items[key]
           if hasattr(view,'legend'):
               view.legendMode.set(0)
               view.changeLegend()
    def mapLegendsLeft(self):
        for key in viewObserver.items.keys():
           view = viewObserver.items[key]
           if hasattr(view,'legend'):
               view.legendMode.set(1)
               view.changeLegend()
    def mapLegendsRight(self):
        for key in viewObserver.items.keys():
           view = viewObserver.items[key]
           if hasattr(view,'legend'):
               view.legendMode.set(2)
               view.changeLegend()

    def interactionOff(self):
        viewObserver.setInteractionMode("off")
        for key in viewObserver.items.keys():
            view = viewObserver.items[key]
            view.changeInteractionMode(OFF)
    def interactionLinking(self):
        viewObserver.setInteractionMode("linking")
        for key in viewObserver.items.keys():
            view = viewObserver.items[key]
            view.changeInteractionMode(LINKING)
    def interactionBrushing(self):
        viewObserver.setInteractionMode("brushing")
        for key in viewObserver.items.keys():
            view = viewObserver.items[key]
            view.changeInteractionMode(BRUSHING)

    def help(self):
        self.report(PROGRAM)
        #help.main(self.master)
    
    def createViewController(self):
        try:
            self.project.viewController.tkraise()
            self.project.viewController.focus_set()
            self.master.lower()
        except:
            self.project.createViewController()

    ######################################## 
    # help callbacks
    ######################################## 
    def userManual(self):
        #helpFile=os.path.join(STARSHOME,"doc","starsqs.pdf")
        #if PLATFORM=='darwin':
        #    cmd = "open "+helpFile
        #elif PLATFORM=='linux2':
        #    cmd = "acroread "+helpFile
        #elif PLATFORM=="win32":
        #    cmd = "acrobat "+helpFile
        #try:
        #    t=os.popen(cmd)
        #    print t
        #    print t.readlines()
        #    t.close()
        #    print t
        #except:
        txt="Manual available at\n http://stars-py.sf.net"
        showerror("Info",txt)

    def movies(self):
        helpFile=os.path.join(STARSHOME,"doc","linking.mov")
        if PLATFORM=='darwin':
            cmd = "open "+helpFile
        elif PLATFORM=='linux2':
            cmd = "acroread "+helpFile
        elif PLATFORM=="win32":
            cmd = "acrobat "+helpFile
        try:
            t=os.popen(cmd)
            t.close()
        except:
            self.notdone

    def about(self):
        ss=sd.About(self.master)

    def gcredits(self):
        ss=sd.Credits(self.master)
    def tutorial(self):
        ss=sd.Tutorial(self.master)



    ######################################## 
    # Command Parseing 
    ######################################## 
    def parseCommand(self,command):
        com = "self.report(self.project."+command+")"
        self.report(com)
        eval(com)

    ######################################## 
    # Utility commands
    ######################################## 

    def getVariableNames(self,exclude=[]):
        names = self.project.dataBase.getVariableNames()
        names.sort()
        if len(exclude) > 0:
            [names.remove(i) for i in exclude]
        return names
        
    def get_CS_CSTS_variable_names(self,exclude=[]):
        names = self.getVariableNames()
        pdgv = self.project.dataBase.getVariable
        names=[name for name in names if pdgv(name).varType != "TS"]
        if len(exclude) > 0:
            [names.remove(i) for i in exclude if i in names]
        return names

    def get_CSTS_variable_names(self,exclude=[]):
        names = self.getVariableNames()
        pdgv = self.project.dataBase.getVariable
        names=[name for name in names if pdgv(name).varType == "CSTS"]
        if len(exclude) > 0:
            [names.remove(i) for i in exclude if i in names]
        return names

    def get_TS_CSTS_variable_names(self,exclude=[]):
        names = self.getVariableNames()
        pdgv = self.project.dataBase.getVariable
        names=[name for name in names if pdgv(name).varType != "CS"]
        if len(exclude) > 0:
            [names.remove(i) for i in exclude if i in names]
        return names

    def get_TS_variable_names(self,exclude=[]):
        names = self.getVariableNames()
        pdgv = self.project.dataBase.getVariable
        names=[name for name in names if pdgv(name).varType == "TS"]
        if len(exclude) > 0:
            [names.remove(i) for i in exclude if i in names]
        return names

    def get_CS_variable_names(self,exclude=[]):
        names = self.getVariableNames()
        pdgv = self.project.dataBase.getVariable
        names=[name for name in names if pdgv(name).varType == "CS"]
        if len(exclude) > 0:
            [names.remove(i) for i in exclude if i in names]
        return names


    def getMatrixNames(self,exclude=[]):
        names = self.project.dataBase.getMatrixNames()
        names.sort()
        if len(exclude) > 0:
            [names.remove(i) for i in exclude if i in names]
        return names

if __name__ == '__main__':
    import Tkinter
    import sys
    main = App()
    main.disableMenus()
    if len(sys.argv) == 1:
        main.mainloop()
        sys.exit()
    else:
        # below here are wrapper functions for shell
        def openProject():
            main.openProject()

        def example():
            main.example()
        def catalogue():
            print main.project.catalogue()
        def matrixNames():
            print main.getMatrixNames()
        def openProject():
            main.openProject()
        def getVariable(name):
            return main.project.getVariable(name)
        def map(variable,t=[0]):
            t=t[0]
            title = "%s %s"%(variable.name,variable.timeString[t])
            coords = main.project.coords
            poly2cs = main.project.poly2cs
            cs2poly = main.project.cs2poly
            main.drawMap(title,coords,variable[:,t],variable.name,t,
                    poly2cs,cs2poly)

        def boxPlot(variable,timePeriod = [0]):
            t = timePeriod[0]
            x = variable[:,t]
            SBoxPlot(variable.name,main.project,main.master,
                    x= x,
                    csids = range(len(x)),
                    tsids = [t],
                    allX = variable)

        def density(variable,timePeriod = [0]):
            t=timePeriod[0]
            yAll = variable
            tsids = [t] * yAll.t
            SDensity("Density",main.master,
                    main.project,y.name,y[:,t],csid=range(len(y)),
                    tsid = tsids,
                    title = "dtitle",xLabel=yAll.name,
                    xmin = None,
                    xmax = None)
        def quit():
            main.master.destroy()
            sys.exit(0)
        def disableMenus():
            main.disableMenus()

