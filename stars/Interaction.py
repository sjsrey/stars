"""
Defines different view to view interaction types and managing classes
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006 Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW
"""
from Subscriber import *

# module level interaction modes
INTERACTIONMODES = {0:"off",
                    1:"linking",
                    2:"brushing",
                    3:"traveling",
                    4:"brushTraveling"}

IMODES = [ "off","linking","brushing","traveling","brushTraveling" ]

OFF = 0
LINKING = 1
BRUSHING = 2
TRAVELING = 3
BRUSHTRAVELING = 4

ORIGINCOMMANDS = {
    "shiftlinking":"selectedObservations",
    "nonelinking":"newSelectedObservations",
    "shiftbrushing":"brushedObservations",
    "nonebrushing":"newBrushedObservations",
    "nontraveling":"travel",
    "shiftbrushtravel":"brushTravel",
    "nonebrushtravel":"newBrushTravel"
}

# define the types of interactions
class ViewObserver(Observer):
    """ """
    def __init__(self):
        Observer.__init__(self)
 

viewObserver = ViewObserver()
VIEWTYPES = ("map","scatter","timePath","boxplot","density","CDF")

for origin in VIEWTYPES:
    for destination in VIEWTYPES:
        viewObserver.addInteraction("brushing",origin,"brushedObservations",
                                    destination,"brushObservations")
        viewObserver.addInteraction("brushing",origin,"newBrushedObservations",
                                    destination,"newBrushObservations")
        viewObserver.addInteraction("linking",origin,"selectedObservations",
                                    destination,"selectObservations")
        viewObserver.addInteraction("linking",origin,"newSelectedObservations",
                                    destination,"newSelectObservations")

# pair specific interactions could also be added here
# interType, origin, method, destination, method
viewObserver.addInteraction("traveling","map","travel","scatter","newSelectObservations")
viewObserver.addInteraction("traveling","map","travel","histogram","newSelectObservations")
viewObserver.addInteraction("traveling","map","travel","timePath","newSelectObservations")
viewObserver.addInteraction("traveling","map","travel","map","newSelectObservations")
viewObserver.addInteraction("traveling","map","travel","boxplot","newSelectObservations")
viewObserver.addInteraction("traveling","map","travel","density","newSelectObservations")
viewObserver.addInteraction("traveling","map","travel","CDF","newSelectObservations")
viewObserver.addInteraction("traveling","timeSeries","travel","map","updateTime")
viewObserver.addInteraction("traveling","timeSeries","travel","density","updateTime")
viewObserver.addInteraction("traveling","timeSeries","travel","CDF","updateTime")
viewObserver.addInteraction("traveling","timeSeries","travel","scatter","updateTime")
viewObserver.addInteraction("traveling","timeSeries","travel","histogram","updateTime")
viewObserver.addInteraction("traveling","timeSeries","travel","boxplot","updateTime")
viewObserver.addInteraction("traveling","timeSeries","travel","timeSeries","updateTime2Time")
viewObserver.addInteraction("traveling","timeSeries","travel","timePath","updateTime2Time")
viewObserver.addInteraction("traveling","timePath","travel","timePath","updateTime2Time")
viewObserver.addInteraction("traveling","timePath","travel","timeSeries","updateTime2Time")
viewObserver.addInteraction("traveling","timePath","travel","map","updateTime")
viewObserver.addInteraction("traveling","timePath","travel","density","updateTime")
viewObserver.addInteraction("traveling","timePath","travel","CDF","updateTime")
viewObserver.addInteraction("traveling","timePath","travel","scatter","updateTime")
viewObserver.addInteraction("traveling","timePath","travel","histogram","updateTime")
viewObserver.addInteraction("traveling","timePath","travel","boxplot","updateTime")
# histo interactions as origins
hDest = ['histogram', 'map', 'scatter', 'timePath','boxplot','density','CDF']
hLinking = [["newSelectedObservations","newSelectObservations"], ["selectedObservations","selectObservations"]]
hBrushing = [["newBrushedObservations","newBrushObservations"], ["brushedObservations","brushObservations"]]
for view in hDest:
    for type in hLinking:
        viewObserver.addInteraction("linking", "histogram", type[0], view, type[1])
    for type in hBrushing:
        viewObserver.addInteraction("brushing", "histogram", type[0], view, type[1])
viewObserver.addInteraction("linking","histogram","newSelectedObservations","density","newSelectObservations")
viewObserver.addInteraction("linking","histogram","newSelectedObservations","CDF","newSelectObservations")
hOrig = ['histogram', 'map', 'scatter', 'timePath','boxplot','density','CDF']   
hLinking2 = [["newSelectedObservations","newSlice2Highlight"], ["selectedObservations","slice2Highlight"]]   
hBrushing2 = [["newBrushedObservations","newSlice2Brush"], ["brushedObservations","slice2Brush"]]   
for view in hOrig:
   for type in hLinking2:
      viewObserver.addInteraction("linking", view, type[0], "histogram", type[1])
   for type in hBrushing2:
       viewObserver.addInteraction("brushing", view, type[0], "histogram", type[1])
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","timePath","updateTime2Time")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","timeSeries","updateTime2Time")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","scatter","updateTime")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","map","updateTime")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","histogram","updateTime")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","boxplot","updateTime")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","density","updateTime")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","CDF","updateTime")
viewObserver.addInteraction("linking","map","newSelectedObservations","timeSeries","newSelectObservations")
viewObserver.addInteraction("linking","timePath","newSelectedObservations","timeSeries","newSelectObservations")
viewObserver.addInteraction("linking","scatter","newSelectedObservations","timeSeries","newSelectObservations")
viewObserver.addInteraction("brushTraveling","map","brushTravel","histogram","slice2Brush")
viewObserver.addInteraction("brushTraveling","map","brushTravel","scatter","brushObservations")
viewObserver.addInteraction("brushTraveling","map","brushTravel","boxplot","brushObservations")
viewObserver.addInteraction("linking","map","selectedObservations","boxplot","selectObservations")
#viewObserver.addInteraction("linking","map","newSelectedObservations","boxplot","newSelectObservations")
#viewObserver.addInteraction("brushing","map","brushedObservations","boxplot","brushObservations")
#viewObserver.addInteraction("brushing","map","newBrushedObservations","boxplot","newBrushObservations")
viewObserver.addInteraction("linking","map","newSelectedObservations","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","density","newSelectedObservations","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","CDF","newSelectedObservations","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","histogram","newSelectedObservations","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","scatter","newSelectedObservations","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","boxplot","newSelectedObservations","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","cscatter","newSelectedObservations","map","newSelectObservations")
viewObserver.addInteraction("linking","cscatter","newSelectedObservations","boxplot","newSelectObservations")
viewObserver.addInteraction("linking","cscatter","newSelectedObservations","density","newSelectObservations")
viewObserver.addInteraction("linking","cscatter","newSelectedObservations","CDF","newSelectObservations")
viewObserver.addInteraction("linking","cscatter","newSelectedObservations","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","cscatter","newSelectedObservations","scatter","newSelectObservations")
viewObserver.addInteraction("brushing","cscatter","brushedObservations","scatter","brushedObservations")
viewObserver.addInteraction("brushing","cscatter","newBrushedObservations","scatter","newBrushedObservations")
viewObserver.addInteraction("brushing","scatter","brushedObservations","cscatter","brushedObservations")
viewObserver.addInteraction("brushing","scatter","newBrushedObservations","cscatter","newBrushedObservations")
viewObserver.addInteraction("brushing","cscatter","brushedObservations","cscatter","brushedObservations")
viewObserver.addInteraction("brushing","cscatter","newBrushedObservations","cscatter","newBrushedObservations")
viewObserver.addInteraction("traveling","map","travel","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","cscatter","selectTsObservations")
viewObserver.addInteraction("traveling","timeSeries","travel","cscatter","selectTsObservations")
viewObserver.addInteraction("traveling","timePath","travel","cscatter","selectTsObservations")

#CS PCP interactions as 
vws4PCP = ["map", "density", "scatter", "timepath", "cscatter", "histogram", "boxplot", "CDF"]
for i in vws4PCP:
    viewObserver.addInteraction("linking", "PCP","newSelectedObservations",i,"newSelectObservations") 
    viewObserver.addInteraction("linking",i,"newSelectedObservations","PCP","newSelectObservations")    
viewObserver.addInteraction("linking","PCP","newSelectedObservations","PCP","newSelectObservations")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","PCP","updateTime")
viewObserver.addInteraction("traveling","map","travel","PCP","newSelectObservations")
viewObserver.addInteraction("traveling","timeSeries","travel","PCP","updateTime")

# table
viewObserver.addInteraction("linking","map","newSelectedObservations","table","selectObservations")
viewObserver.addInteraction("linking","cdf","newSelectedObservations","table","selectObservations")
viewObserver.addInteraction("linking","density","newSelectedObservations","table","selectObservations")
viewObserver.addInteraction("linking","scatter","newSelectedObservations","table","selectObservations")
viewObserver.addInteraction("linking","table","newSelectedObservations","map","newSelectObservations")
viewObserver.addInteraction("linking","table","newColumnSelected","map","updateTime")
viewObserver.addInteraction("linking","table","newColumnSelected","scatter","updateTime")
viewObserver.addInteraction("linking","table","newColumnSelected","density","updateTime")
viewObserver.addInteraction("linking","table","newColumnSelected","histogram","updateTime")
viewObserver.addInteraction("linking","table","newColumnSelected","CDF","updateTime")
viewObserver.addInteraction("brushing","map","newBrushedObservations","table","newBrushObservations")
viewObserver.addInteraction("traveling","map","travel","table","selectObservations")
viewObserver.addInteraction("traveling","timeSeries","travel","table","newSelectColumn")
viewObserver.addInteraction("linking","timeSeries","newSelectedObservations","table","newSelectColumn")
viewObserver.addInteraction("traveling","timePath","travel","table","newSelectColumn")

viewObserver.addInteraction("linking","table","newSelectedObservations","CDF","newSelectObservations")
viewObserver.addInteraction("linking","table","newSelectedObservations","density","newSelectObservations")
viewObserver.addInteraction("linking","table","newSelectedObservations","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","table","newSelectedObservations","CDF","newSelectObservations")
viewObserver.addInteraction("linking","table","newSelectedObservations","boxplot","newSelectObservations")
viewObserver.addInteraction("linking","table","newSelectedObservations","scatter","newSelectObservations")
viewObserver.addInteraction("linking","table","newSelectedObservations","histogram","newSelectObservations")
viewObserver.addInteraction("linking","table","newSelectedObservations","mtable","selectObservations")
# matable
viewObserver.addInteraction("linking","map","newSelectedObservations","mtable","selectObservationsCS")
viewObserver.addInteraction("traveling","map","travel","mtable","selectObservationsCS")
viewObserver.addInteraction("linking","mtable","newSelectedObservations","map","newSelectObservations")
viewObserver.addInteraction("linking","mtable","newSelectedObservations","density","newSelectObservations")
viewObserver.addInteraction("linking","mtable","newSelectedObservations","cscatter","newSelectObservations")
viewObserver.addInteraction("linking","mtable","newSelectedObservations","CDF","newSelectObservations")
viewObserver.addInteraction("linking","mtable","newSelectedObservations","boxplot","newSelectObservations")
viewObserver.addInteraction("linking","mtable","newSelectedObservations","scatter","newSelectObservations")
viewObserver.addInteraction("linking","mtable","newSelectedObservations","histogram","newSelectObservations")
viewObserver.addInteraction("linking","mtable","newSelectedObservations","table","selectObservations")
