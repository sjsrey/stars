"""
Dynamic Interactive Views module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

This module implements the primitive graphics classes for STARS.


"""

from types import *
from Tkinter import *
from tkFileDialog import *
import time, string, tkColorChooser, pickle
import tkFont
import sys
import re
import math
from random import *
from numpy.oldnumeric.random_array import *

from numpy.oldnumeric import *
from numpy.oldnumeric.mlab import *
from numpy.oldnumeric.linear_algebra import *

from Subscriber import *
from iview import *
import classifier
from Esda import PolyChar

from SDialog import * 
from color import *

import DataViewer as DV

from stars import options
from stars import DEVICE


# set up color schemes
#DEVICE = "desktop"
def getColors(legendType,numberOfClasses):
    cs = colorSchemes
    scheme = cs.getScheme(DEVICE,legendType,
                numberOfClasses)
    if scheme:
        #scheme.summary()
        return scheme.colors
    else:
        return 0

#print "default colors"
SEQCOLORS=getColors("sequential",7) # default

#VIEWBACKGROUND="white"
SCREENFORFONT6 = 118 # XXX Move to Common.py
SCREENFORFONT8 = 89  # XXX Move to Common.py




from Interaction import *



class Screen:
    """
    Get screen resolution for device for scaling Views.
    """
    def __init__(self,root):
        """
        root (Tk root): Application level Tk window.
        """
        self.screenWidth = root.winfo_screenwidth()
        if self.screenWidth > 1280:
            # kludge for serge running on dual-extended displays :)
            self.screenWidth = 1280
        self.screenHeight = root.winfo_screenheight()
        self.screenAspect= self.screenWidth * 1. / self.screenHeight
        self.root=root

class View(Screen):
    """Abstract View Class"""
    nViews = 0
    def __init__(self,name,master,width=None,height=None,title=None):
        """
        name (string): view name
        master (tk top level): Top level window the view will live in.
        width (float/int): view width
        height (float/int): view height
        title (string): title of View
        """
        Screen.__init__(self,master)
        self.observer = viewObserver
        View.nViews +=1
        #print View.nViews
        self.selectedIds = None 
        self.name = name
        self.master = master
        self.top = Toplevel(self.master)
        self.top.protocol("WM_DELETE_WINDOW",self.cleanup)
        #self.setTitle()
        self.genericString = 'View'
        self.title = title
        self.canvasTitle = ''
        self.__resizeCount = 0
        self.pointIds={}
        self.top.configure(cursor=options.CURSOR)
        if height and width:
            self.width = width
            self.height = height
        else:
            self.height = int(self.screenHeight/2.2)
            self.width  = int(self.screenWidth/2.2)
        #if self.height > self.width:
        #    self.height = self.width
        #else:
        #    self.width = self.height
        #print self.height, self.width
        self.interactionMode = OFF
        self.roamWindowOn = 0
        self.modButton = "none"
        # set max size
        self.top.maxsize(self.width,self.height)
        self.top.minsize(self.width,self.height)

        # top level window placement. divides screen into four sections.
        # 1,1   1,2
        # 2,1   2,2
        # fill up first four then place new views in 1,1, position
        sgeom = "%dx%d"%(self.width,self.height)
        if not View.nViews % 4:
            s=sgeom+"+%d+%d"%(self.width,self.height + options.TOPOFSCREEN)
            self.top.geometry(s)
        elif not View.nViews %  3:
            s=sgeom+"+%d+%d"%(0,self.height + options.TOPOFSCREEN)
            self.top.geometry(s)
        elif not View.nViews % 2:
            s=sgeom+"+%d+%d"%(self.width,options.TOPOFSCREEN)
            self.top.geometry(s)
        else:
            s=sgeom+"+%d+%d"%(0,options.TOPOFSCREEN)
            self.top.geometry(s)
   
        self.registered = 0

        self.makeMenu()

        self.canvas=Canvas(self.top,width=self.width,height=self.height,bg=options.VIEWBACKGROUND)
        self.canvas.bind('<Configure>', self.resize)
        self.canvas.bind("<Control-q>",self.Quite)
        self.canvas.bind("<1>", self.mouseLeftButton)
        self.canvas.bind("<Button1-Motion>",self.b1mouseMotion)
        self.canvas.bind("<Button1-ButtonRelease>",self.mouseLeftButtonRelease)
        self.canvas.bind("<Shift-1>",self.shiftMouseLeftButton)
        self.canvas.bind("<Shift-Button1-ButtonRelease>",
                         self.shiftMouseLeftButtonRelease)
        self.canvas.bind("<2>", self.mouseMiddleButton)
        self.canvas.bind("<Button2-ButtonRelease>",self.mouseMiddleRelease)
        self.canvas.bind("<Button-2>", self.do_menu) # for tkaqua bug!
        self.canvas.bind("<Button-3>", self.do_menu)

        self.canvas.bind("<Control-h>",self.starsWindowE)
        self.canvas.bind("<Control-m>",self.do_menu)
        self.canvas.bind("<Control-f>",self.printToFile)
        self.canvas.bind("<Control-1>",self.ctrlMouseLeft)
        self.canvas.bind("<Control-2>",self.do_menu)
        self.canvas.bind("<Control-3>",self.do_menu)
        self.canvas.bind("<Shift-2>",self.shiftMouseMiddle)
        self.canvas.bind("<Shift-3>",self.do_menu)
        self.canvas.bind("<Control-b>",self.toggleBrushing)
        self.canvas.bind("<Control-l>",self.toggleLinking)
        self.canvas.bind("<Control-r>",self.redrawE)
        self.canvas.bind("<Control-t>",self.toggleTravel)

        # roaming window
        #self.canvas.bind_all("<Button3-Motion>",self.roamWindowStretch)
        self.canvas.bind("<Escape>",self.roamWindowDeleteE)
        self.canvas.bind("<Motion>",self.mouseMotion)
        self.canvas.bind("<Shift-Button-1>",self.roamWindowStart)
        #self.canvas.bind_all("<Button3-Motion>",self.roamWindowStretch)
        self.canvas.bind("<Shift-Button1-Motion>",self.roamWindowStretch)
        self.canvas.bind("<Shift-ButtonRelease-1>",self.roamWindowStop)

        #self.roamWindowOn = 0

        #zooming
        self.canvas.bind("<Control-z>", self.startZoomingE)
        self.canvas.bind("<Control-u>", self.zoomReverseE)
        self.zoomHistory = []
        self.coordiHistory = []
        self.zoomOn = 0
        self._percent = 1.
   
        self.draw()
        self.canvas.focus_set()
	
    def startZoomingE(self,event):
        self.toggleZooming()

    def toggleZooming(self):
        if self.zoomOn:
            self.zoomOn = 0
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Button1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")

            self.canvas.bind("<1>", self.mouseLeftButton)
            self.canvas.bind("<Button1-Motion>",self.b1mouseMotion)
            self.canvas.bind("<Button1-ButtonRelease>",self.mouseLeftButtonRelease)
            self.canvas.bind("<Shift-1>",self.shiftMouseLeftButton)
            self.canvas.bind("<Shift-Button1-ButtonRelease>",
                         self.shiftMouseLeftButtonRelease)
            #self.canvas.bind_all("<Button3-Motion>",self.roamWindowStretch)
            self.canvas.bind("<Motion>",self.mouseMotion)
            self.canvas.bind("<Shift-Button-1>",self.roamWindowStart)
            #self.canvas.bind_all("<Button3-Motion>",self.roamWindowStretch)
            self.canvas.bind("<Shift-Button1-Motion>",self.roamWindowStretch)
            self.canvas.bind("<Shift-ButtonRelease-1>",self.roamWindowStop)


            print 'zoom off'
        else:
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Button1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")

            self.canvas.bind("<Button-1>",self.zoomWindowStart)
            self.canvas.bind("<Button1-Motion>",self.zoomWindowStretch)
            self.canvas.bind("<ButtonRelease-1>",self.zoomWindowStop)
            self.zoomOn=1
            print "startzoom"


    def startZooming(self):
        self.toggleZooming()
                  
           
    def zoomWindowStart(self,event):
        if self.zoomOn:
            self.startZWX = self.canvas.canvasx(event.x)
            self.startZWY = self.canvas.canvasy(event.y)
  

	
    def zoomWindowStop(self,event):
        if self.zoomOn:
            try:
                x0,y0,x1,y1 = self.canvas.coords("zoomWindow")
                self.zoomWindowDelete()
                self.zoomWindowOn = 0
                self.zoom(coords = (x0,y0,x1,y1))

            except:
                pass
	


    def zoomWindowStretch(self,event):
        if self.zoomOn:
            cx = self.canvas.canvasx(event.x)
            cy = self.canvas.canvasy(event.y)
            self.lastZWX = cx
            self.lastZWY = cy
            self.zoomWindowDelete()
            self.zoomWindowCreate([self.startZWX,self.startZWY,cx,cy])
       

      
    def zoomWindowDelete(self):
        try:
            self.canvas.delete('zoomWindow')
            self.zoomWindowOn = 0
        except:
            print 'no zoomWindow defined'

    def zoomWindowCreate(self,coords):
        if self.zoomOn:
            x0,y0,x1,y1 = coords
            self.zoomWindow = self.canvas.create_rectangle(x0,y0,x1,y1,
                        tag = 'zoomWindow', outline='white')

    def zoomReverseE(self,event):
        self.zoomReverse()

    def zoomReverse(self):
        try:
            
            percent,dx,dy = self.zoomHistory.pop()
           
            percent = 1./percent
            dx = -1 * dx
            dy = -1 * dy
            My = self.height / 2.
            Mx = self.width / 2.
         
            self.canvas.scale(ALL,Mx,My,percent,percent)
            self.canvas.move(ALL,dx,dy)
            self.updatePercent(percent)

        except:
            print 'back at original scale'

  
    def updatePercent(self,percent):
        self._percent = self._percent * percent
        
    def getPercent(self):
        return self._percent

    def getSbCoordinates(self):
        # accessor for left and right positions of scrollbars
        return (self._x0,self._y0)

  

    def resize(self, event):
        h = self.canvas.winfo_height()
        w = self.canvas.winfo_width()
        if h != self.height or w != self.width:
            self.height = h
            self.width = w
            print 'redraw required'
            print 'height, width', h,w
        else:
            if self.__resizeCount:
                print "resize not enabled"
        self.__resizeCount += 1

    def reset(self, event):
        """Reset graphical view to original size"""
        print 'resetting'
        self.root.geometry(self.__geometry)
        
                                 
    def moveXview(self,fraction):
        """move viewable portion of canvas so that top edge is at fraction of
        entire canvas."""
        self.canvas.xview_moveto(fraction)
        
    def moveYview(self,fraction):
        """move viewable portion of canvas so that left edge is at fraction of
        entire canvas."""
        self.canvas.yview_moveto(fraction)

    def showCell(self,cell):
        """move viewable portion of canvas so that cell is visible."""
        x,y = cell
        xfraction = 0.9 * y*1./self.k 
        yfraction = 0.9 * x*1./self.n
        self.moveXview(xfraction)
        self.moveYview(yfraction)
 
 
             
    def zoom(self,percent=2.00,coords=None):

        Mx = self.width/2.
        My = self.height/2.
     
       
     
        if coords:
            x0,y0,x1,y1 = coords
            #print "x0,y0,x1,y1", x0,y0,x1,y1
        
            mx = (x0+x1)/2.
            my = (y0+y1)/2.
                         
        else:
            my = Mx
            mx = My
        dx = Mx - mx
        dy = My - my
	
        self.zoomHistory.append((percent,dx,dy))
        self.updatePercent(percent)
        
        self.canvas.move(ALL,dx,dy)
        self.canvas.scale(ALL, Mx,My,percent,percent)
      
         

    def roamWindowStart(self,event):
        """
        Creates selector box to move around view.

        event (Tk event): user issued event on view.
        """
        if self.interactionMode:
            self.startRWX = self.canvas.canvasx(event.x)
            self.startRWY = self.canvas.canvasy(event.y)

    def roamWindowStop(self,event):
        """
        Stops the extent of the roaming window.

        event (Tk event): user issued event on view.
        """
        if self.interactionMode:
            self.roamWindowOn = 1

    def roamWindowStretch(self,event):
        """
        Stretches roam window as mouse is pressed and dragged.

        event (Tk event): user issued event on view.
        """
        if self.interactionMode:
            #print 'roamWindowStretch'
            cx = self.canvas.canvasx(event.x)
            cy = self.canvas.canvasy(event.y)
            self.lastRWX = cx
            self.lastRWY = cy
            self.roamWindowDelete()
            self.roamWindowCreate([self.startRWX,self.startRWY,cx,cy])

    def roamWindowDelete(self):
        """
        Destroy roam window.
        """

        try:
            self.canvas.delete('roamWindow')
            self.roamWindowOn = 0
            self.clearAll()
            self.unhighlightCentroids()
        except:
            pass

    def roamWindowDeleteE(self,event):
        """
        Destroy roam window. Wrapper around event.
        """
        self.roamWindowDelete()
        self.clearAllViews()

    def roamWindowCreate(self,coords):
        """
        Start roam window.

        coords (tuple): upper left and lower right points for rectangle.
        """
        if self.interactionMode:
            x1,y1,x2,y2 = coords
            self.roamWindow = self.canvas.create_rectangle(x1,y1,x2,y2,
                tag = 'roamWindow', outline='blue')
            self.roamWindowOn = 1



    def scale(self,amount=options.SCALE):
        """
        Scale all items on the view canvas.
        XXXworks but needs to be redone.
        """
        #w=self.width * ( 1 - options.SCALE) 
        #h=self.height * (1 - options.SCALE)
        mpx0 = self.width/2
        mpy0 = self.height/2
        self.canvas.scale( ALL,0,0,amount,amount )
        dx = mpx0 - mpx0 * amount
        dy = mpy0 - mpy0 * amount
        self.canvas.move(ALL,dx,dy)


    def scaleE(self,event):
        """
        Event wrapper for scale.
        """
        self.scale(amount=2.0)
        #self.scaleWindow()

    def scaleWindow(self,amount=options.SCALE):
        """
        Scales window.
        XXX redo
        """
        newHeight = amount * self.height
        newWidth  = amount * self.width
        geomString = "%dx%d+0+0"%(newWidth,newHeight)
        self.top.geometry(geomString)

    def makeMenu(self):
        """
        Make menus for view canvas.
        XXX get these back on prior to release.
        """
        # menu bar for view. can be overridden in subclasses to omit,
        # add menus as needed
        self.menu = Menu(self.top,tearoff=0)
        self.fileMenu()
        #self.editMenu()
        self.interMenu()
        #self.animateMenu()
        #self.windowMenu()
        #self.debugMenu()
        self.menu.add_separator()
        self.menu.add_command(label='Reset <CTRL-r>', command=self.redraw)
        self.menu.add_separator()
        self.menu.add_command(label="STARS Window",
                              command=self.starsWindow)
        self.menu.add_separator()
        self.menu.add_command(label="Close",
                              command=self.Quit)

        self.top.bind("<Button-3>",self.do_menu)

    def do_menu(self,event):
        """
        create view menus in response to event.
        """
        try:
            self.menu.tk_popup(event.x_root,event.y_root,0)
        finally:
            self.menu.grab_release()

    def fileMenu(self):
        """
        file menu for canvas

        """
        #self.interactionVar  = IntVar()
        choices = Menu()
        choices.add_command(label="Print",underline=0,command=self.printToFile)
        choices.add_separator()
        choices.add_command(label="Close",underline=0,command=self.Quit)
        self.menu.add_cascade(label="File",underline=0,menu=choices)
        

    def editMenu(self):
        """
        edit menu for canvas

        """
        self.menu.add_separator()
        choices = Menu()
        choices.add_command(label="Labels",
        underline=0,command=self.changeTextOnCanvas)
        choices.add_command(label="Legend",underline=0,command=self.notdone)
        self.menu.add_cascade(label='Edit',underline=0,menu=choices)


    def interMenu(self):
        """
        Interaction menu for canvas.

        """
        self.menu.add_separator()
        zoom = Menu()
        zoom.add_command(label="Zoom in  <CTRL-z>", underline=0,
                         command=self.startZooming)
        zoom.add_command(label="Zoom out <CTRL-u>", underline=1,
                         command=self.zoomReverse)
        self.menu.add_cascade(label="Zoom",underline=0,menu=zoom)

        self.interactionVar  = IntVar()
        imode = self.observer.getInteractionMode()
        imode = IMODES.index(imode)
        self.interactionVar.set(imode)
        pulldown = Menu()
        pulldown.add_radiobutton(label="Off",underline=0,command=self.turnoffInteraction,
            variable = self.interactionVar,value=OFF)
        pulldown.add_radiobutton(label="Linking <CTRL-l>",underline=0,command=self.linkingMode,
            variable = self.interactionVar,value=LINKING)
        pulldown.add_radiobutton(label="Brushing <CTRL-b>",underline=0,command=self.brushMode,
            variable = self.interactionVar,value=BRUSHING)
        pulldown.add_radiobutton(label="Traveling <CTRL-t>",underline=0,command=self.travelMode,
            variable = self.interactionVar,value=TRAVELING)
        pulldown.add_radiobutton(label="Brush Traveling",underline=0,command=self.brushTravelMode,
            variable = self.interactionVar,value=BRUSHTRAVELING)
        self.menu.add_separator()
        self.menu.add_cascade(label='Interaction',underline=0,menu=pulldown)

    def windowMenu(self):
        """
        Window menu for canvas
        """
        pulldown = Menu()
        pulldown.add_command(label="Iconify",underline=0,command=self.iconify)
        self.menu.add_separator()
        pulldown.add_command(label="STARS Window",underline=6,command=self.starsWindow)
        self.menu.add_cascade(label='Window',underline=0,menu=pulldown)

    def animateMenu(self):
        """
        animation menu for canvas
        """
        pulldown = Menu()
        pulldown.add_command(label="Movie",underline=0,command=self.movie)
        pulldown.add_command(label="Travel",underline=0,command=self.travel)
        self.menu.add_separator()
        self.menu.add_cascade(label='Animate',underline=0,menu=pulldown)

    def debugMenu(self):
        """
        debug menu for canvas
        """
        pulldown = Menu()
        pulldown.add_command(label="Interaction",command=self.sendInteractionVar)
        pulldown.add_command(label="Selected Observations",command=self.listSelectedIds)
        pulldown.add_command(label="UnSelect Observations",command=self.unselectIds)
        pulldown.add_command(label="WidgetIds",command=self.idWidgets)
        pulldown.add_command(label="Redraw",command=self.redraw)
        self.menu.add_separator()
        self.menu.add_cascade(label='Debug',underline=0,menu=pulldown)

    def starsWindow(self):
        """
        raise top level application window
        """
        self.root.tkraise()
        self.root.focus_set()

    def starsWindowE(self,event):
        """
        Event handler for app window raising
        """
        self.starsWindow()

    def notdone(self):
        """
        very important method.
        """
        print "not done yet"
        
    def iconify(self):
        """
        shrink windows to icon
        """
        self.top.wm_iconify()

    def deiconify(self):
        """
        blow up window from icon
        """
        self.top.wm_deiconify()

    def redrawE(self, event):
        """
        redo entire view
        """
        self.redraw()

    def redraw(self):
        self.canvas.delete('all')
        self.draw()

    def pause(self):
        """
        debug handle
        """
        a=raw_input("pause")
        
    def drawCanvasTitle(self, titleString):
        """
        Draws the title on the canvas
        
        titleString (string): string to put on canvas (duh)
        """
        g = self.canvas.create_text(self.xMidPoint, self.y1 + 5,
        text=titleString, font=(options.VIEWFONT, options.TITLEFONTSIZE), anchor = N, tag=('title'))    
        
    def changeCanvasTitle(self, title):
        """
        Changes the title on canvas
        
        titleString (string): string to put on canvas (duh)
        """
        self.canvas.delete('title')
        self.canvasTitle = title
        self.drawCanvasTitle(self.canvasTitle)       

    def changeTextOnCanvas(self):
        """
        Change text on canvas
        """
        options={}
        options[1] = ["Title",StringVar()]
        options[1][1].set(self.canvasTitle)
        SDialog("Text on Canvas",options)
        title = options[1][1].get()
        self.changeCanvasTitle(title)

    def Quit(self):
        """
        exit handler
        """
        self.cleanup()

    def Quite(self,event):
        """
        Event handler for Quit
        """
        self.Quit()

    def changeTitle(self,newTitleString):
        pass
        #print newTitleString

    def cursorBusy(self):
        """
        toggle to busy cursor
        """
        self.top.configure(cursor = options.BUSYCURSOR)

    def cusorStar(self):
        """
        change cursor to a star
        """
        self.top.configure(cursor = options.STARCURSOR)

    def cursorReset(self):
        """
        put cursor back to original cursor style.
        """
        self.top.configure(cursor = options.CURSOR)
        
    def getgeometry(self,something):
        """
        return geometry of someting as a list of ints
        """
        s = something.geometry()
        return map(int, re.sub("[x+]"," ",s).split())

    def cleanup(self):
        """
        Window Closure Handling of Top Level master
        """
        self.top.destroy()
    
    def changedInteractionMode(self):
        """
        single the change of interaction mode on this view to
        change the interaction mode on all live views.
        """
        mode = self.interactionVar.get()
        self.observer.setInteractionMode(INTERACTIONMODES[mode])
        #self.observer.setInteractionMode("ANY")
        self.interactionBroadcast() 
        for viewkey in self.observer.items.keys():
            view = self.observer.items[viewkey]
            view.changeInteractionMode(mode)
            view.clearAll()

    def clearAllViews(self):
        """
        signal to clear all views of selected widgets.
        """
        self.interactionBroadcast() 
        for viewkey in self.observer.items.keys():
            view = self.observer.items[viewkey]
            view.clearAll()




    def interactionBroadcast(self):
        print "need to override"

    def changeInteractionMode(self,mode):
        """
        change the interaction mode of this view
        """
        self.interactionVar.set(mode)
        self.interactionMode = mode
        self.interactionModeString = INTERACTIONMODES[mode]
        self.clearAll()

    def turnoffInteraction(self):
        """
        turn interaction off
        """
        self.changeInteractionMode(OFF)
        self.changedInteractionMode()

    def linkingMode(self):
        """
        turn linking on
        """
        self.changeInteractionMode(LINKING)
        self.changedInteractionMode()

    def brushMode(self):
        """
        turn brushing on
        """
        self.changeInteractionMode(BRUSHING)
        self.changedInteractionMode()

    def travelMode(self):
        """
        turn traveling on
        """
        self.changeInteractionMode(TRAVELING)
        self.changedInteractionMode()
        self.travel()

    def brushTravelMode(self):
        """
        turn brush traveling on
        """
        self.changeInteractionMode(BRUSHTRAVELING)
        self.changedInteractionMode()
        self.brushTravel()

    def clearAll(self):
        """
        unhighlight all selected widgets, and deselect all selected widgets
        """
        self.unHighlightWidget()
        self.matcher.deselect()

    def toggleBrushing(self,event):
        """
        handler
        turn brushing on
        """
        if self.interactionMode != BRUSHING:
            self.brushMode()
        else:
            self.turnoffInteraction()

    def toggleLinking(self,event):
        """
        handler
        turn linking on
        """
        if self.interactionMode != LINKING:
            self.linkingMode()
        else:
            self.turnoffInteraction()


    def toggleTravel(self,event):
        """
        handler
        turn travel on
        """
        if self.interactionMode != TRAVELING:
            self.travelMode()
        else:
            self.turnoffInteraction()

    def unselectIds(self):
        """
        deselect all selected ids
        """
        self.clearAll()

    def listSelectedIds(self):
        """
        debug method
        """
        for i in self.matcher.selected:
            print i

    def travel(self):
        """
        XXX what is this?
        """
        self.notdone()

    def brushTravel(self):
        """
        XXX what is this?
        """
        self.notdone()

    def movie(self):
        """
        XXX what is this?
        """
        self.notdone()

    def getIdsForWidgets(self,widgetIds):
        """
        map widget ids to observation ids
        widgetIds (list): list of widget ids
        XXX revisit this - self.widget2id maybe redundant or should be moved
        to in iview
        """
        matchedIds = []
        for wid in widgetIds:
            if self.widget2Id.has_key(wid):
                id = self.widget2Id[wid]
                matchedIds.append(id)
        return matchedIds


    def getWidgetsForIds(self,ids):
        """
        get widgets associated with ids:

        ids (list): list of ids to get widgets for

        returns (list): of widgets with the ids
        """
        matchedIds = []
        for id in ids:
            if self.id2Widget.has_key(id):
                wid = self.id2Widget[id]
                matchedIds.append(wid)
        return matchedIds

    def cleanWidgetIds(self,ids):
        """
        get rid of non observation-widget ids
        XXX refactor

        """
        cleanIds = []
        for id in ids:
            if self.widgetKeys.count(id):
                cleanIds.append(id)
        return cleanIds


    #file menu callbacks
    def printToFile(self,fileName="graphic.eps"):
        """
        Produce an EPSF of canvas in fileName. Note: Graph gets scaled
        and rotated as to maximize size while still fitting on paper.
        
        This could be wrapped around an interface to allow the
        printing of the eps file rather than just the creation of
        the file.""" 
        print 'in printToFile'
        bb = self.canvas.bbox("all") # Bounding box of all elements on canvas
        # Give 10 pixels room to breathe
        print bb
        bb=reshape(array(bb),[len(bb),1])
        x = max(bb[0] - 10,0)
        y = max(bb[1] - 10,0)
        width=bb[2] - bb[0] + 10
        height=bb[3] - bb[1] + 10
        width=width[0]
        height=height[0]

        printablePageHeight=280 #m
        printablePageWidth =190 #m

        printableRatio=printablePageHeight/printablePageWidth
        
        bbRatio = height/width

        fileName=asksaveasfilename(filetypes=[("Postscript files","*.eps")])

        if fileName:
            if bbRatio > printableRatio: # Height gives limiting dimension
                self.canvas.postscript(file=fileName, pageheight="%dm" % printablePageHeight,
                           x=x,y=y,height=height,width=width)	
            else:
                self.canvas.postscript(file=fileName, pagewidth="%dm" % printablePageWidth,
                           x=x,y=y,height=height,width=width)	

    def setTitle(self, title="defaultTitle"):
        """
        set view title

        title (string): view title
        """
        self.title = title

    def draw(self):
        """
        only draws the title.
        XXX dunno?
        """
        self.setTitle(self.genericString)

    def update(self):
        pass



    def quit(self,event):
        """
        Handler
        Override for withdrawing view
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')
        self.Quit()

    def sendInteractionVar(self):
        """
        Tell observer about my interaction mode
        """
        self.observer.setInteractionMode(self.interactionVar.get())
        val = self.interactionVar.get()
        self.observer.setInteractionMode(INTERACTIONMODES[val])

    def setInteractionVar(self,mode):
        """
        set interaction Var
        """
        self.interactionVar.set(mode)
                          
    def mouseLeftButton(self,event):
        """
        handler for left button press
        XXX use for newSelection
        """
        self.modButton = "none" 
        x1=self.canvas.canvasx(event.x)
        x2=x1
        y1=self.canvas.canvasy(event.y)
        y2=y1
        if self.interactionMode !=0:
            self.createSelector([x1,y1,x2,y2])
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')
        interactionVar = self.interactionVar.get()
        self.startx=x1
        self.starty=y1

        if self.selectedIds:
            self.canvas.delete("selector")
            self.unHighlightWidget()
            try:
                self.unhighlightCentroids()
            except:
                pass
            
        if self.interactionMode:
            self.canvas.delete(self.selectorRectangle)
            self.lastx = self.startx = self.canvas.canvasx(event.x)
            self.lasty = self.starty = self.canvas.canvasy(event.y)
            x1 = self.startx
            y1 = self.starty
            x2 = self.lastx
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()
        
    def shiftMouseLeftButton(self,event):
        """
        Handler for shift-left-button
        # use for extended selection
        """
        self.modButton = "shift"
        x1=self.canvas.canvasx(event.x)
        x2=x1
        y1=self.canvas.canvasy(event.y)
        y2=y1
        self.createSelector([x1,y1,x2,y2])
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')
        interactionVar = self.interactionVar.get()
        self.startx=x1
        self.starty=y1

        if self.selectedIds:
            # reset to orginal preselection colors
            self.canvas.delete("selector")
            r=range(len(self.selectedIds))
            tags=self.selectedIds

        if interactionVar:
            self.canvas.delete(self.selectorRectangle)
            self.lastx = self.startx = self.canvas.canvasx(event.x)
            self.lasty = self.starty = self.canvas.canvasy(event.y)
            x1 = self.startx
            y1 = self.starty
            x2 = self.lastx
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()

    def deleteSelector(self):
        """
        delete selector rectangle
        """
        self.canvas.delete("selector")
   
    def createSelector(self,coords):
        """
        creat selector rectangle

        coords (tuple): points for rectangle
        """
        x1,y1,x2,y2=coords
        self.selectorRectangle = self.canvas.create_rectangle(x1,y1,x2,y2,
            tag = "selector")

    def mouseMotion(self,event):
        """
        handler for movement of mouse
        """
        if self.roamWindowOn and self.interactionMode:
            #print 'mouse motion'
            cx = self.canvas.canvasx(event.x)
            cy = self.canvas.canvasy(event.y)
            try:
                dx = cx - self.lastRWX
            except:
                dx = 0.0
            dy = cy - self.lastRWY
            self.lastRWX = cx
            self.lastRWY = cy
            self.canvas.move('roamWindow',dx,dy)
            self.startRWX = cx
            self.startRWY = cy
            x1,y1,x2,y2 = self.canvas.bbox('roamWindow')
            wids = self.canvas.find_overlapping(x1,y1,x2,y2)
            #print wids
            self.selectedIds = self.cleanWidgetIds(wids)
            ids = self.getIdsForWidgets(self.selectedIds)
            newObs = self.matcher.getObsforIds(ids)
            if newObs:
                commandKey = self.modButton+self.interactionModeString
                originCommand = ORIGINCOMMANDS[commandKey]
                self.dispatch(originCommand,newObs)
                self.publish(originCommand,newObs)
                self.cursorReset()
            self.canvas.tkraise('roamWindow')



    def b1mouseMotion(self,event):
        """
        handler for left button down and move
        """
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        if self.interactionMode:
            self.deleteSelector()
            self.createSelector([self.startx,self.starty,cx,cy])
        
    def mouseLeftButtonRelease(self,event):
        """
        handler for left button release
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        if self.interactionMode:
            self.lastx  = self.canvas.canvasx(event.x)
            self.lasty  = self.canvas.canvasy(event.y)
            x1 = self.startx
            x2 = self.lastx
            y1 = self.starty
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()
            oid = self.canvas.find_overlapping(x1,y1,x2,y2)
            self.selectedIds = self.cleanWidgetIds(oid)
            ids = self.getIdsForWidgets(self.selectedIds)
            newObs = self.matcher.getObsforIds(ids)
            commandKey = self.modButton+self.interactionModeString
            originCommand = ORIGINCOMMANDS[commandKey]
            if newObs:
                self.dispatch(originCommand,newObs)
                self.publish(originCommand,newObs)
            self.cursorReset()

   
    def shiftMouseLeftButtonRelease(self,event):
        """
        handler for shift-left-button release
        """
        self.mouseLeftButtonRelease(event)

       
    def mouseMiddleButton(self,event):
        """
        handler for middle-button press
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')
        
    def mouseMiddleRelease(self,event):
        """
        handler for middle-button release
        """
        print 'middle release'

    def mouseRightButton(self,event):
        """
        handler for right-button press
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')

    def ctrlMouseLeft(self,event):
        """
        handler for ctrl-left-button press
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')

    def ctrlMouseMiddle(self,event):
        """
        handler for ctrl-middle-button press
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')
        print 'ctrlMouseMiddle'

    def ctrlMouseRight(self,event):
        """
        handler for ctrl-right-button press
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')
        print 'ctrlMouseRight'

    def shiftMouseMiddle(self,event):
        """
        handler for shift-middle-button press
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')

    def shiftMouseRight(self,event):
        """
        handler for shift-right-button press
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')
        self.do_menu()

    def cleanup(self):
        """Window Closure Handling of Top Level master"""
        self.observer.listItems()
        self.observer.unsubscribe(self)
        self.observer.listItems()
        self.top.destroy()


    def highlightWidget(self,widgetIds):
        """
        highlight widgets on view.

        widgetids (list): integer ids
        """
        for widget in widgetIds:
            self.canvas.itemconfigure(widget,fill=options.HIGHLIGHTCOLOR,
                                      outline='red')
            self.canvas.tkraise(widget)

    def highlightSingleWidget(self,widget):
        """
        highlight a single widget

        widget (int): widget id
        """
        try:
            self.canvas.itemconfigure(widget,fill=options.HIGHLIGHTCOLOR,
                                      outilne=options.BRUSHCOLOR)
        except:
            self.canvas.itemconfigure(widget,fill=options.HIGHLIGHTCOLOR)
        self.canvas.tkraise(widget)

    def unhighlightSingleWidget(self,widget):
        """
        unhighlight a single widget

        widget (int): widget id
        """
        try:
            self.canvas.itemconfigure(widget,fill=options.DEFAULTOVALFILL,
                                      outline=options.DEFAULTOVALBORDER)
        except:
            self.canvas.itemconfigure(widget,fill=options.DEFAULTOVALFILL)

    def brushWidget(self,widgetIds):
        """
        brush widgets with widgetIds

        widgetIds (list): of ints widget ids
        """
        for widget in widgetIds:
            self.canvas.tkraise(widget)
            self.canvas.itemconfigure(widget,fill=options.BRUSHCOLOR,
                                      outline=options.HIGHLIGHTCOLOR)

    def unHighlightWidget(self,widgetIds=[]):
        """
        unhighlight specific (or all) widgets

        widgetIds (list): of ints widget ids
        """
        if widgetIds == []:
            ids = self.matcher.selected
            wids = self.getWidgetsForIds(ids)
            widgetIds = wids
        for widget in widgetIds:
            if self.origColors.has_key(widget):
                color = self.origColors[widget]    
                self.canvas.itemconfigure(widget,fill=color,outline=options.DEFAULTOVALBORDER)

    def drawLine(self, xOrigin, yOrigin, xDestination, yDestination, lineWidth):
        """
        draws a line on the canvas.

        xOrigin (float): pixel for x0
        yOrigin (float): pixel for y0
        xDestination (float): pixel for x1
        yDestination (float): pixel for y1
        lineWidth (int?): width of line
        """
        self.canvas.create_line(xOrigin, yOrigin, xDestination, yDestination, width=lineWidth)


   ############################################################  
   # Interaction related methods to be found in all Views
   ############################################################  
 
    def selectedObservations(self,observations):
        """wrapper to handle own signal to extended-select own widgets associated with
        observations

        observations (list): of Observation objects
        """
        self.selectObservations(observations)

    def selectObservations(self,observations):
        """wrapper to handle signal to extended-select widgets associated with
        observations

        observations (list): of Observation objects
        """
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.highlightWidget(wids)

    def newSelectedObservations(self,observations):
        """wrapper to handle own signal to select own widgets associated with
        observations

        observations (list): of Observation objects
        """
        self.newSelectObservations(observations)

    def newSelectObservations(self,observations):
        """wrapper to handle signal to select own widgets associated with
        observations

        observations (list): of Observation objects
        """
        self.unHighlightWidget()
        self.matcher.deselect()
        self.selectObservations(observations)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)

    def brushedObservations(self,observations):
        """wrapper to handle own signal to extend-brush own widgets associated
        with observations.

        observations (list): of Observation objects
        """
        self.brushObservations(observations)

    def brushObservations(self,observations):
        """wrapper to handle signal to extend-brush own widgets associated
        with observations.

        observations (list): of Observation objects
        """
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.brushWidget(wids)

    def newBrushedObservations(self,observations):
        """wrapper to handle own signal to brush own widgets associated
        with observations.

        observations (list): of Observation objects
        """
        self.brushObservations(observations)
        self.newBrushObservations(observations)

    def newBrushObservations(self,observations):
        """wrapper to handle signal to brush own widgets associated
        with observations.

        observations (list): of Observation objects
        """
        self.brushObservations(observations)
        self.unHighlightWidget()
        self.matcher.deselect()
        self.selectObservations(observations)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.brushWidget(wids)

    def travel(self):
        """
        stub to be implemented in subclass views to handle traveling.
        """
        print "need to override"

    def buildMethods(self):
        """
        populate methods dictionary that makes selected methods public to the
        Observer.

        creates methods (dict): method name is key, method is value
        """
        # only methods that are to be accessed by observer go in here.
        m={"selectedObservations":self.selectedObservations,
           "selectObservations":self.selectObservations,
           "newSelectedObservations":self.newSelectedObservations,
           "newSelectObservations":self.newSelectObservations, 
           "brushedObservations":self.brushedObservations,
           "brushObservations":self.brushObservations,
           "newBrushedObservations":self.newBrushedObservations,
           "newBrushObservations":self.newBrushObservations,
           "updateTime":self.updateTime,
           "travel":self.travel
           }
        self.methods=m


    def idWidgets(self):
        """
        debug method to print bridge between widget and Id
        """
        for pid in self.widget2Id.keys():
            print "screen widget %s, observationId %d"%(pid,self.widget2Id[pid])

    def updateTime(self):
        """
        stub to be implemented in subclasses to handle updating time.
        """
        pass

class Table(Screen,DV.DataTable,Subscriber):
    """Abstract Container for grid display of data/matrices"""
    def __init__(self,name,master,values,varName,tsid,csid,
            rowLabels,columnLabels,fmt=[8,3],type="table"):
        """name: table name
        
           master: widget it will be associated with
        
           values: array of values to display
           
           varName: a list of lists with variable names associated with each
           cell

           tsid: a list of lists with time series ids associatied with each
           cell

           csid: a list of lists with cross sectional ids associated with each
           cell

           rowLabels: list of strings for row headings

           columnLabels: list of strings for column headings

           fmt: tupe of width and number of decimal places

           type: "table" or "mtable"  mtable is for matrices and markov transition
                 tables
        """
        Screen.__init__(self,master)
        self.observer = viewObserver
        self.values = values
        self.type = type
        self.matcher = ITable(values,varName,tsid,csid)
        self.interactionMode = OFF
        self.buildMethods()
        self.top = master
        self.top.protocol("WM_DELETE_WINDOW",self.cleanup)
        DV.DataTable.__init__(self,master,values,
                rowLabels=rowLabels,columnLabels=columnLabels,listener=self,
                labelFamily=options.getLabelFontFamily(),
                labelSize=options.getLabelFontSize(),
                cellFamily=options.getCellFontFamily(),
                cellSize=options.getCellFontSize(),
                fmt=fmt)

        Subscriber.__init__(self,self.observer)
        self.interactionMode = OFF
        self.buildMethods()
        self.top = master
        self.top.protocol("WM_DELETE_WINDOW",self.cleanup)


 
    def iconify(self):
        """
        shrink windows to icon
        """
        self.top.wm_iconify()

    def deiconify(self):
        """
        blow up window from icon
        """
        self.top.wm_deiconify()

    def redraw(self):
        """
        redo entire view
        """
        self.canvas.delete('all')
        self.draw()


    def cleanup(self):
        """
        Window Closure Handling of Top Level master
        """
        self.top.destroy()
    

    def Quit(self):
        """
        exit handler
        """
        self.cleanup()


    def buildMethods(self):

        m={"selectedObservations":self.selectedObservations,
           "selectObservations":self.selectObservations,
           "selectObservationsCS":self.selectObservationsCS,
           "newSelectedObservations":self.newSelectedObservations,
           "newBrushObservations":self.newBrushObservations,
           "newSelectColumn":self.newSelectColumn
           }
        self.methods=m

    def selectedObservations(self,observations):
        self.selectObservations(observations)

    def selectObservations(self,observations):
        """wrapper to handle signal to extended-select widgets associated with
        observations

        observations (list): of Observation objects
        """
        ids = self.matcher.matchObservations(observations)
        cells = [ self.id2cell[id] for id in ids]
        self.selectCells(cells)
        r,c = cells[-1]
        self.showCell((r,0))

    def selectObservationsCS(self,observations):
        for obs in observations:
            ids = self.matcher.matchObservationsCS(observations)
        cells = [ self.id2cell[id] for id in ids]
        self.selectCells(cells)
        r,c = cells[-1]
        self.showCell((r,0))



    def newBrushObservations(self,observations):
        self.selectObservations(observations)

    def newSelectedObservations(self,observations):
        self.selectObservations(observations)

    def changeInteractionMode(self,mode):
        """
        change the interaction mode of this view
        """
        self.interactionMode = mode
        self.interactionModeString = INTERACTIONMODES[mode]
        if mode == LINKING:
            self.setHighlightColor(options.HIGHLIGHTCOLOR)
        elif mode == BRUSHING:
            self.setHighlightColor(options.BRUSHCOLOR)
        elif mode == OFF:
            self.setHighlightColor(options.HIGHLIGHTCOLOR)
        elif mode == BRUSHTRAVELING:
            self.setHighlightColor(options.BRUSHCOLOR)
        self.clearAll()


    def clearAll(self):
        self.unHighlightSelectedSet()

    def cleanup(self):
        """Window Closure Handling of Top Level master"""
        self.observer.listItems()
        self.observer.unsubscribe(self)
        self.observer.listItems()
        self.top.destroy()

    def getObservations(self):
        ids = self.getFlattenedSelectedCellIds()
        return [self.matcher.observations[id] for id in ids ]


    def selectCell(self,event):
        """Select an individual cell."""
        DV.DataTable.selectCell(self,event)
        obs = self.getObservations()
        obs = self.getObservations()
        self.publish("newSelectedObservations",obs)

    def selectCellText(self,event):
        """Select an individual cell underneath text value."""
        DV.DataTable.selectCellText(self,event)
        obs = self.getObservations()
        self.publish("newSelectedObservations",obs)

    def onShiftButton1(self,event):
        DV.DataTable.onShiftButton1(self,event)
        obs = self.getObservations()
        self.publish("selectedObservations",obs)

    def selectLabel(self,event):
        DV.DataTable.selectLabel(self,event)
        obs = self.getObservations()
        if 'rlabel' in self.ctag:
            self.publish("newSelectedObservations",obs)
        else:
            ts = obs[0].ts
            self.publish("newColumnSelected",ts)

    def selectLabelExtend(self,event):
        DV.DataTable.selectLabelExtend(self,event)
        obs = self.getObservations()

    def newSelectColumn(self,ids):
        """
        ids is a list with one integer pointing to column to highlight. First
        row will be shown in vertical view of grid."""

        if len(ids) > 1:
            ids = ids[0] # get earliest column
        DV.DataTable.selectColumns(self,ids)
        self.showCell((0,ids[0]))



class Plot(View):
    """
    Abstract Plot Class.
    """
    def __init__(self,name,master,x,y,xDelimiter=None,yDelimiter=None,
        title=None,
        xLabel=None, yLabel=None, xDecimal=None, yDecimal=None,
        ovalFill=None, ovalBorder=None,xPop='X',yPop='Y'):
        """
        Constructor

        name (string): name of view
        master (Tk.Toplevel): top level window view lives in
        x (?):
        y (?):
        xDelimeter (?):
        yDelimeter (?):
        title (?):
        xLabel (?):
        yLabel (?):
        xDecimal (?):
        yDelimiter (?):
        ovalFill (?):
        ovalBoarder (?):
        xPop (?):
        yPop (?):
        """
        self.x = x
        self.y = y
        self.xDelimiter = xDelimiter
        self.yDelimiter = yDelimiter
        self.name = name
        self.master = master
        self.title = title
        self.canvasTitle = ''
        self.labelDict = {}
        self.labelDict['title'] = ''
        self.Type="Plot"
        self.xDecimal = xDecimal
        self.yDecimal = yDecimal
        self.ovalFill = ovalFill
        self.ovalBorder = ovalBorder
        self.xPop = xPop
        self.yPop = yPop
        View.__init__(self,name,master,width=None,height=None,
                     title=self.title)
        self.top.title(self.title)
        #self.canvas.pack(side=LEFT,anchor=W)
        self.canvas.pack(fill=BOTH,expand=YES)
        self.IDS = range(len(self.x))
        self.editMenu()
        
    def changeTextOnCanvas(self):
        """
        Prompt user for new Title, X and Y Labels and changes them on view 
        """
        options={}
        options[1] = ["Title",StringVar()]
        options[2] = ["X-Label", StringVar()]
        options[3] = ["Y-Label", StringVar()]
        options[1][1].set(self.canvasTitle)
        options[2][1].set(self.xLabel)
        options[3][1].set(self.yLabel)

        SDialog("Text on Canvas",options)
        title = options[1][1].get()
        xLabel = options[2][1].get()
        yLabel = options[3][1].get()
        self.changeXLabel(xLabel)
        self.changeYLabel(yLabel)
        self.changeCanvasTitle(title)

    def editMenu(self):
        """
        Items for edit component of view-specific menu.
        """
        self.menu.add_separator()
        choices = Menu()
        choices.add_command(label="Labels",
        underline=0,command=self.changeTextOnCanvas)
        choices.add_command(label="Legend",underline=0,command=self.notdone)
        self.menu.add_cascade(label='Edit',underline=0,menu=choices)

    def draw(self):
        """
        Wraps all the calls to methods to draw individual components.
        """
        self.setOvalColors()
        self.scaleBox()
        self.getMinMax()
        self.getRanges()
        self.getRatios()
        self.makeXTicks()
        self.makeYTicks()
        self.makeTickLabels()
        self.scaleTicks()
        self.scalePoints()
        self.drawOuterBox()
        self.drawAxis()
        self.drawTicks()
        self.drawPoints()

    def setOvalColors(self):
        """
        Handles setting of oval colors (passed in to constructor) for fill and
        border.
        """
        if self.ovalFill:
            self.ovalFill = self.ovalFill
        else:
            self.ovalFill = options.DEFAULTOVALFILL
        if self.ovalBorder:
            self.ovalBorder = self.ovalBorder
        else:
            self.ovalBorder = options.DEFAULTOVALBORDER
    
    def scaleBox(self):
        """
        Outer Box is the frame, Inner Box includes the X-Y axis, and
        the Buffer Box will include all of the data.  No points on a
        plot are allowed outside the Buffer Box.
        """
        #get outer box vertices
        self.x1 = self.width * options.OUTERBOXPLOTS[0]
        self.y0 = self.height * options.OUTERBOXPLOTS[0]
        self.x0 = self.width * options.OUTERBOXPLOTS[1]
        self.y1 = self.height * options.OUTERBOXPLOTS[1]
        #get x y inner vertices for plot
        self.x1Inner = self.width * options.INNERBOXPLOTS[0]
        self.y0Inner = self.height * options.INNERBOXPLOTS[0]
        self.x0Inner = self.width * options.INNERBOXPLOTS[1]
        self.y1Inner = self.height * options.INNERBOXPLOTS[1]
        #get buffer box
        self.x1Buffer = self.width * options.BUFFERBOXPLOTS[0]
        self.x0Buffer = self.width * options.BUFFERBOXPLOTS[1]
        self.y0Buffer = self.height * options.BUFFERBOXPLOTS[0]
        self.y1Buffer = self.height * options.BUFFERBOXPLOTS[1]
        #get midpoint for x and title labels
        self.xMidPoint = (self.x0Inner + self.x1Inner) / 2

    def getMinMax(self):
        """
        Get extreme values for both x and y variables.
        """
        self.MaxX = max(self.x) 
        self.MinX = min(self.x) 
        self.MaxY = max(self.y) 
        self.MinY = min(self.y) 

    def getRanges(self):
        """
        Get Ranges for x and y variables and create sequences for these
        ranges.
        """
        self.xRangeValues = self.MaxX - self.MinX
        self.yRangeValues = self.MaxY - self.MinY
        self.xIntegerRange = arange(self.MinX, self.MaxX+1)
        self.yIntegerRange = arange(self.MinY, self.MaxY+1)


    def getRatios(self):
        """
        Find screen to world ratio for both x and y axes.
        """
        self.xratio = (self.x1Buffer - self.x0Buffer) / self.xRangeValues
        self.yratio = (self.y1Buffer - self.y0Buffer) / self.yRangeValues
        
    def makeXTicks(self):
        """
        Creates X tick marks either by default or with 
        delimiter arguments.
        """
        self.xTickInterval = self.MaxX - self.MinX
        if self.xDelimiter == None:
            ints = 4.0
            width = self.xTickInterval / ints
            self.xTicks = arange(self.MinX, self.MaxX + width, width)
            self.xTicks = self.xTicks.tolist()
            self.xTicks = self.xTicks[0:5]
        elif len(self.xDelimiter) == 1:
            ints = self.xDelimiter[0]
            numberXBreaks = range(1, ints+1)
            for i in numberXBreaks:
                t = float(i) / numberXBreaks[-1]
                xBreaks.append(t)
            for i in xBreaks:
                self.xTicks.append(self.MinX + (self.xTickInterval * i))
            self.xTicks.append(self.MinX)
        else:
            self.xTicks = self.xDelimiter

    def makeYTicks(self):
        """
        Creates Y tick marks either by default or with 
        delimiter arguments.
        """
        self.yTickInterval = self.MaxY - self.MinY
        if self.yDelimiter == None:
            ints = 4.0
            width = self.yTickInterval / ints
            self.yTicks = arange(self.MinY, self.MaxY + width, width)
            self.yTicks = self.yTicks.tolist()
            self.yTicks = self.yTicks[0:5]
        elif len(self.yDelimiter) == 1:
            ints = self.yDelimiter[0]
            numberYBreaks = range(1, ints+1)
            for i in numberYBreaks:
                t = float(i) / numberYBreaks[-1]
                yBreaks.append(t)
            for i in yBreaks:
                self.yTicks.append(self.MinY + (self.yTickInterval * i))
            self.yTicks.append(self.MinY)
        else:
            self.yTicks = self.yDelimiter
    
    def makeTickLabels(self):
        """
        Format x and y labels create decimal places by default or for
        argument passed in.
        """
        if self.xDecimal:
            pass
        else:
            if self.MaxX < 10.0:
                self.xDecimal = 3
            else:
                self.xDecimal = 0
        if self.yDecimal:
            pass
        else:
            if self.MaxY < 10.0:
                self.yDecimal = 3
            else:
                self.yDecimal = 0
        # get largest integer and change to str for left pad
        xTickLeft = [int(i) for i in self.xTicks]
        tmp = [len(str(i)) for i in xTickLeft]
        self.xTickLeftMax = max(tmp)
        # format all xTick values
        tmpX = "%"+str(self.xTickLeftMax)+"."+str(self.xDecimal)+"f"
        self.xTicksLabs = [tmpX %(i) for i in self.xTicks]
        yTickLeft = [int(i) for i in self.yTicks]
        yTickLeft = [len(str(i)) for i in yTickLeft]
        self.yTickLeftMax = max(yTickLeft)
        # format all yTick values
        tmpY = "%"+str(self.yTickLeftMax)+"."+str(self.yDecimal)+"f"
        self.yTicksLabs = [tmpY %(i) for i in self.yTicks]

    def scaleTicks(self):
        """Scale x and y axis ticks"""
        self.scaledXTicks = [self.x0Buffer + (self.xTicks[x] - self.MinX) * self.xratio for x in range(0,len(self.xTicks))]
        self.scaledYTicks = [self.y0Buffer + (self.yTicks[x] - self.MinY) * self.yratio for x in range(0,len(self.yTicks))]

    def scalePoints(self):
        """Scale x and y values to fit canvas"""
        self.scaledXCords = [self.x0Buffer + (self.x[x] - self.MinX) * self.xratio for x in range(0,len(self.x))]
        self.scaledYCords = [self.y0Buffer + (self.y[x] - self.MinY) * self.yratio for x in range(0,len(self.y))]

    def fitLine(self,x=[],y=[],tagString = "fitLine",fill="black"):
        """
        Fits a line using ols to x-y scatter.

        x (list): x values (uses original if empty)
        x (list): y values (uses original if empty)
        tagString (string): string to use as tag for line on canvas
        fill (string): color for the fitline
        """
        if not x:
            x = array(self.scaledXCords)
        if not y:
            y = array(self.scaledYCords)

        mx = mean(x)
        my = mean(y)
        xd = x - mx
        yd = y - my
        x2 = sum(xd*xd)
        xy = sum(xd*yd)
        b = xy/x2
        a = my - b * mx
        x0 = min(self.scaledXCords)
        x1 = max(self.scaledXCords)
        y0 = a + b * x0
        y1 = a + b * x1

        # constrain line endpoints to stay within range of Y
        yScreenMin = min(self.scaledYCords)
        yScreenMax = max(self.scaledYCords)

        if y0 < yScreenMin:
            x0 = (yScreenMin - a)/b
            y0 = yScreenMin
        elif y0 > yScreenMax:
            x0 = (yScreenMax - a)/b
            y0 = yScreenMax

        if y1 < yScreenMin:
            x1 = (yScreenMin - a)/b
            y1 = yScreenMin
        elif y1 > yScreenMax:
            x1 = (yScreenMax - a)/b
            y1 = yScreenMax

        self.canvas.create_line(x0,y0,x1,y1, width = 1,tags=(tagString),fill=fill )


    def clearAll(self):
        View.clearAll(self)
        self.removeFitLine()
        self.removeBrushLine()



    def removeFitLine(self):
        """
        Removes fitline from canvas.
        """
        self.canvas.delete("fitLine")

    def removeBrushLine(self):
        """
        Removes brush line from canvas.
        """
        self.canvas.delete("brushLine")

    def drawOuterBox(self):
        """ Draw outer box around view."""
        self.drawLine(self.x0,self.y0,self.x1,self.y0, 1)
        self.drawLine(self.x1,self.y0,self.x1,self.y1, 1)
        self.drawLine(self.x1,self.y1,self.x0,self.y1, 1)
        self.drawLine(self.x0,self.y1,self.x0,self.y0, 1)

    def drawAxis(self):
        """draw x and y axis"""
        self.drawLine(self.x0Inner,self.y0Inner,self.x1Inner,self.y0Inner, 2)
        self.drawLine(self.x0Inner,self.y0Inner,self.x0Inner,self.y1Inner, 2)

    def drawTicks(self):
        """Draw ticks and value labels for X and Y axis"""
        stringLengths = []
        [stringLengths.append(len(i)) for i in self.xTicksLabs]
        [stringLengths.append(len(i)) for i in self.yTicksLabs]
        maxLabelLength = max(stringLengths)
        if maxLabelLength <= 6:
            self.axisFontSize = 8
        else:
            self.axisFontSize = 8
            
        c = 0
        for i in self.scaledXTicks:
            self.drawLine(i, self.y0Inner, i, self.y0Inner + 4, 1)
            self.canvas.create_text(i+2 , self.y0Inner + 7, text=self.xTicksLabs[c], 
            font=('Times', options.AXISFONTSIZE), anchor = W)
            c = c+1
        # draw ticks and value labels Y
        c = 0
        for i in self.scaledYTicks:
            self.drawLine(self.x0Inner, i, self.x0Inner - 4, i, 1)
            self.canvas.create_text(self.x0Inner - 2, i-5, text=self.yTicksLabs[c], 
            font=(options.VIEWFONT, options.AXISFONTSIZE), anchor = E)
            c = c+1

        # for label boxes # ratio from screen buffers to str lengths
        if options.AXISFONTSIZE == 8:
            self.xStringRatio = (self.x1Buffer - self.x0Buffer) / options.SCREENFORFONT8
        else:
            self.xStringRatio = (self.x1Buffer - self.x0Buffer) / options.SCREENFORFONT6
    
    def drawPoints(self):
        """
        Plots x-y points on canvas.
        """
        self.id2Widget = {}
        self.widget2Id = {}
        self.idInfo = {}
        self.origColors = {}
        c = 0
        for i in self.scaledXCords:
            x1 = i
            y1 = self.scaledYCords[c]
            x1 = x1-options.NEGATIVEOVAL
            y1 = y1-options.NEGATIVEOVAL
            x2=x1+options.POSITIVEOVAL
            y2=y1+options.POSITIVEOVAL
            g = self.canvas.create_oval(x1,y1,x2,y2,outline=self.ovalBorder, fill=self.ovalFill)
            self.origColors[g] = self.ovalFill
            self.id2Widget[c] = g

            self.widget2Id[g] = c
            self.idInfo[c] = [self.x[c], self.y[c]] #actual x,y vals for tags
            c = c+1
        self.widgetKeys = self.widget2Id.keys()

    def drawYLabel(self):
        """Draws the Y-Axis label on the canvas"""
        if len(self.yLabel) < 16:
            g = self.canvas.create_text(self.x0Inner, self.y1Inner - 4,
            text=self.yLabel, font=('Times', options.AXISFONTSIZE), anchor = S, tag=('YLabel'))
        else:
            g = self.canvas.create_text(self.x0 + 3, self.y1Inner - 10,
            text=self.yLabel, font=('Times', options.AXISFONTSIZE), anchor = W, tag=('YLabel'))

    def drawXLabel(self):
        """Draws the X-Axis label on the canvas"""
        g = self.canvas.create_text(self.xMidPoint, self.y0 - 5,
        text=self.xLabel, font=('Times', options.AXISFONTSIZE), anchor = S, tag=('XLabel'))

    def drawCanvasTitle(self, titleString):
        """Draws the title on the canvas"""
        g = self.canvas.create_text(self.xMidPoint, self.y1 + 5,
        text=titleString, font=('Times', 10), anchor = N, tag=('title'))
        
    def changeYLabel(self, newLabel):
        """Changes the Y Label on canvas"""
        self.canvas.delete('YLabel')
        self.yLabel = newLabel
        self.drawYLabel()

    def changeXLabel(self, newLabel):
        """Changes the X Label on canvas"""
        self.canvas.delete('XLabel')
        self.xLabel = newLabel
        self.drawXLabel()
 
    def changeCanvasTitle(self, title):
        """Changes the title on canvas"""
        self.canvas.delete('title')
        self.canvasTitle = title
        self.drawCanvasTitle(self.canvasTitle)

    def changeTitle(self):
        """changes title in toplevel window."""
        self.top.title(self.title)
        
    def newBrushObservations(self,observations):
        """
        Overrides method from View.
        """
        self.removeBrushLine()
        self.unHighlightWidget()
        self.matcher.deselect()
        self.selectObservations(observations)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.brushWidget(wids)

    def brushObservations(self,observations):
        """
        Overrides method from View.
        """
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.brushWidget(wids)
        compids = [j for j in self.IDS if ids.count(j) == 0]
        xvals = array([self.scaledXCords[i] for i in compids])
        yvals = array([self.scaledYCords[i] for i in compids])

        if len(xvals) > 2:
            #self.fitLine(xvals,yvals,tagString="brushLine",fill=options.DEFAULTOVALFILL)
            self.fitLine(xvals,yvals,tagString="brushLine",fill='Blue')
        else:
            pass

    def brushWidget(self,widgetIds):
        """
        Overrides View method
        """
        for widget in widgetIds:
            self.canvas.itemconfigure(widget,fill=options.BRUSHCOLOR,outline='Yellow')
            self.canvas.tkraise(widget)

    def changeInteractionMode(self,mode):
        """
        Changes Interaction Mode.
        """
        self.interactionVar.set(mode)
        self.interactionMode = mode
        self.interactionModeString = INTERACTIONMODES[mode]
        self.removeBrushLine()

    def mouseMiddleButton(self,event):
        """
        Overrides View method
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
            observation = self.matcher.observations[cid]
            ts = str(observation.ts)
            varNames = observation.variable
            values = observation.value
            csString = 'cross-section id: ' + str(cid) + '\n'
            tsString = 'time-series id: ' + ts + '\n'
            c = 0
            temps = ['X', 'Y']
            for i in varNames:
                if i == None:
                    varNames[c] = temps[c]
                c = c+1
            xString = varNames[0] + "= " + str(values[0]) + '\n'
            yString = varNames[1] + "= " + str(values[1])
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
        Overrides View method
        """
        try:
            self.unhighlightSingleWidget(self.tempWID)
            self.canvas.delete(self.tLabel)
            self.canvas.delete(self.identLabel)
        except:
            pass

class MoranScatter(Plot,Subscriber):
    """
    View for Moran Scatter Plot 
    """
    nmscat = 0
    def __init__(self,name,master,x,y,varName,variableX,variableY,t,xDelimiter=None,yDelimiter=None,title=None,
        xLabel=None, yLabel=None, xDecimal=None, yDecimal=None,
        ovalFill=None, ovalBorder=None, xPop='X', yPop='Y'):
        """
        Constructor.

        name (string): name of plot
        master (Tk.toplevel): toplevel window view lives in
        x (list): of values for x variable
        y (list): of values for y variable (spatial Lag)
        varName (string): name of variable depicted in scatter
        variableX (STARS Variable): XXX need to check this logic
        variableY (STARS Variable): XXX
        t (?): XXX what is this
        xDelimiter (?):
        yDelimiter (?):
        title (?):
        xLabel (?):
        yLabel (?):
        xDecimal (?):
        yDelimiter (?):
        ovalFill (?):
        ovalBoarder (?):
        xPop (?):
        yPop (?):
        """
        self.name = name
        self.master = master
        self.title=title
        self.type="scatter"
        self.xDecimal = xDecimal
        self.yDecimal = yDecimal
        self.yLabel = yLabel
        self.xLabel = xLabel
        self.ovalFill = ovalFill
        self.ovalBorder = ovalBorder
        self.labelDict = {}
        self.titleOnCanvas = 0
        self.moranString = 'Scatter Plot'
        self.setTitle(self.moranString)
        Plot.__init__(self,name,master,x,y,xDelimiter=None,yDelimiter=None,title=self.title,
                      xLabel=xLabel, yLabel=yLabel, xDecimal=None, yDecimal=None,
                      ovalFill=None, ovalBorder=None,xPop=xPop,yPop=yPop)
        
        self.canvas.pack(side=LEFT,anchor=W)
        self.matcher = IScatter(variableX,x,variableY,
                                y,t)

        MoranScatter.nmscat +=1
        self.name = "mscat_%d"%MoranScatter.nmscat
        self.top.title(self.title)
        Subscriber.__init__(self,self.observer)

    def draw(self):
        """
        Overrides Plot method.
        """
        self.setOvalColors()
        self.scaleBox()
        self.getMinMax()
        self.getRanges()
        self.getRatios()
        self.getMeanAxis()
        self.makeXTicks()
        self.makeYTicks()
        self.makeTickLabels()
        self.scaleTicks()
        self.scalePoints()
        self.drawOuterBox()
        self.drawScatterAxis()
        self.drawTicks()
        self.drawPoints()
        self.fitLine()
        self.drawYLabel()
        self.drawXLabel()
        
    def drawPoints(self):
        """
        Overrides Plot method.
        """
        self.id2Widget = {}
        self.widget2Id = {}
        self.idInfo = {}
        self.origColors = {}
        self.ovalLabel2Id = {}
        c = 0
        for i in self.scaledXCords:
            x1 = i
            y1 = self.scaledYCords[c]
            x1 = x1-options.NEGATIVEOVAL
            y1 = y1-options.NEGATIVEOVAL
            x2=x1+options.POSITIVEOVAL
            y2=y1+options.POSITIVEOVAL
            g = self.canvas.create_oval(x1,y1,x2,y2,outline=self.ovalBorder,
            fill=self.ovalFill, tag=('OVAL', str(c)))
            self.origColors[g] = self.ovalFill
            self.id2Widget[c] = g
            self.widget2Id[g] = c
            
            self.idInfo[c] = [self.x[c], self.y[c]] #actual x,y vals for tags
            c = c+1
        self.widgetKeys = self.widget2Id.keys()
        self.canvas.tag_bind("OVAL", "<Control-1>")
        
    def ctrlMouseLeft(self,event):
        """
        Overrides View method.
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')
        try:
            csId = int(tg[1])
            self.drawLEO(csId)
        except:
            pass

    def drawLEO(self,csString):
        """
        XXX debug method only?
        """
        print 'Draw LEO with csid - ', csString
        
    def getMeanAxis(self):
        """
        Set pixel locations of average x and y value on axes
        """
        self.xMean = mean(self.x)
        self.xMeanPix = self.x0Buffer + (self.xMean - self.MinX) * self.xratio
        self.yMean = mean(self.y)
        self.yMeanPix = self.y0Buffer + (self.yMean - self.MinY) * self.yratio

    def drawScatterAxis(self):
        """
        Draws Axis with mean X-Y grid.
        """
        self.drawAxis()
        self.drawLine(self.xMeanPix, self.y0Inner, self.xMeanPix, self.y1Inner, 1)
        self.drawLine(self.x0Inner, self.yMeanPix, self.x1Inner, self.yMeanPix, 1)

    def newBrushObservations(self,observations):
        """
        Overrides View method.
        """
        self.removeLinkLine()
        self.removeBrushLine()
        self.unHighlightWidget()
        self.matcher.deselect()
        self.selectObservations(observations)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.brushWidget(wids)
        # get complement set to selected ids
        compids = [j for j in self.IDS if ids.count(j) == 0]
        xvals = array([self.scaledXCords[i] for i in compids])
        yvals = array([self.scaledYCords[i] for i in compids])
        if len(xvals) > 2:
            self.fitLine(xvals,yvals,tagString="brushLine",fill=options.HIGHLIGHTCOLOR)
        else:
            pass

        # plot fit line for selected set
        ownids = [ j for j in self.IDS if ids.count(j) ]
        xvals = array([self.scaledXCords[i] for i in ownids])
        yvals = array([self.scaledYCords[i] for i in ownids])

        if len(xvals) > 2:
            self.fitLine(xvals,yvals,tagString="brushLine",fill=options.BRUSHCOLOR)
        else:
            pass


    def updateTime(self,tsId):
        """
        Overrides View method.

        XXX get current x and y variables
        XXX assumes moran has set these in gui.py
        """
        x = self.xVar
        y = self.xVarLag
        x = x[:,tsId]
        y = y[:,tsId]
        self.x = x
        self.y = y
        self.canvas.delete('all')
        self.draw()

    def redraw(self,tsId):
        """
        Clears view and redraws itself.

        XXX why the x.reverse() call?
        """
        self.x.reverse()
        t = tsId
        self.canvas.delete('all')
        self.draw()
        
    def removeLinkLine(self):
        self.canvas.delete('linkLine')

    def clearAll(self):
        View.clearAll(self)
        self.removeBrushLine()
        self.removeLinkLine()


    def newSelectObservations(self,observations):
        """wrapper to handle signal to select own widgets associated with
        observations

        observations (list): of Observation objects
        """
        self.unHighlightWidget()
        self.matcher.deselect()
        self.removeLinkLine()
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.highlightWidget(wids)
        compids = [j for j in self.IDS if ids.count(j)]
        xvals = array([self.scaledXCords[i] for i in compids])
        yvals = array([self.scaledYCords[i] for i in compids])
        if len(xvals) > 2:
            self.fitLine(xvals,yvals,tagString="linkLine",fill=options.HIGHLIGHTCOLOR)
        else:
            pass


class TimePath(Plot,Subscriber):
    """View showing  x-y observations with points in neighoring time periods
    connected with lines.


    """
    ntp = 0
    def __init__(self,name,master,x,y,t,xDelimiter=None,yDelimiter=None,title=None,
                 xLabel=None, yLabel=None, xDecimal=None, yDecimal=None,
                 ovalFill=None, ovalBorder=None,csIds=[],tsLabels=[],xPop='X',yPop='Y'):
        """Constructor


        name (string): name of view
        master (Tk.Toplevel): toplevel window view lives inside
        x (list): values for x variable
        y (list): values for y variable
        t (int): time period id ? XXX
        xDelimiter (?): XXX
        yDelimiter (?): XXX
        title (string): title for toplevel window
        xLabel (string): label for x axis
        yLabel (string): label for y axis
        xDecimal (?): XXX
        yDecimal (?): XXX
        xDecimal (?): XXX
        yDelimiter (?): XXX
        ovalFill (?): XXX
        ovalBoarder (?): XXX
        xPop (?): XXX
        yPop (?): XXX
        """
        self.type = "timePath"
        self.name = name
        self.master = master
        self.xLabel = xLabel
        self.yLabel = yLabel
        self.xDelimiter = xDelimiter
        self.yDelimiter = yDelimiter
        self.title= title
        self.t = t
        self.tsLabels = tsLabels
        self.Type="Time Plot"
        self.xDecimal = xDecimal
        self.yDecimal = yDecimal
        self.labelDict = {}
        self.titleOnCanvas = 0
        self.ovalFill = ovalFill
        self.ovalBorder = ovalBorder
        self.timepathString = "Time Path"
        self.setTitle(self.timepathString)
        Plot.__init__(self,name,master,x,y,xDelimiter=None,yDelimiter=None,title=self.title,
                      xLabel=None, yLabel=None, xDecimal=None, yDecimal=None,
                      ovalFill=None, ovalBorder=None,xPop=xPop,yPop=yPop)
        
        
        self.canvas.pack(side=LEFT,anchor=W)
        self.matcher = ITimePath(xVariableName=xLabel,xValues=x,
                                 yVariableName=yLabel,
                                 yValues=y,
                                 t=self.t ,
                                 cs=csIds )
        TimePath.ntp +=1
        self.name = "tp_%d"%TimePath.ntp
        self.top.title(self.title)
        Subscriber.__init__(self,self.observer)
            
    def mouseLeftButtonRelease(self,event):
        """
        Overrides View Method.
        """
        stat='coords:'+str(event.x)+','+str(event.y)
        if self.interactionMode:
            self.lastx  = self.canvas.canvasx(event.x)
            self.lasty  = self.canvas.canvasy(event.y)
            x1 = self.startx
            x2 = self.lastx
            y1 = self.starty
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()
            oid = self.canvas.find_overlapping(x1,y1,x2,y2)
            self.selectedIds = self.cleanWidgetIds(oid)
            ids = self.getIdsForWidgets(self.selectedIds)
            newObs = self.matcher.getObsforIds(ids)
            commandKey = self.modButton+self.interactionModeString
            try:
                originCommand = ORIGINCOMMANDS[commandKey]
                if newObs:
                    self.dispatch(originCommand,ids)
                    self.publish(originCommand,newObs)
                self.cursorReset()
            except:
                pass
            
    def mouseMiddleButton(self,event):
        """
        Overrides View Method.
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
        cid = self.widget2Id[wid]
        observation = self.matcher.observations[cid]
        ts = str(observation.ts)
        varNames = observation.variable
        values = observation.value
        csString = 'cross-section id: ' + str(cid) + '\n'
        tsString = 'time-series id: ' + ts + '\n'
        xString = self.xPop + " = " + str(values[0]) + '\n'
        yString = self.yPop + " = " + str(values[1])
        label = csString+tsString+xString+yString
        self.highlightSingleWidget(wid)
        self.tLabel = Label(self.canvas,text=label,bg='Yellow',font=('Times', options.AXISFONTSIZE))
        self.tempWID = wid
        if self.lastx < self.xMidPoint:
            self.identLabel = self.canvas.create_window(self.lastx+3, self.lasty, anchor=W, window=self.tLabel)
        else:
            self.identLabel = self.canvas.create_window(self.lastx-3, self.lasty, anchor=E, window=self.tLabel)

    def mouseMiddleRelease(self,event):
        """
        Overrides View Method.
        """
        self.unhighlightSingleWidget(self.tempWID)
        self.canvas.delete(self.tLabel)
        self.canvas.delete(self.identLabel)

    def draw(self):
        """
        Overrides View Method.
        """
        self.genericTimeSign()
        self.setOvalColors()
        self.scaleBox()
        self.getMinMax()
        self.getRanges()
        self.getRatios()
        self.makeXTicks()
        self.makeYTicks()
        self.makeTickLabels()
        self.scaleTicks()
        self.scalePoints()
        self.drawOuterBox()
        self.drawAxis()
        self.drawTicks()
        self.drawTimeLinks()
        self.drawPoints()  
        self.drawXLabel()
        self.drawYLabel()

    def genericTimeSign(self):
        """
        Creates a list of strings with time labels.
        """
        if len(self.tsLabels) == 0:
            self.intervalList = ["T("+str(i)+")" for i in self.t]
        else:
            self.intervalList = self.tsLabels    
        
    def drawTimeLinks(self):
        """
        Connects time points with lines.
        """
        c = 0
        for i in self.scaledXCords[0:-1]:
            xOrigin = i
            xDest = self.scaledXCords[c+1]
            yOrigin = self.scaledYCords[c]
            yDest = self.scaledYCords[c+1]
            g = self.drawLine(xOrigin, yOrigin, xDest, yDest, 1)
            c = c+1
            
    def drawPoints(self):
        """
        Overrides Plot Method
        """
        self.id2Widget = {}
        self.widget2Id = {}
        self.idInfo = {}
        self.origColors = {}
        self.pointXY = {}
        c = 0
        for i in self.scaledXCords:
            x1 = i
            y1 = self.scaledYCords[c]
            x1 = x1-options.NEGATIVEOVAL
            y1 = y1-options.NEGATIVEOVAL
            x2=x1+options.POSITIVEOVAL
            y2=y1+options.POSITIVEOVAL
            g = self.canvas.create_oval(x1,y1,x2,y2,outline=self.ovalBorder, fill=self.ovalFill)
            self.origColors[g] = self.ovalFill
            self.id2Widget[c] = g
            self.widget2Id[g] = c
            self.idInfo[c] = [self.x[c], self.y[c], self.intervalList[c]] #actual x,y vals for tags
            self.pointXY[g] = (i,self.scaledYCords[c])
            c = c+1
        self.widgetKeys = self.widget2Id.keys()
        sWids = sort(self.widgetKeys)
        self.startWidget = sWids[0]
        self.finishWidget = sWids[-1]
        self.canvas.itemconfigure(self.startWidget,fill=options.HIGHLIGHTSTART)
        self.canvas.itemconfigure(self.finishWidget,fill=options.HIGHLIGHTFINISH)

    def selectedObservations(self,observations):
        """
        Overrides View method.
        """
        ids = observations
        self.matcher.select(ids)
        wids = self.getWidgetsForIds(ids)
        self.highlightWidget(wids)

    def newSelectedObservations(self,observations):
        """
        Overrides View method.
        """
        ids = observations
        self.unHighlightWidget()
        self.matcher.deselect()
        self.renewEndPoints()
        self.matcher.select(ids)
        self.highlightWidget(self.getWidgetsForIds(ids))
        timeIds = self.getWidgetsForIds(ids)
        ts = sort(timeIds)
        wid = ts[0]
        xy = self.pointXY[wid]
        self.canvas.delete("tsline")
        self.canvas.create_oval(xy[0]-4,xy[1]-4,xy[0]+4,xy[1]+4,outline='red',tag=("tsline"))
        
    def changeInteractionMode(self,mode):
        """
        Overrides Plot method.
        """
        self.interactionVar.set(mode)
        self.interactionMode = mode
        self.interactionModeString = INTERACTIONMODES[mode]
        self.unHighlightWidget()
        self.matcher.deselect()
        self.renewEndPoints()
        self.canvas.delete("tsline")

    def renewEndPoints(self):
        """
        Color start and end points.
        """
        self.canvas.itemconfigure(self.startWidget,fill=options.HIGHLIGHTSTART)
        self.canvas.itemconfigure(self.finishWidget,fill=options.HIGHLIGHTFINISH)

    def brushedObservations(self,observations):
        """
        Overrides View method.
        """
        ids = observations
        self.matcher.select(ids)
        self.brushWidget(self.getWidgetsForIds(observations))

    def brushObservations(self,observations):
        """
        Overrides View method.
        """
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.brushWidget(wids)
        compids = [j for j in self.IDS if ids.count(j) == 0]
        xvals = array([self.scaledXCords[i] for i in compids])
        yvals = array([self.scaledYCords[i] for i in compids])

    def newBrushedObservations(self,observations):
        """
        Overrides View method.
        """
        self.unHighlightWidget()
        self.matcher.deselect()
        self.renewEndPoints()
        self.matcher.select(observations)
        self.brushWidget(self.getWidgetsForIds(observations))
    
    def fitLine(self):
        """
        Overrides Plot method.
        """
        pass
        
    def unhighlightSingleWidget(self,widget):
        """
        Overrides View method.
        """
        if widget == self.startWidget:
            self.canvas.itemconfigure(widget,fill=options.HIGHLIGHTSTART)
        elif widget == self.finishWidget:
            self.canvas.itemconfigure(widget,fill=options.HIGHLIGHTFINISH)
        else:
            self.canvas.itemconfigure(widget,fill=options.DEFAULTOVALFILL)
        
    def updateTime(self,tsId):
        """
        Overrides View method.
        """
        if len(self.matcher.selected) == 1:
            oldWidget = self.id2Widget[self.matcher.selected[0]]
            self.unhighlightSingleWidget(oldWidget)
            self.matcher.deselect()
        else:
            self.unHighlightWidget()
            self.matcher.deselect()
        self.matcher.selectSingle(tsId)
        self.highlightSingleWidget(self.id2Widget[tsId])
        xy = self.pointXY[self.id2Widget[tsId]]
        self.canvas.delete("tsline")
        self.canvas.create_oval(xy[0]-4,xy[1]-4,xy[0]+4,xy[1]+4,outline='red',tag=("tsline"))

    def updateTime2Time(self, timeId):
        """
        XXX special time handler?
        """
        if len(self.matcher.selected) == 1:
            oldWidget = self.id2Widget[self.matcher.selected[0]]
            self.unhighlightSingleWidget(oldWidget)
            self.matcher.deselect()
        else:
            self.unHighlightWidget()
            self.matcher.deselect()
        self.matcher.selectSingle(timeId[0])
        self.highlightSingleWidget(self.id2Widget[timeId[0]])
        xy = self.pointXY[self.id2Widget[timeId[0]]]
        self.canvas.delete("tsline")
        self.canvas.create_oval(xy[0]-4,xy[1]-4,xy[0]+4,xy[1]+4,outline='red',tag=("tsline"))

    def travel(self):
        """
        Handles travel signal.
        """
        sortedKeys = self.matcher.observationKeys
        sortedKeys.sort()
        for key in sortedKeys:
            obs = self.matcher.observations[key]
            if len(self.matcher.selected) == 1:
                wid2Delete = self.id2Widget[self.matcher.selected[0]]
                self.unhighlightSingleWidget(wid2Delete)
            self.canvas.update()
            self.updateTime(obs.ts[0])
            self.publish("travel",obs.ts)
            for it in range(50):
                self.canvas.update()

        self.linkingMode()
                
    def buildMethods(self):
        # only methods that are to be accessed by observer go in here.
        m={"selectedObservations":self.selectedObservations,
           "selectObservations":self.selectObservations,
           "newSelectedObservations":self.newSelectedObservations,
           "newSelectObservations":self.newSelectObservations, 
           "brushedObservations":self.brushedObservations,
           "brushObservations":self.brushObservations,
           "newBrushedObservations":self.newBrushedObservations,
           "newBrushObservations":self.newBrushObservations,
           "updateTime":self.updateTime,
           "updateTime2Time":self.updateTime2Time,
           "travel":self.travel
           }
        self.methods=m

class Map(View,Subscriber):
    """Implements different Map Views."""
    nmap = 0
    def __init__(self,name,master,coords,values,varName,t,poly2cs,cs2poly,
                 width=None,height=None,title=None,classification="percentile",
                 nBins=5,bins=[],legend=1,legendType="sequential"):
        """Constructor.

        name (string): name of View
        master (Tk.Toplevel): toplevel application window
        coords (list): of lists of coordinates
        values (list): list of values to map
        varName (string): name of variable to map
        t (int): time period id
        poly2cs (dict): key is polygonId, values are cross-sectional ids
            associated with that polygon
        cs2poly (dict): key is csid, values are polygon ids associated with
            that cross-sectional id
        width (float): width of view XXX should be moved up a class
        height (float): height of view XXX should be moved up a class
        title (string): map title
        classification (string): name of classification method for legend
        nbins (int): number of bins for legends
        bins (list): of cut-off values for bins
        legend (int): 1=legend on, other, legend off
        legendType (string): type of legend, used to select colorscheme
        """
        self.classification = classification
        self.nBins = nBins
        self.bins = bins
        self.values = values
        self.coords = coords
        self.poly2cs = poly2cs
        self.cs2poly = cs2poly
        self.mapString = 'Map'
        self.varName = varName
        self.legendTitle = varName
        self.legend = 2 # 1=left,2=right, 0 = off
        self.tsIds = t
        self.legendType = legendType

        # XXX kludge prior to refactoring post release
        if legendType == "qualitative":
            self.classification = "uniqueValues"
        Map.nmap +=1
        View.__init__(self,Map.nmap,master,width=None,height=None,title=None)
        self.canvas.pack(side=LEFT,anchor=W)
        self.centroidsOn = 0
        self.matcher = IMap(varName,values,t,poly2cs,cs2poly)
        self.type="map"
        self.values = values
        Map.nmap +=1
        self.title = "map_%d"%Map.nmap
        self.name= "map_%d"%Map.nmap
        self.top.title(name)
        Subscriber.__init__(self,self.observer)
        self.varName = varName
        self.canvas.bind("<Control-c>",self.toggleCentroids)
        self.canvas.bind("<Control-Shift-T>",self.brushTravelE)

    
    def highlightWidget(self,widgetIds):
        """
        highlight widgets on view.

        widgetids (list): integer ids
        """
        #print widgetIds
        for widget in widgetIds:
            self.canvas.tkraise(widget) 
            self.canvas.itemconfigure(widget,outline='Yellow')
            #self.canvas.itemconfigure(widget,outline='Yellow',stipple='gray25')

    def unhighlightSingleWidget(self,widget):
        """
        unhighlight a single widget

        widget (int): widget id
        """
        self.canvas.itemconfigure(widget,outline=options.DEFAULTOVALFILL)

    def unHighlightWidget(self,widgetIds=[]):
        """
        unhighlight specific (or all) widgets

        widgetIds (list): of ints widget ids
        """
        if widgetIds == []:
            ids = self.matcher.selected
            wids = self.getWidgetsForIds(ids)
            widgetIds = wids
        for widget in widgetIds:
            if self.origColors.has_key(widget):
                color = self.origColors[widget]    
                self.canvas.itemconfigure(widget,outline='black')
                self.canvas.itemconfigure(widget,fill=color)



    def toggleCentroids(self,event):
        """turn centroids on or off"""
        if self.centroidsOn:
            self.deleteCentroids()
            self.centroidsOn = 0
        else:
            self.drawCentroids()
            self.centroidsOn = 1

    def editMenu(self):
        """edit menu for view specific menu"""
        self.legendMode = IntVar()
        self.legendMode.set(self.legend)
        choices = Menu()
        pulldown = Menu()
        choices.add_command(label="Labels",
        underline=0,command=self.changeTextOnCanvas)
        self.menu.add_separator()
        self.menu.add_cascade(label='Edit',underline=0,menu=choices)
        pulldown.add_radiobutton(label="Off",underline=0,command=self.changeLegend,
            variable = self.legendMode,value=0)
        pulldown.add_radiobutton(label="Left",underline=0,command=self.changeLegend,
            variable = self.legendMode,value=1)
        pulldown.add_radiobutton(label="Right",underline=0,command=self.changeLegend,
            variable = self.legendMode,value=2)
        self.menu.add_separator()
        self.menu.add_cascade(label='Legend',underline=0,menu=pulldown)

    def changeLegend(self):
        """change and add the legend"""
        self.legend = self.legendMode.get()
        self.addLegend()

    def drawCentroids(self):
        """plot polygon centroids"""
        for centroid in self.centroids.keys():
            x,y = self.centroids[centroid]
            self.canvas.create_oval(x-2,y-2,x+2,y+2,fill="GREEN",tag=("CENTROID"))

    def deleteCentroids(self):
        """delete polygon centroids"""
        self.canvas.delete("CENTROID")
    
    def highlightCentroid(self, id):
        """highlight centroid

        id (int): polygon id
        """
        csId = self.poly2cs[id][0]
        x,y = self.centroids[csId]
        #self.canvas.create_oval(x-3,y-3,x+3,y+3,fill="Yellow",outline='Red',tag=("bigCentroid"))

    def brushCentroid(self, id):
        """brush centroid

        id (int): polygon id
        """
        csId = self.poly2cs[id][0]
        x,y = self.centroids[csId]
        #self.canvas.create_oval(x-3,y-3,x+3,y+3,fill="Red",outline='Yellow',tag=("bigCentroid"))

    def brushWidget(self,widgetIds):
        """
        brush widgets with widgetIds. Overriding so map fill is not obscured

        widgetIds (list): of ints widget ids
        """
        for widget in widgetIds:
            self.canvas.tkraise(widget)
            self.canvas.itemconfigure(widget,outline=options.BRUSHCOLOR)


    def unhighlightCentroids(self):
        """unhighlight all centroids"""
        self.canvas.delete("bigCentroid")
         
    def draw(self):
        """Override Plot Method"""
        self.binData()
        origColors = self.binIds

        self.setTitle(self.mapString)
        #self.scaleCoords()
        #self.canvas.create_text(self.width/2.,self.height/2.,text=self.name,tag="name")
        cic=0
        self.widget2Id = {}
        self.id2Widget = {}
        self.origColors = {}
        self.poly2widget = {}
        self.widget2poly = {}
        self.polyLabel2Id = {}
        polyKeys = self.coords.keys()
        polyKeys = sort(polyKeys)
        for polyKey in polyKeys:
            ci = cic%6
            polyId = "poly%d"%cic
            csId = self.poly2cs[polyKey]
            #print csId
            colorId = origColors[csId]
            color = self.mapColors[colorId]
            try:
                color = self.mapColors[colorId]
            except:
                color = "Black" 
            p=self.canvas.create_polygon(self.coords[polyKey],fill=color,outline='black',tags=("MAPITEM",polyId))
            self.origColors[p] = color
            cic = self.poly2cs[polyKey][0]
            self.polyLabel2Id[p] = csId[0]
            self.widget2Id[p] = cic 
            self.poly2widget[polyKey] = p
            self.widget2poly[p] = polyKey
            if self.id2Widget.has_key(cic):
                self.id2Widget[cic].append(p)
            else:
                self.id2Widget[cic] = [p]
            cic+=1
        self.widgetKeys = self.widget2Id.keys()
        self.canvas.tag_bind("MAPITEM", "<Control-1>")
        self.xMidPoint = self.width/2.

    def binData(self):
        """Classify data for legend on map"""
        xa = array(self.values)
        #print min(xa),max(xa)
        classResults = classifier.Classifier(xa,
                                             method=self.classification,
                                             nBins=self.nBins,
                                             bins=self.bins)
        self.binCounts = classResults.binCounts
        self.legendBounds = classResults.bins
        self.binIds = classResults.binIds
        try:
            self.canvas.delete("legend")
        except:
            pass
        n = len(self.legendBounds)
        #print self.legendType,self.classification
        self.mapColors = getColors(self.legendType,n)
        self.addLegend()

    def addLegend(self):
        self.canvas.delete("legend")
        if self.legend:
            # get binInfo
            bCounts = self.binCounts
            bins = self.legendBounds
            ids = range(len(bCounts))
            n=len(bins)
            rn = range(n)
            lstrings= [ "  %.3f (%d)"%(bins[i],bCounts[i]) for i in rn ] 
            fontSize = options.AXISFONTSIZE 
            fontType = "Times"
            FONTCHECK= tkFont.Font(family=fontType, size=fontSize)
            maxWidth=max([FONTCHECK.measure(s) for s in lstrings])


            titleString = self.legendTitle 
            legendType = self.classification

            titleWidth=FONTCHECK.measure(titleString)
            if titleWidth > maxWidth:
                maxWidth = titleWidth


            nEntries = n
            topPos = (fontSize+1) * (nEntries+1)
            topPos = self.height - topPos
            maxY = topPos
            rightEdge = self.width - maxWidth
            lpos = rightEdge
            cv=self.canvas
            cv.create_text(lpos,topPos-2,text=titleString,anchor=E,
                           font=(fontType,fontSize),
                           tag=("legend","legText"))

            recUp = fontSize/2.
            topPos = topPos + fontSize + 1


            recR = rightEdge - 6
            recL = recR - fontSize



 
            cv = self.canvas
            for i in rn:
                x0 = lpos 
                y0 = topPos - recUp
                y1 = topPos + recUp
                cv.create_rectangle(recL,y0,recR,y1,tag=("legend"),
                    fill=self.mapColors[i])
                x0 = recL - 3
                cv.create_text(x0,topPos,text=lstrings[i],
                    anchor=E,font=(fontType,fontSize),
                               tag=("legend","legText"))
                topPos += fontSize + 1

            topPos = (fontSize+1) * (nEntries+1)
            topPos = self.height - topPos
            topPos = topPos + fontSize + 1
            cv.create_text(recR+2,topPos,text=legendType,
                           anchor=W,font=(fontType,fontSize),
                           tag=("legend", "legText"))

            cv.tag_bind("legend", "<1>", self.lmouseDown)
            cv.tag_bind("legend", "<B1-Motion>",self.lmouseMove)
            cv.tag_bind("legend", "<Any-Enter>",self.lmouseEnter)
            cv.tag_bind("legend", "<Any-Leave>",self.lmouseLeave)
        else:
            pass


    def lmouseDown(self,event):
        """handler for legend movement"""
        self.llastx = event.x
        self.llasty = event.y

    def lmouseMove(self,event):
        self.canvas.move("legend", event.x - self.llastx, event.y - self.llasty)
        self.llastx = event.x
        self.llasty = event.y

    def lmouseEnter(self,event):
        self.canvas.itemconfig("legText", fill='green')

    def lmouseLeave(self,event):
        self.canvas.itemconfig("legText", fill='black')



    def addLegend1(self):
        """Add map legend"""
        self.canvas.delete("legend")
        if self.legend:
            # get binInfo
            bCounts = self.binCounts
            bins = self.legendBounds
            ids = range(len(bCounts))
            n=len(bins)
            mv = max(self.values)
            if mv < 10.:
                fmt = "%.3f"
                dec = 3
            elif mv < 1000.:
                fmt = "%.1f"
                dec = 1
            else:
                fmt = "%.0f"
                dec = 0

            # kludge for qualitative map
            if self.legendType == "qualitative":
                fmt = "%.0f"
                dec = 0


            # get largest bin with nonzero count
            maxNzId = max(compress(greater(bCounts,0),ids))+1
            fontType = "Times"
            if maxNzId < 9:
                fontSize = options.AXISFONTSIZE 
            else:
                fontSize = options.AXISFONTSIZE - 2 
            FONTCHECK= tkFont.Font(family=fontType, size=fontSize)

        
            boundMax = max(bins)
            countMax = max(bCounts)

            maxString = len(fmt%boundMax)
            maxCountString = len("%d"%countMax)

            # get maximum width entry

            formatS = "%"+str(maxString)+"."+str(dec)+"f"
            formatC = "%"+str(maxCountString)+"d"
            countStrings=[formatC%binCount for binCount in bCounts]
            boundStrings=[formatS%bound for bound in bins]
            titleString  = self.legendTitle
            titleWidth = FONTCHECK.measure(titleString)
            countWidth = FONTCHECK.measure(maxCountString)
            binWidth   = FONTCHECK.measure(maxString)
            maxCountString = len("%d"%countMax)
            maxElen = fontSize/2 + countWidth + binWidth + 6
            if titleWidth > maxElen:
                maxElen = titleWidth

            if self.legend == 1:
                rightEdge = 20 + maxElen
            else:
                #totalWidth = maxElen + 2 * (fontSize + 2) + countWidth+2
                rightEdge = self.width - 20
            #print rightEdge

            maxl = rightEdge-maxElen

            nEntries = n
            rn = range(n)
            topPos = (fontSize+1) * (nEntries + 1)
            topPos = self.height - topPos
            maxY = topPos
            lpos = rightEdge
            self.canvas.create_text(lpos,topPos-2,text=titleString,anchor=E,
                font=(fontType,fontSize),tag=("legend"))
            recUp = fontSize/2.
            topPos = topPos + fontSize + 1

            recR = lpos - countWidth - 6 
            recL = recR - fontSize 
 
            cv = self.canvas
            for i in rn:
                countString = countStrings[i]
                boundString = boundStrings[i]
                x0 = lpos 
                cv.create_text(x0,topPos,text=countString,
                    anchor=E,font=(fontType,fontSize),tag=("legend"))
                y0 = topPos - recUp
                y1 = topPos + recUp
                cv.create_rectangle(recL,y0,recR,y1,tag=("legend"),
                    fill=self.mapColors[i])
                x0 = recL - 3
                cv.create_text(x0,topPos,text=boundString,
                    anchor=E,font=(fontType,fontSize),tag=("legend"))
                topPos += fontSize + 1

        else:
            pass
      
    def mouseLeftButtonRelease(self,event):
        """Override View method"""
        stat='coords:'+str(event.x)+','+str(event.y)
        if self.interactionMode:
            self.lastx  = self.canvas.canvasx(event.x)
            self.lasty  = self.canvas.canvasy(event.y)
            x1 = self.startx
            x2 = self.lastx
            y1 = self.starty
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()
            oid = self.canvas.find_overlapping(x1,y1,x2,y2)
            self.selectedIds = self.cleanWidgetIds(oid)
            ids = self.getIdsForWidgets(self.selectedIds)
            #print "map",oid, self.selectedIds,id
            newObs = self.matcher.getObsforIds(ids)
            commandKey = self.modButton+self.interactionModeString
            originCommand = ORIGINCOMMANDS[commandKey]
            if newObs:
                self.dispatch(originCommand,newObs)
                self.publish(originCommand,newObs)
            else:
                self.unhighlightCentroids()
            self.cursorReset()

    def newSelectedObservations(self,observations):
        """Override View method XXX how so?"""
        self.newSelectObservations(observations)

    def newSelectObservations(self,observations):
        """Override View method XXX how so?"""
        self.unHighlightWidget()
        self.unhighlightCentroids()
        self.matcher.deselect()
        self.selectObservations(observations)

    def selectObservations(self,observations):
        """Override View method"""
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.highlightWidget(wids)
        for id in ids:
            self.highlightCentroid(id)
        
    def newBrushObservations(self,observations):
        """Override View method XXX how so?"""
        self.unHighlightWidget()
        self.unhighlightCentroids()
        self.matcher.deselect()
        self.brushObservations(observations)

    def brushObservations(self,observations):
        """Override View method"""
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        #print 'brushing in map'
        self.brushWidget(wids)
        for id in ids:
            self.brushCentroid(id)
            #self.canvas.itemconfigure(widget,fill=color)

   
    def changeInteractionMode(self,mode):
        """Override View method XXX how so?"""
        self.interactionVar.set(mode)
        self.interactionMode = mode
        self.interactionModeString = INTERACTIONMODES[mode]
        self.clearAll()
        self.unhighlightCentroids()

    def getIdsForWidgets(self,widgetIds):
        """Override View method XXX how so?"""
        # maps widget ids to observation ids
        # overridden from view
        matchedIds = []
        for wid in widgetIds:
            polyid = self.widget2poly[wid]
            matchedIds.append(polyid)
        return matchedIds


    def getWidgetsForIds(self,ids):
        """Override View method."""
        matchedIds = []
        for id in ids:
                wid = self.poly2widget[id]
                matchedIds.append(wid)
        return matchedIds

    def travel(self):
        """Override View method."""
        values = self.values
        n=len(values)
        ids = argsort(values)
        self.clearAll()
        for i in ids:
            polyIds = self.id2Widget[i]
            if i == ids[-1]:
                pass
                #print i,ids[-1]
            for polyId in polyIds:
                origColor = self.canvas.itemcget(polyId,"fill")
                self.canvas.update()
                self.matcher.deselect()
                self.matcher.selected = [self.widget2poly[polyId]]
                pid = self.matcher.selected
                pid = pid[0]
                self.highlightCentroid(pid)
                mobs = self.matcher.getSelected()
                self.publish("travel",mobs)
            for it in range(5):
                for polyId in polyIds:
                    self.canvas.itemconfigure(polyId,fill="Yellow")
                    self.canvas.update()
                time.sleep(0.05)
                for polyId in polyIds:
                    self.canvas.itemconfigure(polyId,fill=origColor)
                    self.canvas.update()
                time.sleep(0.05)
            self.unhighlightCentroids()
        # keep last observation highlighted/selected
        self.matcher.deselect()
        self.newSelectObservations(mobs)

        self.linkingMode()

    def brushTravelE(self,event):
        """Override View method"""
        self.brushTravelMode()

    def brushTravel(self):
        """Override View method"""
        values = self.values
        n=len(values)
        ids = argsort(values)
        # need to only signal for unique cs ids not every polygon,
        # otherwise multi-polygon cs units signal too many times.
        for i in ids:
            polyIds = self.id2Widget[i]
            signalId = polyIds[0]
            self.clearAll()

            self.matcher.selected = [ self.widget2poly[signalId] ]
            pid = self.matcher.selected
            pid = pid[0]
            self.brushCentroid(pid)
            mobs = self.matcher.getSelected()
            for polyId in polyIds:
                origColor = self.canvas.itemcget(polyId,"fill")
                self.canvas.update()
            for it in range(5):
                for polyId in polyIds:
                    self.canvas.itemconfigure(polyId,fill=options.BRUSHCOLOR)
                    self.canvas.update()
                time.sleep(0.05)
                for polyId in polyIds:
                    self.canvas.itemconfigure(polyId,fill=origColor)
                    self.canvas.update()
                time.sleep(0.05)
            self.unhighlightCentroids()
            self.publish("brushTravel",mobs)
        #keep last polygons highlighted
        self.matcher.deselect()
        self.unhighlightCentroids()
        self.brushObservations(mobs)

    def redraw1(self,tsId):
        """Override View method XXX how so?"""
        self.values.reverse()
        t = tsId
        self.canvas.delete('all')
        self.draw()



class Histogram(Plot,Subscriber):
    """Histogram View"""
    nmhist = 0
    def __init__(self,name,master,x,y,xDelimiter=None,yDelimiter=None,title=None,
        xLabel=None, yLabel=None, xDecimal=None,yDecimal=None,  
        ovalFill=None, ovalBorder=None, csIds = [], tsIds = [],
        xPop='X',yPop='Observations in set',
        classification="sturges",nBins=5,bins=[]):
        """Constructor.
        name (string): name of view
        master (Tk.Toplevel): top level window view lives in
        x (?):
        y (?):
        xDelimeter (?):
        yDelimeter (?):
        title (?):
        xLabel (?):
        yLabel (?):
        xDecimal (?):
        yDelimiter (?):
        ovalFill (?):
        ovalBoarder (?):
        method (string): uses Classifier Class
        nBins (integer): number of bins
        bins (list): list of bin boundaries for User Defined Bins
        csIds (list): list of cs ids associated with values XXX is this right?
        tsIds (list): list of ts ids associated with values XXX is this right?
        xPop (?):
        yPop (?):
        """
        self.name = name
        self.master = master
        self.xLabel = xLabel
        self.x = x
        self.y = y
        self.yLabel = yLabel
        self.genericY = 'Number of Observations'
        self.xDelimiter = xDelimiter
        self.yDelimiter = yDelimiter
        self.genericString = 'Histogram'
        self.title= title
        self.labelDict = {}
        self.titleOnCanvas = 0
        self.type="histogram"
        self.xDecimal = xDecimal
        self.yDecimal = yDecimal
        self.ovalFill = ovalFill
        self.ovalBorder = ovalBorder
        self.histoString = 'Histogram'
        self.setTitle(self.histoString)
        print "BINS", nBins
        
        self.matcher = IHistogram(self.xLabel,self.x,tsIds,csIds,
        classification=classification,nBins=nBins,bins=bins)

        Plot.__init__(self,name,master,x,y,xDelimiter=None,yDelimiter=None,title=self.title,
                      xLabel=None, yLabel=None, xDecimal=None, yDecimal=None,
                      ovalFill=None, ovalBorder=None,xPop=xPop,yPop=yPop)
        self.canvas.pack(side=LEFT,anchor=W)
                                
        Histogram.nmhist +=1
        self.name = "hist_%d"%Histogram.nmhist
        
        Subscriber.__init__(self,self.observer)
        self.selected = []
   
    def draw(self):
        """Override Plot method"""
        self.setOvalColors()
        self.scaleBox()
        self.rescaleBox()
        self.createBins()
        self.getSlices()
        self.makeXTicks()
        self.makeYTicks()
        self.makeTickLabels()
        self.scaleTicks()
        self.drawOuterBox()
        self.drawAxis()
        self.drawTicks()
        if self.yLabel:
            pass
        else:
            self.yLabel = self.genericY
        self.drawYLabel()
        self.drawXLabel()
        self.drawSlices()
        
    def rescaleBox(self):
        """X axis buffer is larger for box widths"""
        self.x1Buffer = (self.width * options.BUFFERBOXPLOTS[0]) - 10
        self.x0Buffer = (self.width * options.BUFFERBOXPLOTS[1]) + 10
        self.xMidPoint = (self.x0Inner + self.x1Inner) / 2

    def createBins(self):
        """Combines getMinMax, getRanges, getRatios for X only"""
        self.binInfo = self.y
        self.MaxX = max(self.x) 
        self.MinX = min(self.x) 
        self.xRangeValues = self.MaxX - self.MinX
        self.xIntegerRange = arange(self.MinX, self.MaxX+1)
        self.bins = self.matcher.bins
        self.bounds = self.matcher.bounds
        self.numberOfBins  = len(self.bins.keys())
        
        self.binKeys = self.bins.keys()
        self.binVolumes = {}
        for i in self.binKeys:
            self.binVolumes[i] = len(self.bins[i])
        self.MaxY = max(self.binVolumes.values()) 
        self.MinY = 1
        self.yRangeValues = float(self.MaxY) - float(self.MinY)
        self.yIntegerRange = range(self.MinY, self.MaxY+1)
        self.yratio = (self.y1Buffer - self.y0Buffer) / self.yRangeValues

        self.MaxXBins = float(len(self.binKeys)) 
        self.MinXBins = 1.0
        self.xRangeValuesBins = self.MaxXBins - self.MinXBins
        self.xIntegerRangeBins = arange(self.MinXBins, self.MaxXBins+1)
        self.xratio = (self.x1Buffer - self.x0Buffer) / self.xRangeValuesBins
        
    def getSlices(self):
        """XXX not sure?"""
        self.newMaxBinPix = self.y0Inner - self.y1Buffer
        self.slices = self.newMaxBinPix / self.MaxY
        
    def makeXTicks(self):
        """Create labels for x ticks"""
        self.xTicks = [] # empty list for final x delims
        self.newXPixels = self.x1Buffer - self.x0Buffer
        if self.xDelimiter == None:
            self.xTicks.append(self.x0Buffer)
            boxWidth = self.newXPixels / self.numberOfBins
            numberXBreaks = range(1, self.numberOfBins)
            for i in numberXBreaks:
                t = self.x0Buffer + (float(i) * boxWidth) 
                self.xTicks.append(t)
            self.xTicks.append(self.x1Buffer)
        elif len(self.xDelimiter) == 1:
            ints = self.xDelimiter[0]
            numberXBreaks = range(1, ints+1)
            for i in numberXBreaks:
                t = float(i) / numberXBreaks[-1]
                xBreaks.append(t)
            for i in xBreaks:
                self.xTicks.append(self.MinX + (self.xTickInterval * i))
            self.xTicks.append(self.MinX)
        else:
            self.xTicks = self.xDelimiter[0:]
 
    def makeYTicks(self):
        """Create labels for y ticks"""
        self.yTickInterval = self.yIntegerRange[-1] 
        self.yTicks = []
        yBreaks = []
        if self.yDelimiter == None: 
            ticks = 5
            ints = ceil(self.yTickInterval / ticks)
            if ints <= 1:
                ints = 2
            for i in self.yIntegerRange:# 4 lines diff view.py
                g = float(i) % ints
                if g == 0:
                    self.yTicks.append(i) 
        elif len(self.yDelimiter) == 1:
            ints = self.yDelimiter[0]
            numberYBreaks = range(1, ints+1)
            for i in numberYBreaks:
                t = float(i) / numberYBreaks[-1]
                yBreaks.append(t)
            for i in yBreaks:
                self.yTicks.append(self.MinY + (self.yTickInterval * i))
            self.yTicks.append(self.MinY)
        else:
            self.yTicks = self.yDelimiter
        
    def makeTickLabels(self):
        """Format x and y labels create decimal places by default or for
        argument passed in."""
        if self.xDecimal:
            pass
        else:
            if self.MaxX < 10.0:
                self.xDecimal = 3
            else:
                self.xDecimal = 0
        if self.yDecimal:
            pass
        else:
            self.yDecimal = 0
        xTickLeft = [int(i) for i in self.bounds]
        tmp = [len(str(i)) for i in xTickLeft]
        self.xTickLeftMax = max(tmp)
        tmpX = "%"+str(self.xTickLeftMax)+"."+str(self.xDecimal)+"f"
        self.xTicksLabs = [tmpX %(i) for i in self.bounds]
        yTickLeft = [int(i) for i in self.yTicks]
        yTickLeft = [len(str(i)) for i in yTickLeft]
        self.yTickLeftMax = max(yTickLeft)
        tmpY = "%"+str(self.yTickLeftMax)+"."+str(self.yDecimal)+"f"
        self.yTicksLabs = [tmpY %(i) for i in self.yTicks]
        
    def scaleTicks(self):
        """Scale x and y axis ticks"""
        self.scaledXTicks = self.xTicks
        self.scaledYTicks = [self.y0Inner - (self.yTicks[x] * self.slices) for x in range(0,len(self.yTicks))]
        
    def drawTicks(self):
        """Draw ticks and value labels for X and Y axis"""
        stringLengths = []
        [stringLengths.append(len(i)) for i in self.xTicksLabs]
        [stringLengths.append(len(i)) for i in self.yTicksLabs]
        maxLabelLength = max(stringLengths)
        if maxLabelLength <= 6:
            self.axisFontSize = 8
        else:
            self.axisFontSize = 8
        c = 0
        midTick = (self.scaledXTicks[1] - self.scaledXTicks[0]) / 2
        if len(self.bounds) != len(self.binKeys):
            pass
        for i in self.scaledXTicks[0:-1]:
            mid = i + midTick  
            name = self.xTicksLabs[c]
            self.canvas.create_text(mid , self.y0Inner + 2, text=self.xTicksLabs[c], 
            font=('Times', options.AXISFONTSIZE), anchor = N)
            c = c+1

        c = 0
        for i in self.scaledYTicks:
            self.drawLine(self.x0Inner, i, self.x0Inner - 4, i, 1)
            self.canvas.create_text(self.x0Inner - 2, i-5, text=int(self.yTicksLabs[c]), 
            font=('Times', options.AXISFONTSIZE), anchor = E)
            c = c+1
            
    def drawSlices(self):
        """draws slices of each bin."""
        self.widget2Id = {}
        self.id2Widget = {}
        self.bin2Widget = {}
        self.widget2Bin = {}
        self.binSlices = {}
        self.highlightedBins = {}
        self.id2Bin = {}
        self.bin2Id = {}
        for i in range(len(self.scaledXTicks)-1):
            x0 = self.scaledXTicks[i]
            x1 = self.scaledXTicks[i+1]
            nSlices = self.binVolumes[i]
            y0Range = range(nSlices)
            y1Range = range(1, nSlices+1)
            self.bin2Widget[i] = []
            self.bin2Id[i] = []
            c = 0
            self.highlightedBins[i] = 0
            for j in y0Range:
                y0 = self.y0Inner - (self.slices * j)
                y1 = self.y0Inner - (self.slices * y1Range[j])
                g = self.canvas.create_rectangle(x0, y0, x1, y1,
                width=1, fill=options.DEFAULTOVALFILL,
                outline=options.DEFAULTOVALFILL)
                id = self.bins[i][c]
                self.widget2Id[g] = id
                self.id2Widget[id] = g
                self.bin2Widget[i].append(g)
                self.widget2Bin[g] = i
                self.id2Bin[id] = i
                self.bin2Id[i].append(id)
                self.binSlices[i] = []
                c = c+1
       
        self.widgetKeys = self.widget2Id.keys() 
                
    def getSlice2Highlight(self,csid):
        """find id's of slices to highlight to represent unit csid

        csid (int): cross-sectional id
        """
        originWidget = self.id2Widget[csid]
        bin = self.widget2Bin[originWidget]
        widgetList = self.bin2Widget[bin]
        actual = self.highlightedWidgets[bin]['actual']
        display = self.highlightedWidgets[bin]['display']
        c = len(display)
        if originWidget not in actual:
            displaySlice = widgetList[c]
            self.highlightedWidgets[bin]['actual'].append(originWidget)
            self.highlightedWidgets[bin]['display'].append(displaySlice)
            self.highlightSlice(displaySlice)
        else:
            displaySlice = widgetList[c-1]
            self.highlightedWidgets[bin]['actual'].remove(originWidget)
            self.highlightedWidgets[bin]['display'].remove(displaySlice)
            self.unhighlightSlice(displaySlice)

    def getSlice2Brush(self,csid):
        """find id's of slices to brush to represent unit csid

        csid (int): cross-sectional id
        """
        originWidget = self.id2Widget[csid]
        originWidget = self.id2Widget[csid]
        bin = self.widget2Bin[originWidget]
        widgetList = self.bin2Widget[bin]
        actual = self.highlightedWidgets[bin]['actual']
        display = self.highlightedWidgets[bin]['display']
        c = len(display)
        if originWidget not in actual:
            displaySlice = widgetList[-1 - c]
            self.highlightedWidgets[bin]['actual'].append(originWidget)
            self.highlightedWidgets[bin]['display'].append(displaySlice)
            self.brushSlice(displaySlice)
        else:
            displaySlice = widgetList[-c]
            self.highlightedWidgets[bin]['actual'].remove(originWidget)
            self.highlightedWidgets[bin]['display'].remove(displaySlice)
            self.unhighlightSlice(displaySlice)

    def brushSlice(self, slice):
        """brush slice

        slice (int): widget id/tag"""
        self.canvas.itemconfigure(slice,fill=HOLLOWCOLOR)


    def highlightSlice(self, slice):
        """highlight slice

        slice (int): widget id/tag"""
        self.canvas.itemconfigure(slice,fill=options.HIGHLIGHTCOLOR)

    def highlightMultiple(self, widgetList):
        """Highlight multiple widgets

        widgetlist (list): ids for widgets
        """
        for i in widgetList:
            self.canvas.itemconfigure(i,fill=options.HIGHLIGHTCOLOR)
        
    def brushMultiple(self, widgetList):
        """Brush multiple widgets

        widgetlist (list): ids for widgets
        """
        for i in widgetList:
            self.canvas.itemconfigure(i,fill=HOLLOWCOLOR)
            
    def unhighlightSlice(self, slice):
        """Unhighlight slice

        slice (int): slice id/tag"""
        self.canvas.itemconfigure(slice,fill=options.DEFAULTOVALFILL)

    def getUniqueBin(self, widgetList):
        """Find bin ids containing these widgets

        widgetList (list): of widget ids

        Returns:
        bins (list): of unique binIds.
        """

        bins = []
        for i in widgetList:
            g = self.widget2Bin[i]
            if g not in bins:
                bins.append(g)
        return bins

    def getBins2Widgets(self,bins):
        """Find widgets living in bins

        bins (list): of bin ids

        Returns:
        widgets2Highlight (list): of widgetIds
        """
        widgets2Highlight = []
        for bin in bins:
            wList = self.bin2Widget[bin]
            for widget in wList:
                widgets2Highlight.append(widget)
        return widgets2Highlight

    def getId2Widget(self,ids):
        """XXX why this? and not id2Widget"""
        widgets = []
        for i in ids:
            widgets.append(self.id2Widget[i])
        return widgets

    def getWidget2Id(self, widgets):
        """XXX why this? and not widget2Id"""
        ids = []
        for i in widgets:
            ids.append(self.widget2Id[i])
        return ids
        
    def mouseLeftButton(self,event):
        """Override View method"""
        print 'mouseLeftButton'
        self.modButton = "none" 
        x1=self.canvas.canvasx(event.x)
        x2=x1
        y1=self.canvas.canvasy(event.y)
        y2=y1
        if self.interactionMode !=0:
            self.createSelector([x1,y1,x2,y2])
        stat='coords:'+str(event.x)+','+str(event.y)
        tg=self.canvas.gettags('current')
        interactionVar = self.interactionVar.get()

        if self.selectedIds:
            self.canvas.delete("selector")
            self.unhighlightMultiple(self.selected)
            
        if self.interactionMode:
            self.canvas.delete(self.selectorRectangle)
            self.lastx = self.startx = self.canvas.canvasx(event.x)
            self.lasty = self.starty = self.canvas.canvasy(event.y)
            x1 = self.startx
            y1 = self.starty
            x2 = self.lastx
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()
            
    def mouseLeftButtonRelease(self,event):
        """Override View method"""
        stat='coords:'+str(event.x)+','+str(event.y)
        if self.interactionMode:
            self.lastx  = self.canvas.canvasx(event.x)
            self.lasty  = self.canvas.canvasy(event.y)
            x1 = self.startx
            x2 = self.lastx
            y1 = self.starty
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()
            oid = self.canvas.find_overlapping(x1,y1,x2,y2)
            self.selectedIds = self.cleanWidgetIds(oid)
            totalBins = self.getUniqueBin(self.selectedIds)
            totalWidgets = self.getBins2Widgets(totalBins)
            ids = self.getWidget2Id(totalWidgets)
            
            newObs = self.matcher.getObsforIds(ids)
            #[i.summary() for i in newObs]
            commandKey = self.modButton+self.interactionModeString
            originCommand = ORIGINCOMMANDS[commandKey]
            if newObs:
                self.dispatch(originCommand, newObs)
                self.publish(originCommand, newObs)
            self.cursorReset()

    def selectObservations(self,observations):
        """Override View Method"""
        ids = self.matcher.matchObservations(observations)
        wids = self.getId2Widget(ids) 
        bins = self.getUniqueBin(wids)
        totalWidgets = self.getBins2Widgets(bins)
        self.selected = self.selected + totalWidgets
        self.highlightMultiple(totalWidgets)

    def newSelectObservations(self,observations):
        """Override View Method"""
        ids = self.matcher.matchObservations(observations)
        self.unhighlightMultiple(self.selected)
        wids = self.getId2Widget(ids) 
        bins = self.getUniqueBin(wids)
        totalWidgets = self.getBins2Widgets(bins)
        self.selected = totalWidgets
        self.highlightMultiple(totalWidgets)

    def brushObservations(self,observations):
        """Override View Method"""
        ids = self.matcher.matchObservations(observations)
        wids = self.getId2Widget(ids) 
        bins = self.getUniqueBin(wids)
        totalWidgets = self.getBins2Widgets(bins)
        self.selected = self.selected + totalWidgets
        self.brushMultiple(totalWidgets)
        
    def newBrushObservations(self,observations):
        """Override View Method"""
        ids = self.matcher.matchObservations(observations)
        self.unhighlightMultiple(self.selected)
        wids = self.getId2Widget(ids) 
        bins = self.getUniqueBin(wids)
        totalWidgets = self.getBins2Widgets(bins)
        self.selected = totalWidgets
        self.brushMultiple(totalWidgets)

    def linkSliceCounter(self,widgetList):
        """Get list of slices to highlight to represent widgets in widgetList
        XXX is this correct?

        widgetlist (list): list of ids for widgets

        Returns:
        widgets2highlight (list): of widget ids
        """
        widgets2highlight = []
        bins = {}
        for widget in widgetList:
            bin = self.widget2Bin[widget]
            if bins.has_key(bin):
                bins[bin] = bins[bin] + 1
            else:
                bins[bin] = 1
        for bin in bins.keys():
            widgetList = self.bin2Widget[bin]
            newWidgets = widgetList[0:bins[bin]]
            widgets2highlight = widgets2highlight + newWidgets
        return widgets2highlight

    def brushSliceCounter(self,widgetList):
        """Get list of slices to highlight to represent widgets in widgetList
        XXX is this correct?

        widgetlist (list): list of ids for widgets

        Returns:
        widgets2highlight (list): of widget ids
        """
        widgets2highlight = []
        bins = {}
        for widget in widgetList:
            bin = self.widget2Bin[widget]
            if bins.has_key(bin):
                bins[bin] = bins[bin] + 1
            else:
                bins[bin] = 1
        for bin in bins.keys():
            widgetList = self.bin2Widget[bin]
            newWidgets = widgetList[- bins[bin] :]
            widgets2highlight = widgets2highlight + newWidgets
        return widgets2highlight
    
    def newSlice2Highlight(self,observations):
        """Highlight slices associated with observations

        observations (list): of Observations
        """
        self.unhighlightMultiple(self.selected)
        ids = self.matcher.matchObservations(observations)
        wids = self.getId2Widget(ids)
        slices = self.linkSliceCounter(wids)
        self.highlightMultiple(slices)
        self.selected = slices

    def slice2Highlight(self,observations):
        """Extended-highlight slices associated with observations

        observations (list): of Observations
        """
        ids = self.matcher.matchObservations(observations)
        wids = self.getId2Widget(ids)
        wids = wids + self.selected
        slices = self.linkSliceCounter(wids)
        self.highlightMultiple(slices)
        self.selected = slices

    def newSlice2Brush(self,observations):
        """Brush slices associated with observations

        observations (list): of Observations
        """
        self.unhighlightMultiple(self.selected)
        self.unhighlightMultiple(self.selected)
        ids = self.matcher.matchObservations(observations)
        wids = self.getId2Widget(ids)
        slices = self.brushSliceCounter(wids)
        self.brushMultiple(slices)
        self.selected = slices
    
    def slice2Brush(self,observations):
        """Extended-Brush slices associated with observations

        observations (list): of Observations
        """
        self.unhighlightMultiple(self.selected)
        ids = self.matcher.matchObservations(observations)
        wids = self.getId2Widget(ids)
        wids = wids + self.selected
        slices = self.brushSliceCounter(wids)
        self.brushMultiple(slices)
        self.selected = slices            

    def changeInteractionMode(self,mode):
        """XXX move up?"""
        self.interactionVar.set(mode)
        self.interactionMode = mode
        self.interactionModeString = INTERACTIONMODES[mode]
        self.unhighlightMultiple(self.selected)
        self.selected = []

    def mouseMiddleButton(self,event):
        """Override View method"""
        stat='coords:'+str(event.x)+','+str(event.y)
        self.lastx  = self.canvas.canvasx(event.x)
        self.lasty  = self.canvas.canvasy(event.y)
        oid = self.canvas.find_overlapping(self.lastx,self.lasty,self.lastx,self.lasty)
        self.selectedIds = self.cleanWidgetIds(oid)
        if len(self.selectedIds) != 0:
            Bin = self.widget2Bin[self.selectedIds[0]]
            wids = self.bin2Widget[Bin]
            ids = self.getWidget2Id(wids)
            topBound = self.matcher.bounds[Bin]
            if Bin == 0:
                lowerBound = self.MinX
            else:
                lowerBound = self.matcher.bounds[Bin - 1]

            try:
                observations = [self.matcher.observations[i] for i in ids]
                ts = str(observations[0].ts)
                varName = observations[0].variable
                csString = 'Number of Cross-Section: ' + str(len(ids)) + '\n'
                tsString = 'Time-Series Id: ' + ts + '\n'
                vString = 'Variable Name: ' + self.xLabel + '\n'
                bString = 'Bin Bounds: ' + str(lowerBound) + ' -- ' + str(topBound) 
                label = csString+tsString+vString+bString
                self.highlightMultiple(wids)
                self.tLabel = Label(self.canvas,text=label,bg='Yellow',font=('Times', options.AXISFONTSIZE))
                if self.lastx < self.xMidPoint:
                    self.identLabel = self.canvas.create_window(self.lastx+3, self.lasty, anchor=W, window=self.tLabel)
                else:
                    self.identLabel = self.canvas.create_window(self.lastx-3, self.lasty, anchor=E, window=self.tLabel)            
                self.tempWID = wids

            except KeyError:
                pass
            
    def mouseMiddleRelease(self,event):
        """Override View method"""
        try:
            self.unhighlightMultiple(self.tempWID)
            self.canvas.delete(self.tLabel)
            self.canvas.delete(self.identLabel)
        except:
            pass
            
    def buildMethods(self):
        """Override View method"""
        # only methods that are to be accessed by observer go in here.
        m={"selectedObservations":self.selectedObservations,
           "selectObservations":self.selectObservations,
           "newSelectedObservations":self.newSelectedObservations,
           "newSelectObservations":self.newSelectObservations, 
           "brushedObservations":self.brushedObservations,
           "brushObservations":self.brushObservations,
           "newBrushedObservations":self.newBrushedObservations,
           "newBrushObservations":self.newBrushObservations,
           "travel":self.travel,
           "newSlice2Highlight":self.newSlice2Highlight,
           "slice2Highlight":self.slice2Highlight,
           "newSlice2Brush":self.newSlice2Brush,
           "slice2Brush":self.slice2Brush,
           "updateTime":self.updateTime
           }
        self.methods=m
        
    def unhighlightMultiple(self,widgets):
        """Unhighlight several widgets

        widgets (list) of widget ids
        """
        for i in widgets:
            self.unhighlightSlice(i)

class TimeSeries(Plot,Subscriber):
    nmtime = 0
    def __init__(self,name,master,x,y,xDelimiter=None,yDelimiter=None,title=None,
        xLabel='t', yLabel='Y', xDecimal=None, yDecimal=None,
        ovalFill=None, ovalBorder=None,csIds=[],tsLabels=[],xPop='t',yPop='Y'):
        self.name = name
        self.master = master
        self.title=title
        self.x = x
        lx = len(self.x)
        #print lx
        self.t = range(lx)
        self.y = y
        self.type="timeSeries"
        self.xDecimal = xDecimal
        self.yDecimal = yDecimal
        self.yLabel = yLabel
        self.xLabel = xLabel
        self.tsLabels = tsLabels
        self.labelDict = {}
        self.titleOnCanvas = 0
        self.ovalFill = ovalFill
        self.ovalBorder = ovalBorder
        self.timeString = 'Time Series Plot'
        self.setTitle(self.timeString)
        Plot.__init__(self,name,master,x,y,xDelimiter=None,yDelimiter=None,title=self.title,
                      xLabel=xLabel, yLabel=yLabel, xDecimal=None, yDecimal=None,
                      ovalFill=None, ovalBorder=None,xPop=xPop,yPop=yPop)
        self.canvas.pack(side=LEFT,anchor=W)
        self.matcher = ITimeSeries(self.yLabel,self.y,self.t,csIds)

        TimeSeries.nmtime +=1
        self.name = "time_%d"%TimeSeries.nmtime
        self.top.title(self.title)
        Subscriber.__init__(self,self.observer)
        self.selected = []    

    def draw(self):
        self.genericTimeSign()
        self.setOvalColors()
        self.scaleBox()
        self.getMinMax()
        self.getRanges()
        self.getRatios()
        self.makeXTicks()
        self.makeYTicks()
        self.makeTickLabels()
        self.scaleTicks()
        self.scalePoints()
        self.drawOuterBox()
        self.drawAxis()
        self.drawTicks()
        self.drawTimeLinks()
        self.drawPoints()  
        self.drawXLabel()
        self.drawYLabel()

    def genericTimeSign(self):
        if len(self.tsLabels) == 0:
            self.intervalList = ["T("+str(i)+")" for i in self.t]
        else:
            self.intervalList = self.tsLabels    
    
    def makeXTicks(self):
        self.xTickInterval = self.xIntegerRange[-1] - self.xIntegerRange[0]

        if self.xDelimiter == None:
            ints = 4
            xBreaker = self.xTickInterval / ints
            numberXBreaks = range(ints + 1)
            xBreak2 = [i*xBreaker for i in numberXBreaks]
            try:
                self.xTicks = [self.x[i] for i in xBreak2]
            except:
                s = self.x
                s.sort()
                width=s[1]-s[0]
                nBreaks = 5
                xTicks = [s[0] + i * width for i in range(nBreaks)]
                self.xTicks = xTicks
            if sum(self.xTicks) == ints+1: #Kludge for small integer range
                self.xTicks = range(1,ints+1)
        elif len(self.xDelimiter) == 1:
            ints = self.xDelimiter[0]
            numberXBreaks = range(1, ints+1)
            for i in numberXBreaks:
                t = float(i) / numberXBreaks[-1]
                xBreaks.append(t)
            for i in xBreaks:
                self.xTicks.append(self.MinX + (self.xTickInterval * i))
            self.xTicks.append(self.MinX)
            if sum(self.xTicks) == ints+1:
                self.xTicks = range(1,ints+1) #Kludge for small integer range
        else:
            self.xTicks = self.xDelimiter

           
    def makeTickLabels(self):
        """Format x and y labels create decimal places by default or for
        argument passed in."""
        if self.xDecimal:
            pass
        else:
            self.xDecimal = 0
        if self.yDecimal:
            pass
        else:
            if self.MaxY < 10.0:
                self.yDecimal = 3
            else:
                self.yDecimal = 0
        xTickLeft = [int(i) for i in self.xTicks]
        xTickLeft = [len(str(i)) for i in xTickLeft]
        self.xTickLeftMax = max(xTickLeft)
        tmpX = "%"+str(self.xTickLeftMax)+"."+str(self.xDecimal)+"f"
        self.xTicksLabs = [tmpX %(i) for i in self.xTicks]
        yTickLeft = [int(i) for i in self.yTicks]
        yTickLeft = [len(str(i)) for i in yTickLeft]
        self.yTickLeftMax = max(yTickLeft)
        tmpY = "%"+str(self.yTickLeftMax)+"."+str(self.yDecimal)+"f"
        self.yTicksLabs = [tmpY %(i) for i in self.yTicks]

    def drawTimeLinks(self):
        c = 0
        for i in self.scaledXCords[0:-1]:
            xOrigin = i
            xDest = self.scaledXCords[c+1]
            yOrigin = self.scaledYCords[c]
            yDest = self.scaledYCords[c+1]
            g = self.drawLine(xOrigin, yOrigin, xDest, yDest, 1)
            c = c+1
            
    def drawPoints(self):
        self.id2Widget = {}
        self.widget2Id = {}
        self.idInfo = {}
        self.origColors = {}
        self.pointXY = {}
        c = 0
        for i in self.scaledXCords:
            x1 = i
            y1 = self.scaledYCords[c]
            x1 = x1-options.NEGATIVEOVAL
            y1 = y1-options.NEGATIVEOVAL
            x2=x1+options.POSITIVEOVAL
            y2=y1+options.POSITIVEOVAL
            g = self.canvas.create_oval(x1,y1,x2,y2,outline=self.ovalBorder, fill=self.ovalFill)
            self.origColors[g] = self.ovalFill
            self.id2Widget[c] = g
            self.widget2Id[g] = c
            self.idInfo[c] = [self.x[c], self.y[c], self.intervalList[c]] #actual x,y vals for tags
            self.pointXY[g] = (i,self.scaledYCords[c])
            c = c+1
        self.widgetKeys = self.widget2Id.keys()        
        
    def mouseLeftButtonRelease(self,event):
        stat='coords:'+str(event.x)+','+str(event.y)
        if self.interactionMode:
            self.lastx  = self.canvas.canvasx(event.x)
            self.lasty  = self.canvas.canvasy(event.y)
            x1 = self.startx
            x2 = self.lastx
            y1 = self.starty
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()
            oid = self.canvas.find_overlapping(x1,y1,x2,y2)
            self.selectedIds = self.cleanWidgetIds(oid)
            if len(self.selected) > 0:
                wid2Delete = self.id2Widget[self.selected[0]]
                self.unhighlightTime(wid2Delete)
                self.selected = []
            ids = self.getIdsForWidgets(self.selectedIds)
            ids = sort(ids)
            newObs = self.matcher.getObsforIds(ids)
            try:
                newObs = newObs[0]
                commandKey = self.modButton+self.interactionModeString
                originCommand = ORIGINCOMMANDS[commandKey]
                if newObs:
                    self.dispatch(originCommand,[ids[0]])
                    self.publish(originCommand,[ids[0]])
                self.cursorReset()
            except:
                pass
        
    def updateTime(self, timeId):
        if hasattr(timeId,'ts'):
            timeId = timeId.ts
        self.selected = [timeId]
        wid = self.id2Widget[timeId]
        self.highlightTime(wid)
        xy = self.pointXY[wid]
        self.canvas.delete("tsline")
        self.canvas.create_oval(xy[0]-4,xy[1]-4,xy[0]+4,xy[1]+4,outline='red',tag=("tsline"))

    def updateTime2Time(self, timeId):
        if len(self.selected) > 0:
            self.unhighlightTime(self.id2Widget[self.selected[0]])
        self.selected = [timeId[0]]
        wid = self.id2Widget[timeId[0]]
        self.highlightTime(wid)
        xy = self.pointXY[wid]
        self.canvas.delete("tsline")
        self.canvas.create_oval(xy[0]-4,xy[1]-4,xy[0]+4,xy[1]+4,outline='red',tag=("tsline"))

    def newSelectedObservations(self,ids):
        ids = ids[0]
        self.updateTime(ids)
        
    def newSelectObservations(self,observations):
        if len(self.selected) > 0:
            wid2Delete = self.id2Widget[self.selected[0]]
            self.unhighlightTime(wid2Delete)
            self.selected = []
        ids = [i.ts for i in observations]
        newTime = sort(ids)[0][0]
        self.updateTime(newTime)

    def highlightTime(self, widget):
        self.canvas.itemconfigure(widget,fill=options.HIGHLIGHTCOLOR)

    def unhighlightTime(self, widget):
        self.canvas.itemconfigure(widget,fill=options.DEFAULTOVALFILL)

    def travel(self):
        sortedKeys = self.matcher.observationKeys
        sortedKeys.sort()
        for key in sortedKeys:
            obs = self.matcher.observations[key]
            if len(self.selected) > 0:
                wid2Delete = self.id2Widget[self.selected[0]]
                self.unhighlightTime(wid2Delete)
                self.selected = []
            self.canvas.update()
            self.updateTime(obs.ts)
            self.publish("travel",[obs.ts])
            for it in range(50):
                self.canvas.update()
        self.linkingMode()

    def mouseMiddleButton(self,event):
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
            csString = 'cross-section id: ' + str(cid) + '\n'
            tsString = self.xPop +" = " + ts + '\n'
            c = 0
            yString = self.yPop + " = " + str(values) 
            label = csString+tsString+yString
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
     
    def roamWindowStart(self,event):
        #print 'start roamWindow'
        if self.interactionMode:
            self.startRWX = self.canvas.canvasx(event.x)
            self.startRWY = self.canvas.canvasy(event.y)

    def roamWindowStop(self,event):
        if self.interactionMode:
            self.roamWindowOn = 1
            self.startRWX = self.canvas.canvasx(event.x)
            x2 = self.startRWX + 2 
            self.lastRWX = x2
            self.roamWindowCreate([self.startRWX,self.y0Inner,x2,self.y1Inner])

    def roamWindowStretch(self,event):
        pass
        #if self.interactionMode:
        #    #print 'roamWindowStretch'
        #    cx = self.canvas.canvasx(event.x)
        #    cy = self.canvas.canvasy(event.y)
        #    self.lastRWX = cx
        #    self.lastRWY = cy
        #    self.roamWindowDelete()
        #    self.roamWindowCreate([self.startRWX,self.y0Inner,cx,self.y1Inner])


    def mouseMotion(self,event):
        """overridden for TimeSeries"""
        if self.roamWindowOn and self.interactionMode:
            #print 'mouse motion'
            cx = self.canvas.canvasx(event.x)
            cy = self.canvas.canvasy(event.y)
            dx = cx - self.lastRWX
            self.lastRWX = cx
            dy = 0
            self.canvas.move('roamWindow',dx,dy)
            self.startRWX = cx
            self.startRWY = cy
            x1,y1,x2,y2 = self.canvas.bbox('roamWindow')
            oid = self.canvas.find_overlapping(x1,y1,x2,y2)
            self.selectedIds = self.cleanWidgetIds(oid)
            ids = self.getIdsForWidgets(self.selectedIds)
            ids = sort(ids)
            if len(ids > 0) and (ids[0] not in self.selected):
                try:
                    wid2Delete = self.id2Widget[self.selected[0]]
                    self.unhighlightTime(wid2Delete)
                except:
                    pass
                newObs = self.matcher.getObsforIds(ids)
                try:
                    newObs = newObs[0]
                    commandKey = self.modButton+self.interactionModeString
                    originCommand = ORIGINCOMMANDS[commandKey]
                    if newObs:
                        #self.dispatch(originCommand,[ids[0]])
                        self.updateTime(ids[0])
                        self.publish(originCommand,[ids[0]])
                        for it in range(50):
                            self.canvas.update()
                    self.cursorReset()
                except:
                    pass
            self.canvas.tkraise('roamWindow')
   
    def buildMethods(self):
        # only methods that are to be accessed by observer go in here.
        m={"selectedObservations":self.selectedObservations,
           "selectObservations":self.selectObservations,
           "newSelectedObservations":self.newSelectedObservations,
           "newSelectObservations":self.newSelectObservations, 
           "brushedObservations":self.brushedObservations,
           "brushObservations":self.brushObservations,
           "newBrushedObservations":self.newBrushedObservations,
           "newBrushObservations":self.newBrushObservations,
           "updateTime":self.updateTime,
           "updateTime2Time":self.updateTime2Time,
           "travel":self.travel
           }
        self.methods=m
        
class BoxPlot(View,Subscriber):
    """ """
    nbox = 0
    def __init__(self,name,master,varName,x,tsids,csids,fence=1.5,stemPoints=1):
        self.x = x
        self.stemPoints = stemPoints
        self.fence = fence
        self.name = name
        self.varName = varName
        self.matcher = IBox(varName,array(x),tsids=tsids,
                      csids=csids,fence=fence)
        View.__init__(self,name,master,title="Box Plot")
        self.canvas.pack(side=LEFT,anchor=W)
        self.type="boxplot"
        BoxPlot.nbox +=1
        self.name = "boxplot_%d"%BoxPlot.nbox

        Subscriber.__init__(self,self.observer)
        self.top.title(self.name)
    
    def draw(self):
        info = self.matcher
        self.origColors = {}
        if info.highOutliers:
            top = info.maxX
        else:
            top = info.bins[-1]
        if info.lowOutliers:
            bottom = info.minX
        else:
            bottom = info.bins[0]
        
        top2Bottom = top - bottom

        screenTop = self.height * 0.10
        screenBottom = self.height * 0.90
        screenTop2Bottom = screenBottom - screenTop

        vscale = screenTop2Bottom / top2Bottom
        leftBound = self.width * .35
        rightBound = self.width * .65
        self.xMidPoint = (leftBound + rightBound) / 2.0
        self.y1 = self.height * options.OUTERBOXPLOTS[1]
        
        self.widgets2items={}
        self.items2widgets={}
        self.widgets2Ids = {}
        self.ids2Widgets = {}
        self.widget2Cords = {}

        # container box
        bins = info.bins
        sbins = [ screenBottom - (x - bottom) * vscale for x in bins]

        self.selectableWidgets = []
        #iq box
        b1=self.canvas.create_rectangle(leftBound,sbins[1],rightBound,sbins[2],fill="purple")
        self.origColors[b1] = "purple"
        self.widgets2items[b1]="box1"
        self.items2widgets["box1"] = b1
        self.widgets2Ids[b1] = []
        b2=self.canvas.create_rectangle(leftBound,sbins[3],rightBound,sbins[2],fill="purple")
        self.origColors[b2] = "purple"
        self.widgets2items[b2]="box2"
        self.items2widgets["box2"] = b2
        self.widgets2Ids[b2] = []

        ml=self.canvas.create_line(leftBound,sbins[2],rightBound,sbins[2])
        self.widgets2items[ml]="medianLine"
        self.items2widgets["medianLine"]=ml

        midx = self.width * .50

        #fences
        ends = screenTop2Bottom * 0.025
        f1=self.canvas.create_line(leftBound,sbins[0],rightBound,sbins[0],width=1)
        self.canvas.create_line(leftBound,sbins[0],leftBound,sbins[0]-ends,width=1)
        self.canvas.create_line(rightBound,sbins[0],rightBound,sbins[0]-ends,width=1)
         
        self.widgets2items[f1]="fence1"
        self.items2widgets["fence1"]=f1
        f2=self.canvas.create_line(leftBound,sbins[4],rightBound,sbins[4],width=1)
        self.canvas.create_line(leftBound,sbins[4],leftBound,sbins[4]+ends,width=1)
        self.canvas.create_line(rightBound,sbins[4],rightBound,sbins[4]+ends,width=1)
        self.widgets2items[f2]="fence2"
        self.items2widgets["fence2"]=f2

        # stems from box to fences
        s1=self.canvas.create_line(midx,sbins[1],midx,sbins[0])
        self.widgets2items[s1]="stem1"
        self.items2widgets["stem1"]=s1
        self.widgets2Ids[s1] = []
        s2=self.canvas.create_line(midx,sbins[3],midx,sbins[4])
        self.widgets2items[s2]="stem2"
        self.items2widgets["stem2"]=s2
        self.origColors[s1] = "black"
        self.origColors[s2] = "black"
        self.widgets2Ids[s2] = []
        meanY = screenBottom - (mean(self.x) - bottom) * vscale
        self.canvas.create_oval(midx-2,meanY+2,midx+2,meanY-2,fill="pink")
        if self.stemPoints:
            self.selectableWidgets = [b1,b2] 
        else:
            self.selectableWidgets = [b1,b2,s1,s2]

        rangen = range(len(self.x))
        scaledX = [ screenBottom - (x - bottom) * vscale for x in self.x ]
        idsInB1 = []
        idsInB2 = []
        idsOnW1 = []
        idsOnW2 = []
        ids2items = {} 
        for value,i in zip(scaledX,rangen):
            binId = info.binIds[i]
            if binId==1 or binId==4:
                #between the fences and box
                if self.stemPoints:
                    widgetid=self.canvas.create_oval(midx-2,value+2,midx+2,value-2,
                    fill=options.DEFAULTOVALFILL)
                    self.widget2Cords[widgetid] = [midx-2,value+2,midx+2,value-2]
                    self.origColors[widgetid]=options.DEFAULTOVALFILL 
                    self.selectableWidgets.append(widgetid)
                    self.widgets2items[widgetid] = i
                    ids2items[i] = widgetid
                    self.widgets2Ids[widgetid] = i
                    self.ids2Widgets[i] = widgetid
                elif binId==1:
                    ids2items[i] = s1
                    self.widgets2Ids[s1].append(i)
                    self.ids2Widgets[i] = s1
                else:
                    ids2items[i] = s2
                    self.widgets2Ids[s2].append(i)
                    self.ids2Widgets[i] = s2
            elif binId==0 or binId==5:
                #outlier
                o=self.canvas.create_oval(midx-3,value+3,midx+3,value-3,fill=options.DEFAULTOVALFILL)
                self.widget2Cords[o] = [midx-3,value+3,midx+3,value-3]
                self.origColors[o]=options.DEFAULTOVALFILL 
                ids2items[i] = o
                self.widgets2items[o] = i
                self.selectableWidgets.append(o)
                self.widgets2Ids[o] = i
                self.ids2Widgets[i] = o

            elif binId==2:
                idsInB1.append(i)
                ids2items[i] = b1
                self.widgets2Ids[b1].append(i)
                self.ids2Widgets[i] = b1
            else:
                idsInB2.append(i)
                ids2items[i] = b2
                self.widgets2Ids[b2].append(i)
                self.ids2Widgets[i] = b2
        items2ids={}
        items2ids["box1"] = idsInB1
        items2ids["box2"] = idsInB2
        items2ids["stem1"] = idsOnW1
        items2ids["stem2"] = idsOnW2

        self.items2ids = items2ids
        self.ids2items = ids2items
        self.widget2Id = self.widgets2Ids
        self.widgetKeys = self.widget2Id.keys()

    def cleanWidgets(self,oid):
        if len(oid) == 1:
            oid = [oid[0]]
        return oid
 
    def mouseLeftButtonRelease(self,event):
        stat='coords:'+str(event.x)+','+str(event.y)
        if self.interactionMode:
            self.lastx  = self.canvas.canvasx(event.x)
            self.lasty  = self.canvas.canvasy(event.y)
            x1 = self.startx
            x2 = self.lastx
            y1 = self.starty
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()
            oid = self.canvas.find_overlapping(x1,y1,x2,y2)
            oid = self.cleanWidgets(oid)
            ids = self.getIdsForWidgets(oid)
            newObs = self.matcher.getObsforIds(ids)
            commandKey = self.modButton+self.interactionModeString
            originCommand = ORIGINCOMMANDS[commandKey]
            if newObs:
                self.dispatch(originCommand,newObs)
                self.publish(originCommand,newObs)
            else:
                # debug
                print 'no new obs'

            self.cursorReset()

    def getIdsForWidgets(self,wids):
        match = []
        for wid in wids:
            if self.selectableWidgets.count(wid):
                ids = self.widget2Id[wid]
                try:
                    match.extend(ids)
                except:
                    match.append(ids)
        return match

    def getWidgetsForIds(self,ids):
        matched = []
        for id in ids:
                tmp = self.ids2Widgets[id]
                if matched.count(matched) == 0:
                    matched.append(tmp)
        return matched
            
    def selectObservations(self,observations):
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        cordIds = self.widget2Cords.keys()
        for id in wids:
            if id in cordIds:
                cords = self.widget2Cords[id]
                self.canvas.create_oval(cords[0],cords[1],cords[2],cords[3],
                fill=options.HIGHLIGHTCOLOR,tag=('temp'))
            else:
                self.canvas.itemconfig(id,fill=options.HIGHLIGHTCOLOR)

    def clearAll(self):
        View.clearAll(self)
        self.canvas.delete('temp')

    def newSelectObservations(self,observations):
        self.canvas.delete('temp')
        self.unHighlightWidget()
        self.matcher.deselect()
        self.selectObservations(observations)
        ids = self.matcher.selected
        
    def brushObservations(self,observations):
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        cordIds = self.widget2Cords.keys()
        for id in wids:
            if id in cordIds:
                cords = self.widget2Cords[id]
                self.canvas.create_oval(cords[0],cords[1],cords[2],cords[3],
                fill=options.BRUSHCOLOR,tag=('temp'))
            else:
                self.canvas.itemconfig(id,fill=options.BRUSHCOLOR)


    def newBrushObservations(self,observations):
        self.canvas.delete('temp')
        self.unHighlightWidget()
        self.matcher.deselect()
        self.brushObservations(observations)
        ids = self.matcher.selected

    def unHighlightWidget(self,widgetIds=[]):
        t1=time.time()
        if widgetIds == []:
            ids = self.matcher.selected
            wids = self.getWidgetsForIds(ids)
            widgetIds = wids
        for widget in widgetIds:
            if self.origColors.has_key(widget):
                color = self.origColors[widget]    
                self.canvas.itemconfigure(widget,fill=color)
        t2=time.time()
        
    def changeInteractionMode(self,mode):
        self.interactionVar.set(mode)
        self.interactionMode = mode
        self.interactionModeString = INTERACTIONMODES[mode]
        self.canvas.delete('temp')
        self.clearAll()
        
class CScatterPlot(Plot,Subscriber):
    """Conditional Scatter Plot """
    ncscatter=0
    def __init__(self,name,master,x,y,z,nColors=6,xLabel="X",yLabel="Y",
        zLabel="Z"):
        self.master = master
        self.x = x
        self.y = y
        self.z = z
        self.xLabel = xLabel
        self.yLabel = yLabel
        self.zLabel = zLabel
        self.nColors = nColors
        self.matcher = ICScatterPlot(x,y,z)
        Plot.__init__(self,name,master,x,y,title="CScatter Plot")
        self.canvas.pack(side=LEFT,anchor=W)
        self.type="cscatter"
        CScatterPlot.ncscatter +=1
        self.name = "cs %d"%CScatterPlot.ncscatter
        lname = ["Conditional Scatter",xLabel,yLabel,zLabel]
        self.listName = (" ").join(lname)

        Subscriber.__init__(self,self.observer)
        self.top.title(self.type)

    def draw(self): 
        self.scaleBox()
        self.getMinMax()
        self.getRanges()
        self.getRatios()
        self.makeXTicks()
        self.makeYTicks()
        self.makeTickLabels()
        self.scaleTicks()
        self.scalePoints()
        self.drawOuterBox()
        self.drawAxis()
        self.drawTicks()
        self.drawPoints()  
        self.drawXLabel()
        self.drawYLabel()
        self.drawZLabel()

    def drawZLabel(self):
        zString = '* Conditioned on ' + self.zLabel
        self.canvas.create_text(self.x0 + 5, self.y0 - 10,
        text=zString,font=('Times', 8), anchor=W)
        
    def getMinMax(self):
        self.MaxX = max(self.x) 
        self.MinX = min(self.x) 
        self.MaxX = max(self.MaxX)
        self.MinX = min(self.MinX)
        self.MaxY = max(self.y) 
        self.MinY = min(self.y)   
        self.MaxY = max(self.MaxY)
        self.MinY = min(self.MinY)

    def drawPoints(self):
        info = self.matcher
        info.colorMap(self.nColors)
        obskeys = self.matcher.observationKeys
        allx= []
        ally= []

        scaledXcords = []
        scaledYcords = []
        widget2Obs = {}
        obs2Widget = {}
        origColors = {}
        widgetTemp = {}
        for obkey in obskeys:
            observation = self.matcher.observations[obkey]
            x,y,z = observation.value
            xs = self.x0Buffer + (x - self.MinX) * self.xratio
            ys = self.y0Buffer + (y - self.MinY) * self.yratio
            allx.append(xs)
            ally.append(ys)
            colorId = info.colorId[obkey]
            color=SEQCOLORS[colorId]
            id = self.canvas.create_oval(xs-2,ys-2,xs+2,ys+2,
                    outline=color,fill=color)
            widgetTemp[id] = (xs-2,ys-2,xs+2,ys+2)
            widget2Obs[id] = obkey
            obs2Widget[obkey] = id
            origColors[id] = color
            scaledXcords.append(xs)
            scaledYcords.append(ys)

        self.scaledXCords = scaledXcords
        self.scaledYCords = scaledYcords
        self.widget2Obs = widget2Obs
        self.obs2Widget = obs2Widget
        self.widgetKeys = widget2Obs.keys()
        self.id2Widget = obs2Widget
        self.origColors = origColors
        self.widgetTemp = widgetTemp
        self.fitLine()
        
    def getIdsForWidgets(self,wids):
        matchedIds = []
        for id in wids:
            if self.widgetKeys.count(id) > 0:
                obsKey = self.widget2Obs[id]
                if matchedIds.count(obsKey) == 0:
                    matchedIds.append(obsKey)
        k = self.widgetKeys
        k.sort()
        return matchedIds 

    def newSelectedObservations(self,observations):
        self.newSelectObservations(observations)

    def newSelectObservations(self,observations):
        self.unHighlightWidget()
        self.matcher.deselect()
        self.selectObservations(observations)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)

    def selectObservations(self,observations):
        ids = self.matcher.matchObservations(observations)
        # need to remove dups otherwise matcher deselects everything in next
        # call
        ids = dict.fromkeys(ids).keys()
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.highlightWidget(wids)

    def getWidgetsForIds(self,ids):
        matchedIds = []
        for id in ids:
            if self.id2Widget.has_key(id):
                wid = self.id2Widget[id]
                matchedIds.append(wid)
        return matchedIds

    def selectTsObservations(self,tsid):
        obsKeys = self.matcher.ts2key[tsid[0]]
        wids = self.getWidgetsForIds(obsKeys)
        self.unHighlightWidget()
        self.highlightWidget(wids)

    def highlightWidget(self,widgetIds):
        xc = []
        yc = []
        for widget in widgetIds:
             coords = self.widgetTemp[widget]
             self.canvas.create_oval(coords,fill="Yellow",outline='Red',tag=("temp"))
             #self.canvas.addtag_above('above',widget)
             #self.canvas.tkraise(widget,'above')
             #self.canvas.tkraise(widget)
             #self.canvas.itemconfigure(widget, fill="Yellow", outline='Red')
            
             xc.append(coords[0]+2)
             yc.append(coords[1]+2)
        xc = array(xc)
        yc = array(yc)
        self.fitLine(xc,yc,tagString="temp",fill="yellow")

    def unHighlightWidget(self,widgetIds=[]):
        self.canvas.delete("temp")
        self.removeBrushLine()
        if widgetIds == []:
            ids = self.matcher.selected
            wids = self.getWidgetsForIds(ids)
            widgetIds = wids
        for widget in widgetIds:
            print widget
            if self.origColors.has_key(widget):
                color = self.origColors[widget]    
                self.canvas.itemconfigure(widget,fill=color,outline=color)

    def newBrushedObservations(self,observations):
        self.removeBrushLine()
        self.unHighlightWidget()
        self.matcher.deselect()
        
        self.selectObservations(observations)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.brushWidget(wids)


    def buildMethods(self):
        m={"selectedObservations":self.selectedObservations,
           "selectObservations":self.selectObservations,
           "newSelectedObservations":self.newSelectedObservations,
           "newSelectObservations":self.newSelectObservations, 
           "selectTsObservations":self.selectTsObservations,
           "newBrushedObservations":self.newBrushedObservations,
           "travel":self.travel
           }
        self.methods=m

    def fitLine(self,x=[],y=[],tagString = "fitLine",fill="black"):
        if not x:
            x = array(self.scaledXCords)
        if not y:
            y = array(self.scaledYCords)

        mx = mean(x)
        my = mean(y)
        xd = x - mx
        yd = y - my
        x2 = sum(xd*xd)
        xy = sum(xd*yd)
        b = xy/x2
        a = my - b * mx
        x0 = min(self.scaledXCords)
        x1 = max(self.scaledXCords)
        y0 = a + b * x0
        y1 = a + b * x1

        # constrain line endpoints to stay within range of Y
        yScreenMin = min(self.scaledYCords)
        yScreenMax = max(self.scaledYCords)

        if y0 < yScreenMin:
            x0 = (yScreenMin - a)/b
            y0 = yScreenMin
        elif y0 > yScreenMax:
            x0 = (yScreenMax - a)/b
            y0 = yScreenMax

        if y1 < yScreenMin:
            x1 = (yScreenMin - a)/b
            y1 = yScreenMin
        elif y1 > yScreenMax:
            x1 = (yScreenMax - a)/b
            y1 = yScreenMax

        self.canvas.create_line(x0,y0,x1,y1, width = 1,tags=(tagString),fill=fill )

    def removeFitLine(self):
        self.canvas.delete("fitLine")
        
class Density(Plot,Subscriber):
    nden = 0
    def __init__(self,name,master,varName,y,csid=[],tsid=[],
        title="Kernel Density",xLabel='X',yLabel='f(x)',xmin=None,
        xmax=None):
        self.master = master
        self.title = title
        self.varName = varName
        self.matcher = IDensity(varName,y,tsid,csid,xmin=xmin,xmax=xmax)
        self.fixedXmin = xmin
        self.fixedXmax = xmax
        self.tsid = tsid
        self.csid = csid
        self.x = self.matcher.xgrid
        self.y = self.matcher.fx
        self.xLabel = xLabel
        self.yLabel = yLabel
        Density.nden += 1
        name = "density_%d"%Density.nden
        Plot.__init__(self,name,master,self.x,self.y,title=title)
        self.canvas.pack(side=LEFT,anchor=W)
        self.type = "density"
        self.top.title(title)
        self.name =  name
        Subscriber.__init__(self,self.observer)

    def updateTime(self,tsId):
        tsId = tsId[0]
        title = "Density %s %s"%(self.varName,self.variable.timeString[tsId])
        self.top.title(title)
        y = self.variable[:,tsId]
        self.canvas.delete('all')
        self.matcher = IDensity(self.varName,y,self.tsid,self.csid,xmin=self.fixedXmin,
            xmax=self.fixedXmax)
        self.x = self.matcher.xgrid
        self.y = self.matcher.fx
        self.draw()
        
    def draw(self):
        self.setOvalColors()
        self.scaleBox()
        self.getMinMax()
        self.getRanges()
        self.getRatios()
        self.makeXTicks()
        self.makeYTicks()
        self.makeTickLabels()
        self.scaleTicks()
        self.scalePoints()
        self.drawOuterBox()
        self.drawAxis()
        self.drawTicks()
        self.drawIntegral()
        self.drawXLabel()
        self.drawYLabel()
        
    def drawIntegral(self):
        widget2Bin = {}
        bin2Widget = {}
        seg2bin = {}
        origColors = {}
        self.coords = {}

        for i in range(len(self.scaledXCords)-1):
            xc = self.scaledXCords[i]
            yc = self.scaledYCords[i]

            i1=i+1
            x0 = self.scaledXCords[i]
            x1 = self.scaledXCords[i1]
            y0 = self.scaledYCords[i]
            y1 = self.scaledYCords[i1]
            tag = "segment_%d"%i
            id=self.canvas.create_line(x0,y0,x1,y1,tags=(tag))
            self.coords[id] = (x0,y0,x1,y1)
            origColors[id] = "BLACK"
            widget2Bin[id] = tag
            bin2Widget[tag] = id
            seg2bin[tag] = i

        self.origColors = origColors
        self.widget2Bin = widget2Bin
        self.bin2Widget = bin2Widget
        self.widgetKeys = widget2Bin.keys()
        self.seg2bin = seg2bin
        id2Widget = {}

        for idkey in self.matcher.id2bin.keys():
            bin = self.matcher.id2bin[idkey]
            bintag = "segment_%d"%bin
            wid = self.bin2Widget[bintag]
            id2Widget[idkey] = wid
        self.id2Widget = id2Widget

    def getIdsForWidgets(self,wids):
        matchedIds = []
        for id in wids:
            if self.widgetKeys.count(id) > 0:
                binId = self.widget2Bin[id]
                mbinId = self.seg2bin[binId]
                if self.matcher.bin2id.has_key(mbinId):
                    obsIds = self.matcher.bin2id[mbinId]
                    for obsId in obsIds:
                        if matchedIds.count(obsId) == 0:
                            matchedIds.append(obsId)
        return matchedIds

    def highlightWidget(self,widgetIds):
        for widget in widgetIds:
            coords = self.coords[widget]
            bin = self.widget2Bin[widget]
            mbinId = self.seg2bin[bin]
            upperBound = self.scaledXCords[mbinId]
            lowerBound = self.scaledXCords[mbinId-1]
            x0 = coords[0]
            x1 = coords[2]
            y0 = max(self.scaledYCords)
            y1 = coords[1]
            y2 = coords[3]
            pcoords = (x0,y0,x0,y1,x1,y2,x1,y0)
            self.canvas.create_line(x1,y0,x1,y2,fill="BLUE",tag=("denbin"))

    def unHighlightWidget(self,widgetIds=[]):
        t1=time.time()
        if widgetIds == []:
            ids = self.matcher.selected
            wids = self.getWidgetsForIds(ids)
            widgetIds = wids
        for widget in widgetIds:
            if self.origColors.has_key(widget):
                color = self.origColors[widget]    
                self.canvas.itemconfigure(widget,fill=color)
        t2=time.time()
        self.canvas.delete("denbin")

class CDF(Plot,Subscriber):
    nden = 0
    def __init__(self,name,master,varName,y,csid=[],tsid=[],
        title="Empirical CDF",xLabel='X',yLabel='F(x)',xmin=None,
        xmax=None):
        self.master = master
        self.title = title
        self.varName = varName
        self.matcher = ICDF(varName,y,tsid,csid,xmin=xmin,xmax=xmax)
        self.fixedXmin = xmin
        self.fixedXmax = xmax
        self.tsid = tsid
        self.csid = csid
        self.x = self.matcher.xgrid
        self.y = self.matcher.cdf
        self.xLabel = xLabel
        self.yLabel = yLabel
        CDF.nden += 1
        name = "CDF_%d"%Density.nden
        Plot.__init__(self,name,master,self.x,self.y,title=title)
        self.canvas.pack(side=LEFT,anchor=W)
        self.type = "CDF"
        self.top.title(title)
        self.name =  name
        Subscriber.__init__(self,self.observer)

    def updateTime(self,tsId):
        tsId = tsId[0]
        title = "CDF %s %s"%(self.varName,self.variable.timeString[tsId])
        self.top.title(title)
        y = self.variable[:,tsId]
        self.canvas.delete('all')
        self.matcher = ICDF(self.varName,y,self.tsid,self.csid,xmin=self.fixedXmin,
            xmax=self.fixedXmax)
        self.x = self.matcher.xgrid
        self.y = self.matcher.cdf
        self.draw()
        
    def draw(self):
        self.setOvalColors()
        self.scaleBox()
        self.getMinMax()
        self.getRanges()
        self.getRatios()
        self.makeXTicks()
        self.makeYTicks()
        self.makeTickLabels()
        self.scaleTicks()
        self.scalePoints()
        self.drawOuterBox()
        self.drawAxis()
        self.drawTicks()
        self.drawIntegral()
        self.drawXLabel()
        self.drawYLabel()

        
    def drawIntegral(self):
        widget2Bin = {}
        bin2Widget = {}
        seg2bin = {}
        origColors = {}
        self.coords = {}
        self.minScaledX = min(self.scaledXCords)
        self.maxScaledY = max(self.scaledYCords)

        for i in range(len(self.scaledXCords)-1):
            xc = self.scaledXCords[i]
            yc = self.scaledYCords[i]

            i1=i+1
            x0 = self.scaledXCords[i]
            x1 = self.scaledXCords[i1]
            y0 = self.scaledYCords[i]
            y1 = self.scaledYCords[i1]
            tag = "segment_%d"%i
            id=self.canvas.create_line(x0,y0,x1,y1,tags=(tag))
            self.coords[id] = (x0,y0,x1,y1)
            origColors[id] = "BLACK"
            widget2Bin[id] = tag
            bin2Widget[tag] = id
            seg2bin[tag] = i

        self.origColors = origColors
        self.widget2Bin = widget2Bin
        self.bin2Widget = bin2Widget
        self.widgetKeys = widget2Bin.keys()
        self.seg2bin = seg2bin
        id2Widget = {}

        for idkey in self.matcher.id2bin.keys():
            bin = self.matcher.id2bin[idkey]
            bintag = "segment_%d"%bin
            wid = self.bin2Widget[bintag]
            id2Widget[idkey] = wid
        self.id2Widget = id2Widget

    def getIdsForWidgets(self,wids):
        matchedIds = []
        for id in wids:
            if self.widgetKeys.count(id) > 0:
                binId = self.widget2Bin[id]
                mbinId = self.seg2bin[binId]
                if self.matcher.bin2id.has_key(mbinId):
                    obsIds = self.matcher.bin2id[mbinId]
                    for obsId in obsIds:
                        if matchedIds.count(obsId) == 0:
                            matchedIds.append(obsId)
        return matchedIds

    def highlightWidget(self,widgetIds):
        maxWid = max(widgetIds)
        self.highlightCurve( maxWid )
        for widget in widgetIds:
            coords = self.coords[widget]
            bin = self.widget2Bin[widget]
            mbinId = self.seg2bin[bin]
            upperBound = self.scaledXCords[mbinId]
            lowerBound = self.scaledXCords[mbinId-1]
            x0 = coords[0]
            x1 = coords[2]
            y0 = max(self.scaledYCords)
            y1 = coords[1]
            y2 = coords[3]
            pcoords = (x0,y0,x0,y1,x1,y2,x1,y0)
            self.canvas.create_line(x1,y0,x1,y2,fill="BLUE",tag=("denbin"))
        
    def highlightCurve(self, widget):
        endOfHighlight = self.coords[widget]
        maxX = endOfHighlight[2]
        minY = endOfHighlight[3]
        curve = [self.minScaledX,self.maxScaledY,
                maxX,self.maxScaledY,
                maxX,minY]
        minWid = min(self.coords.keys())
        lessThan = range(minWid,widget+1)
        lessThan.reverse()
        for widget in lessThan:
            coords = self.coords[widget]
            [ curve.append(i) for i in coords ]
        curve = curve + [self.minScaledX,self.maxScaledY]
        self.canvas.create_polygon(curve,fill="YELLOW",outline="YELLOW",tag=("underCurve"))
        

    def unHighlightWidget(self,widgetIds=[]):
        t1=time.time()
        if widgetIds == []:
            ids = self.matcher.selected
            wids = self.getWidgetsForIds(ids)
            widgetIds = wids
        for widget in widgetIds:
            if self.origColors.has_key(widget):
                color = self.origColors[widget]    
                self.canvas.itemconfigure(widget,fill=color)
        t2=time.time()
        self.canvas.delete("denbin")
        self.canvas.delete("underCurve")

class PCP(Plot,Subscriber):
    nmpcp = 0
    def __init__(self,name,master,varNames,y,t,z=[],zName=None,xDelimiter=None,yDelimiter=None,title=None, xLabel=None, yLabel=None, ovalFill=None, ovalBorder=None, xPop='X', yPop='Y'):
        self.name = name
        self.master = master
        self.title=title
        self.type="pcp"
        self.z = z
        self.zName = zName
        self.varNames = varNames
        self.x = varNames
        self.nColors=6
        self.y = y
        self.yLabel = yLabel
        self.xLabel = xLabel
        self.ovalFill = ovalFill
        self.ovalBorder = ovalBorder
        self.labelDict = {}
        self.titleOnCanvas = 0
        self.pcpString = 'Parallel Coordinate Plot'
        self.setTitle(self.pcpString)
        self.matcher = IPCP(self.varNames,self.y,t,self.z,self.zName)
        Plot.__init__(self,name,master,self.x,self.y,xDelimiter=None,yDelimiter=None,title=self.title,
                      xLabel=xLabel, yLabel=yLabel, xDecimal=None, yDecimal=None,
                      ovalFill=None, ovalBorder=None,xPop=xPop,yPop=yPop)
        
        self.canvas.pack(side=LEFT,anchor=W)
        self.type = 'PCP'

        PCP.nmpcp +=1
        self.name = "pcp_%d"%PCP.nmpcp
        self.top.title(self.title)
        Subscriber.__init__(self,self.observer)

    def draw(self):
        self.setOvalColors()
        self.scaleBox()
        self.getMinMax()
        self.getRanges()
        self.getRatios()
        self.makeXTicks()
        #self.makeYTicks()
        self.makeTickLabels()
        self.scaleTicks()
        self.scalePoints()
        self.drawOuterBox()
        self.drawAxis()
        self.drawBars()
        self.drawTicks()
        self.drawPoints()
        #self.drawYLabel()
        #self.drawXLabel()
        
    def getMinMax(self):
        self.MaxX = float(len(self.x)-1) 
        self.MinX = 0.0
        self.MaxY = [max(i) for i in self.y]
        self.MinY = [min(i) for i in self.y]
        #print self.MaxX, self.MinX, self.MaxY, self.MinY

    def getRanges(self):
        self.countY = range(len(self.MaxY))
        self.xRangeValues = self.MaxX - self.MinX
        self.yRangeValues = [self.MaxY[i] - self.MinY[i] for i in self.countY]
        self.xIntegerRange = arange(self.MinX, self.MaxX+1)
        #print self.yRangeValues
        
    def getRatios(self):
        self.xratio = (self.x1Buffer - self.x0Buffer) / self.xRangeValues
        self.yratio = [(self.y1Buffer - self.y0Buffer) / self.yRangeValues[i] for i in self.countY]     
        #print self.xratio, self.yratio
        
    def makeXTicks(self):
        self.xTicks = range(len(self.varNames))
        #print self.xTicks
        
    def makeTickLabels(self):
        """Format x and y labels create decimal places by default or for
        argument passed in."""
        self.xTicksLabs = self.varNames
        #print self.xTicksLabs
        
    def scaleTicks(self):
        """Scale x and y axis ticks"""
        self.scaledXTicks = [self.x0Buffer + (self.xTicks[x] - self.MinX) * self.xratio for x in range(0,len(self.xTicks))]

    def scalePoints(self):
        """Scale x and y values to fit canvas"""
        self.scaledXCords = [self.x0Buffer + (self.xTicks[x] - self.MinX) * self.xratio for x in range(0,len(self.x))]
        self.scaledYCords = []
        c = 0
        for i in self.y:
            bar = [self.y0Buffer + (i[j] - self.MinY[c]) * self.yratio[c] for j in range(0,len(i))]
            self.scaledYCords.append(bar)
            c = c+1
        #print self.scaledYCords
        
    def drawBars(self):
        for i in self.scaledXTicks:
            g = self.canvas.create_line(i, self.y0Buffer, i, self.y1Buffer)
    
    def drawPoints(self):
        info = self.matcher
        if self.zName:
            info.colorMap(self.nColors)
        
        self.id2Widget = {}
        self.id2AllWidgets = {}
        self.widget2Id = {}
        self.idInfo = {}
        self.origColors = {}
        self.ovalLabel2Id = {}
        c = 0
        x1 = self.scaledXTicks
        for i in range(len(self.y[0])):
            yVals = [self.scaledYCords[k][i] for k in range(len(self.x))] 
            self.id2AllWidgets[c] = []
            obs = info.getObsforIds([c])
            if self.zName:
                colorId = info.colorId[c]
                color=SEQCOLORS[colorId]
            else:
                color = 'light grey'
            for j in range(len(yVals)):
                if j != int(self.MaxX):
                    h = self.canvas.create_line(x1[j],yVals[j],x1[j+1],yVals[j+1],
                    tag=('CONNECTOR', str(c)),fill=color)
                    self.origColors[h] = color
                    self.widget2Id[h] = c
                    self.id2AllWidgets[c].append(h)
                else:
                    pass
            
            c = c+1
        self.widgetKeys = self.widget2Id.keys()
        self.canvas.tag_bind("CONNECTOR", "<Control-1>")
        
    def drawTicks(self):
        """Draw ticks and value labels for X and Y axis"""
        stringLengths = []
        [stringLengths.append(len(i)) for i in self.xTicksLabs]
        maxLabelLength = max(stringLengths)
        if maxLabelLength <= 6:
            self.axisFontSize = 8
        else:
            self.axisFontSize = 8
            
        c = 0
        for i in self.scaledXTicks:
            self.drawLine(i, self.y0Inner, i, self.y0Inner + 4, 1)
            self.canvas.create_text(i+2 , self.y0Inner + 7, text=self.xTicksLabs[c], 
            font=('Times', options.AXISFONTSIZE), anchor = W)
            c = c+1
        if options.AXISFONTSIZE == 8:
            self.xStringRatio = (self.x1Buffer - self.x0Buffer) / options.SCREENFORFONT8
        else:
            self.xStringRatio = (self.x1Buffer - self.x0Buffer) / options.SCREENFORFONT6
        
    def getUniqueIds(self,csIds):
        unique = []
        [unique.append(i) for i in csIds if i not in unique]
        return unique

    def mouseLeftButtonRelease(self,event):
        stat='coords:'+str(event.x)+','+str(event.y)
        if self.interactionMode:
            self.lastx  = self.canvas.canvasx(event.x)
            self.lasty  = self.canvas.canvasy(event.y)
            x1 = self.startx
            x2 = self.lastx
            y1 = self.starty
            y2 = self.lasty
            self.createSelector([x1,y1,x2,y2])
            self.deleteSelector()
            oid = self.canvas.find_overlapping(x1,y1,x2,y2)
            self.selectedIds = self.cleanWidgetIds(oid)
            ids = self.getIdsForWidgets(self.selectedIds)
            uids = self.getUniqueIds(ids)
            newObs = self.matcher.getObsforIds(uids)
            commandKey = self.modButton+self.interactionModeString
            try:
                originCommand = ORIGINCOMMANDS[commandKey]
                if newObs:
                    self.dispatch(originCommand,newObs)
                    self.publish(originCommand,newObs)
                self.cursorReset()
            except:
                pass
                
    def newSelectedObservations(self,observations):
        self.newSelectObservations(observations)

    def newSelectObservations(self,observations):
        self.unHighlightWidget()
        self.matcher.deselect()
        self.selectObservations(observations)
        ids = self.matcher.selected
        
    def selectedObservations(self,observations):
        self.selectObservations(observations)

    def selectObservations(self,observations):
        ids = self.matcher.matchObservations(observations)
        self.matcher.select(ids)
        ids = self.matcher.selected
        wids = self.getAllWidgetsForIds(ids)
        #wids = self.getWidgetsForIds(ids)
        self.highlightWidget(wids)
        
    def getAllWidgetsForIds(self,ids):
        wids2Highlight = []
        for i in ids:
            wids = self.id2AllWidgets[i]
            for j in wids:
                wids2Highlight.append(j)
        return wids2Highlight
        
    def highlightWidget(self,widgetIds):
        """
        highlight widgets on view.

        widgetids (list): integer ids
        """
        for widget in widgetIds:
            self.canvas.tkraise(widget)
            self.canvas.itemconfigure(widget,fill=options.HIGHLIGHTCOLOR)

    def brushWidget(self,widgetIds):
        """
        brush widgets with widgetIds

        widgetIds (list): of ints widget ids
        """
        for widget in widgetIds:
            self.canvas.tkraise(widget)
            self.canvas.itemconfigure(widget,fill=options.BRUSHCOLOR)



    def unHighlightWidget(self,widgetIds=[]):
        if widgetIds == []:
            ids = self.matcher.selected
            wids = self.getAllWidgetsForIds(ids)
            widgetIds = wids
        for widget in widgetIds:
            if self.origColors.has_key(widget):
                color = self.origColors[widget]    
                self.canvas.itemconfigure(widget,fill=color)     
                
    def newBrushObservations(self,observations):
        self.removeBrushLine()
        self.unHighlightWidget()
        self.matcher.deselect()
        self.selectObservations(observations)
        ids = self.matcher.selected
        wids = self.getWidgetsForIds(ids)
        self.brushWidget(wids)
        # get complement set to selected ids
        compids = [j for j in self.IDS if ids.count(j) == 0]
        xvals = array([self.scaledXCords[i] for i in compids])
        yvals = array([self.scaledYCords[i] for i in compids])
        if len(xvals) > 2:
            self.fitLine(xvals,yvals,tagString="brushLine",fill=options.DEFAULTOVALFILL)
        else:
            pass


if __name__ == '__main__':

    from numpy.oldnumeric import *
    from gView import *
    import whrandom


    class ViewController:
        """ """
        def __init__(self,root,size=48,t=70,polywidth=5,polyheight=5,ovalWidth=5):
            self.root=root
            self.views={}
            self.mapCount = 0
            self.scatterCount = 0
            self.observer=viewObserver
            self.size=size #size of lattice (square)
            self.n=size*size #number of observations
            self.t = t
            if polywidth==5:
                width = 800./(self.n)
                height=width
                polywidth=width
                polyheight=height
            self.w=polywidth
            self.h=polyheight
            self.ovalWidth = ovalWidth
            self.makeCSTS()

        def makeCSTS(self):
            data = open("pcincome.txt",'r')
            d = data.readlines()
            data.close()
            data = []
            for row in d:
                row = row.strip()
                data.append([float(x) for x in row.split()])
            data = array(data)
            self.data = data
            self.n,self.t = data.shape
            self.variable1 = data[:,0]
            self.variable2 = data[:,-1]
            self.ts1 = data[0,:]
            self.ts2 = data[1,:]

        def listViews(self):
            self.observer.listItems()

        def iconify(self):
            for key in self.observer.items.keys():
                view = self.observer.items[key]
                view.iconify()

        def deiconify(self):
            for key in self.observer.items.keys():
                view = self.observer.items[key]
                view.deiconify()

        def deselectAll(self):
            pass

        def drawCSP(self):
            yvar = normal(5,20,shape=(self.n,self.t))
            xvar = normal(255,20,shape=(self.n,self.t))
            CScatterPlot("csp",self.root,xvar,yvar,self.ts1)

        def drawBoxPlot(self):
            self.root.configure(cursor=options.BUSYCURSOR)
            n = self.n
            x = self.variable1.tolist()
            name="box"
            varName="pcincome"
            Title = varName+' year __'
            BoxPlot(name,self.root,varName="var1",x=x,csids=range(n),tsids=[0])
            self.root.configure(cursor=options.CURSOR)

        def drawBoxPlotNSP(self):
            self.root.configure(cursor=options.BUSYCURSOR)
            n = self.n
            x = self.variable1.tolist()
            name="box"
            varName="pcincome"
            Title = varName+' year __'
            BoxPlot(name,self.root,varName="var1",x=x,csids=range(n),tsids=[0],stemPoints=0)
            self.root.configure(cursor=options.CURSOR)

        def DrawMap(self):
            options = {}
            s="Legend (sequential, diverging, qualitative)"
            options[1] = [s,StringVar()]
            options[2] = ["number of classes",IntVar()]
            options[2][1].set(5)

            SDialog("Map Generation",options)
            legendType = options[1][1].get()
            nClasses = options[2][1].get()
            #bins = eval(options[3][1].get())
            bins=[]
            self.root.configure(cursor=options.BUSYCURSOR)
            gis = open("us48.gis",'r')
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
            self.mapCount +=1
            ncol=self.size
            n=self.n
            x=arange(0,n)
            w=self.w
            h=self.h
            coords=polyDict
            timePeriod = whrandom.randint(0,self.t-1)
            timePeriod=0
            variable = self.data[:,timePeriod]
            if legendType == "qualitative":
                n = len(variable)
                k = nClasses
                variable = [ int(uniform(0,k)) for i in range(n) ]
                #print  variable


            name = "map"
            timePeriodString = "Per Capita Income %d"%(1929+timePeriod)
            name = timePeriodString
            Map(name,self.root,coords,variable,timePeriodString,
                timePeriod,poly2cs=poly2cs,cs2poly=cs2poly,
                classification ="percentiles",nBins=nClasses,
                bins=bins,legendType=legendType)
            self.root.configure(cursor=options.CURSOR)

        def defaultMap(self,):
            self.DrawMap(classification="sturges")

        def drawStdMap(self):
            self.DrawMap(classification="stdev")

        def drawQuintileMap(self):
            self.DrawMap(classification="equalCount",nBins=5)

        def drawScatter(self):
            self.root.configure(cursor=options.BUSYCURSOR)
            n = self.n
            x = self.variable1.tolist()
            y = self.variable2
            name="ms"
            varName="pcincome"
            scatTitle = varName+' year __'

            MoranScatter(name,self.root,x,y,
                         varName=varName,
                         variableX="1930",
                         variableY="2000",
                         t=0,
                         ovalFill='Green')
            self.root.configure(cursor=options.CURSOR)

        def drawTimePath(self):
            n = self.n
            t = self.t
            x = self.ts1
            y = self.ts2
            xVariableName = "CS 0"
            yVariableName = "CS 1"
            cs = [0,1]
            ts = range(t)
            tsLabels = [str(i) for i in ts]
            timeDict = {'Type':None}
            TimePath("tpath",self.root,x,y,ts,title='2 Variable Time Path',
            csIds = cs, tsLabels = [])

        def drawTimeSeries(self):
            crossSection = whrandom.randint(0, self.n - 1)
            n = self.n
            cs = range(n)
            y = self.data[crossSection,:]
            x = range(1929, self.t + 1929)
            tsLabels = [str(i) for i in x]
            TimeSeries("timeseries", self.root, x, y, title='Time Series',
            csIds = cs, tsLabels = tsLabels)
            
        def drawDensity(self):
            timePeriod = 0
            y = self.data[:,timePeriod] 
            csIds = range(len(y))
            tsIds = [timePeriod] * len(y)
            Density("density",self.root,"pcincome",y,csid=csIds,tsid=tsIds)

        def drawHistogram(self):
            n = self.n
            timePeriod = whrandom.randint(0, self.t -1)
            timePeriod = 0
            variable = self.data[:,timePeriod] 
            aTime = timePeriod + 1929
            x = variable
            y = []
            htitle = 'Histogram -- '+str(aTime) 
            xVariableName = "pcincome"
            yVariableName = "variable2"
            cs = range(n)
            ts = [0]
            timeDict = {'Type':None}
            Histogram("histo",self.root,x,y, title = htitle,xLabel = xVariableName,csIds = cs, tsIds = timePeriod)

        def drawPCP(self):
            self.n = 25
            v1 = normal(0, 1, self.n-1)
            v1 = v1.tolist()
            v2 = v1
            v2.sort()
            v3 = [v1.index(i) for i in v2] 
            print v1, v3
            v4 = normal(1000, 191, self.n-1)
            v4 = v4.tolist()
            v5 = normal(400, 50, self.n-1)
            v5 = v5.tolist()
            y = [v1,v3,v4,v5]
            t = 0
            vnames = ['income','rank','population','crime']
            PCP("pcp",self.root,vnames,y,t)
            
            

    root=Tk()
    tester=ViewController(root,size=5)
    menubar=Menu(root)
    root.config(menu=menubar)
    pulldown = Menu(menubar)
    pulldown.add_command(label="Map",underline=0,command=tester.DrawMap)
    pulldown.add_command(label="Stdev Map",underline=0,command=tester.drawStdMap)
    pulldown.add_command(label="Quintile  Map",underline=0,command=tester.drawQuintileMap)
    pulldown.add_command(label="Scatter",underline=0,command=tester.drawScatter)
    pulldown.add_command(label="TimePath",underline=0,command=tester.drawTimePath)
    pulldown.add_command(label="TimeSeries",underline=0,command=tester.drawTimeSeries)
    pulldown.add_command(label="Histogram",underline=0,command=tester.drawHistogram)
    pulldown.add_command(label="BoxPlot",underline=0,command=tester.drawBoxPlot)
    pulldown.add_command(label="BoxPlotNSP",underline=0,command=tester.drawBoxPlotNSP)
    pulldown.add_command(label="CSP",underline=0,command=tester.drawCSP)
    pulldown.add_command(label="Density",underline=0,command=tester.drawDensity)
    pulldown.add_command(label="PCP",underline=0,command=tester.drawPCP)
    pulldown.add_command(label="Quit",underline=0,command=root.quit)
    menubar.add_cascade(label="File",underline=0,menu=pulldown)

    pulldown = Menu(menubar)
    pulldown.add_command(label="List",underline=0,command=tester.listViews)
    pulldown.add_command(label="Iconify",underline=0,command=tester.iconify)
    pulldown.add_command(label="DeIconify",underline=0,command=tester.deiconify)
    menubar.add_cascade(label="Windows",underline=0,menu=pulldown)

    pulldown = Menu(menubar)
    pulldown.add_command(label="DeselectAll",underline=0,command=tester.deselectAll)
    menubar.add_cascade(label="Debug",underline=0,menu=pulldown)

    root.mainloop()
