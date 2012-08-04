"""
Common options and utility functions/classes for STARS
----------------------------------------------------------------------
AUTHOR(S):  Serge Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:
Defines all options (general and platform specific) for STARS modules.



TODO
    - Decide if we should distinguish between user installation and system
      installation with regard to paths.

    - Determine which options should go in here and move out of various STARS
      modules.

    - Decide on hierarchy for options: i.e., all options on one level, or two
      or more levels with nested dictionaries.

    - Add an interface for displaying and changing options. For now these will
      be via methods in Options, perhaps a GUI wrapper gets built in starsgui

"""
import sys
import os

def exitHandler(message):
    raw_input(message)
    sys.exit()

class Options:
    """Wrapper for STARS options"""
    def __init__(self):
        self.setPLATFORM()

    def setPLATFORM(self,platform=sys.platform):
        self.__PLATFORM=platform
        # XXXmight have to add a check for whether we are running as a script or
        # XXXa py2exe binary when determining STARSHOME

        # find location of starsgui.py and set STARSHOME
        self.setSTARSHOME(os.path.dirname(sys.argv[0])) 
        self.setDefaults()

    def setDefaults(self):
        """Resets all defaults to those of platform."""

        # platform agnostic options go here
        self.BRUSHCOLOR="Red"
        self.HIGHLIGHTCOLOR="Blue"
        self.CANVASBACKGROUND="White"
        self.VIEWBACKGROUND="White"

        self.SCREENFORFONT6 = 118 # XXX MJ what are these?
        self.SCREENFORFONT8 = 89 #  XXX MJ what are these? change to be determined by platform 

        self.OUTERBOXPLOTS = [.99, .01]
        self.INNERBOXPLOTS = [.90, .1]
        self.BUFFERBOXPLOTS = [.88, .12]
        self.DEFAULTOVALFILL = 'SkyBlue2'
        self.DEFAULTOVALBORDER = 'Black'
        self.NEGATIVEOVAL = 2
        self.POSITIVEOVAL = 2*2
        self.CURSOR = "tcross"
        self.STARCURSOR = "star"
        self.BUSYCURSOR = "watch"
        self.HIGHLIGHTFINISH = 'Purple'
        self.HIGHLIGHTSTART = 'Green'
        self.NEWTITLE = 'New Title'
        self.NEWXLABEL = 'New X Label'
        self.NEWYLABEL = 'New Y Label'
        self.SCALE=0.75
        self.RANDOMCOLORS=["yellow","blue","red","green"] # debugging
        self.AXISFONTSIZE=8
        self.TITLEFONTSIZE=10
        self.TOPOFSCREEN=15
        self.VIEWFONT='Times'

        # end platform agnostic options


    
        # start platform specific options
        # to add a platform, add a new method below named after the platform
        # and extend the PLATFORMS dictionary accordingly

        PLATFORMS={'win32':self.win32,
	'cygwin':self.win32,
        'darwin':self.darwin,
        'linux2':self.linux}
        try:
            #pf = self.getPLATFORM()
            #print pf
            PLATFORMS[self.getPLATFORM()]()
        except:
            message="Sorry, STARS is not yet supported on %s"%self.__PLATFORM
            message+="\n Hit Return to exit...."
            exitHandler(message)
        self.PLATFORMS = PLATFORMS


    def win32(self):
        """Configure common options for windows"""
        #print 'setting win32'
        self.setLabelFontFamily("Times")
        self.setLabelFontSize("11")
        self.setCellFontFamily("Times")
        self.setCellFontSize("10")
        self.AXISFONT=8
        self.TITLEFONT=10

        
    def darwin(self):
        """Configure common options for darwin"""
        #print 'setting darwin'
        self.setLabelFontFamily("Times")
        self.setLabelFontSize("14")
        self.setCellFontFamily("Times")
        self.setCellFontSize("12")
        self.AXISFONTSIZE=10
        self.TITLEFONTSIZE=12
        self.TOPOFSCREEN=15

    def linux(self):
        self.setLabelFontFamily("Times")
        self.setLabelFontSize("14")
        self.setCellFontFamily("Times")
        self.setCellFontSize("12")
        self.AXISFONTSIZE=10
        self.TITLEFONTSIZE=12
        self.TOPOFSCREEN=15


    # methods called by platform methods

    def getSTARSHOME(self):
        return self.__STARSHOME

    def setSTARSHOME(self,home):
        self.__STARSHOME=home

    def getPLATFORM(self):
        return self.__PLATFORM


    def setLabelFontFamily(self,labelFontFamily):
        self.__labelFontFamily = labelFontFamily

    def getLabelFontFamily(self):
        return self.__labelFontFamily

    def setLabelFontSize(self,labelFontSize):
        self.__labelFontSize = labelFontSize

    def getLabelFontSize(self):
        return self.__labelFontSize

    def setCellFontSize(self,cellFontSize):
        self.__cellFontSize = cellFontSize

    def getCellFontSize(self):
        return self.__cellFontSize

    def setCellFontFamily(self,cellFontFamily):
        self.__cellFontFamily = cellFontFamily

    def getCellFontFamily(self):
        return self.__cellFontFamily

    def setHIGHLIGHTCOLOR(self,color):
        self.HIGHLIGHTCOLOR=color

    def setBRUSHCOLOR(self,color):
        self.BRUSHCOLOR=color

    def loadExample(self):
        """XXX this is just a test method to see if the path munging works. it needs
        to be removed before release.
        """
        fileName = "csiss.dat"
        fileDir = "data"
        exampleFile = os.path.join(self.getSTARSHOME(),fileDir,fileName)
        f=open(exampleFile,'r')
        self.contents = f.readlines()
        f.close()
        return exampleFile

if __name__ == '__main__':
    from Numeric import *
    import Tkinter as Tk
    import DataViewer as DV

    class App(Options):
        """ """
        def __init__(self):
            Options.__init__(self)
            print 'in const'
            print self.getSTARSHOME()
            top = Tk.Tk()
            a=zeros((10,10))
            self.a = a
            self.top= top
        def draw(self):
            labelFontFamily = self.getLabelFontFamily()
            labelFontSize = self.getLabelFontSize()
            cellFontSize = self.getCellFontSize()
            cellFontFamily = self.getCellFontFamily()
            top = Tk.Toplevel()
            DV.DataTable(top,self.a,name=self.getPLATFORM(),
                    labelFamily=labelFontFamily,
                    labelSize=labelFontSize,
                    cellFamily=cellFontFamily,
                    cellSize=cellFontSize)


    test=App()
    print 'STARSHOME: ',test.getSTARSHOME()
    # draw a table in the win32 platform font size
    #test.setPLATFORM('win32')
    #test.draw()
    # draw a table in the darwin platform font size
    test.setPLATFORM('darwin')
    test.draw()
    test.top.mainloop()
    # draw a table in the platform default font size
    #test.setPLATFORM()
    #test.draw()
