"""
File IO module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

This module reads and writes files for STARS.


"""

import Utility as UTILITY
import csv as CSV
import os as OS
from numpy.oldnumeric import *
from numpy.oldnumeric.mlab import *
from numpy.oldnumeric.user_array import *
import ConfigParser as CP



class csvWriter:
    def __init__(self,fileName,info,delimiter=','):
        """Class that writes csv files.
        arguments:
            fileName = (str) = name of the output file
            info = (list of lists) each list will be treated as a row in the
            output file.  Each item in each list will be seperateed by a comma.
        """
        writer = CSV.writer(open(fileName,"wb"),delimiter=delimiter)
        for row in info:
            writer.writerow(row)

class csvReaderCSTS:
    def __init__(self,fileName,delimiter=','):
        """Class that reads CSTS Variable Files.
        arguments:
            fileName = (str) = name of the output file
        returns:
            self.newVars = (dict) = dictionary with the new varName as the key
            and a list of lists as its value.
        """
        reader = CSV.reader(file(fileName),delimiter=delimiter)
        self.names = [ i.replace(" ", "_") for i in reader.next() ]
        self.name = self.names[0]
        self.newVars = {}
        first = reader.next()
        dataTypes = UTILITY.findDataTypes(first)
        first = UTILITY.applyDataTypes(dataTypes,first)
        fields = range(len(first))
        self.newVars[ self.name ] = [ [first[i]] for i in fields ] 
        for row in reader:
            rowVals = UTILITY.applyDataTypes(dataTypes,row)
            [ self.newVars[ self.name ][i].append( rowVals[i] ) for i in fields ]
    
class csvReaderCS:
    def __init__(self,fileName,delimiter=','):
        """Class that reads CS Variable Files.
        arguments:
            fileName = (str) = name of the output file
        returns:
            self.newVars = (dict) = dictionary with the new varName(s) as the key(s)
            and a list as value(s).
        """
        reader = CSV.reader(file(fileName),delimiter=delimiter)
        self.names = [ i.replace(" ", "_") for i in reader.next() ]
        fields = range(len(self.names))
        self.newVars = {}
        first = reader.next()
        dataTypes = UTILITY.findDataTypes(first)
        first = UTILITY.applyDataTypes(dataTypes,first)
        for i in fields:
            self.newVars[ self.names[i] ] = [ first[i] ] 
        for row in reader:
            rowVals = UTILITY.applyDataTypes(dataTypes,row)
            [ self.newVars[ self.names[i] ].append( rowVals[i] ) for i in fields ]

class csvReaderTS:
    def __init__(self,fileName,delimiter=','):
        """Class that reads TS Variable Files.
        arguments:
            fileName = (str) = name of the output file
        returns:
            self.newVars = (dict) = dictionary with the new varName(s) as the key(s)
            and a list as value(s).
        """
        reader = CSV.reader(file(fileName),delimiter=delimiter)
        self.names = [ i.replace(" ", "_") for i in reader.next() ]
        fields = range(len(self.names))
        self.newVars = {}
        first = reader.next()
        dataTypes = UTILITY.findDataTypes(first)
        first = UTILITY.applyDataTypes(dataTypes,first)
        for i in fields:
            self.newVars[ self.names[i] ] = [ first[i] ] 
        for row in reader:
            rowVals = UTILITY.applyDataTypes(dataTypes,row)
            [ self.newVars[ self.names[i] ].append( rowVals[i] ) for i in fields ]                                     

class projWriter:
    def __init__(self,fileDict):
        """Writes the STARS Project file in appropriate format.
        fileDict = (dict) = dictionary of filenames for each part of the STARS
        Project.
        types: 'data': Main Project name for data files.
               'weights': list of lists of weight matrix files:
                          [type of weight matrix, fileName]
              'gis': gis file name
        """
        self.fileDict = fileDict
        prjFile = fileDict['main']
        prefix = OS.path.basename(prjFile).split(".")[0]
        fprj = CP.ConfigParser()
        fprj.add_section('data')
        fprj.set('data', 'files', prefix)

        fprj.add_section('weight')
        try:
            galFiles = fileDict['gal']
            fprj.set('weight','gal',galFiles)
        except:
            pass
        
        try:
            galFiles = fileDict['spv']
            fprj.set('weight','spv',galFiles)
        except:
            pass
        
        try:
            galFiles = fileDict['fmt']
            fprj.set('weight','fmt',galFiles)
        except:
            pass
        
        fprj.add_section("gis") 
        try:    
            gis = fileDict['gis']
            fprj.set("gis", "gis", gis)
        except:
            pass
        
        fprj.add_section('graphics')
        try:
            coords = fileDict['coords']
            fprj.set('graphics', 'screen', coords)
        except:
            fprj.set('graphics', 'screen', 'None') 

        fprj.add_section("projection")
        try:
            projection = fileDict['projection']
            fprj.set('projection', 'type', projection)
        except:
            fprj.set('projection', 'type', 'None')

        print 'writing prj', prjFile   
        f = open(prjFile, "w")
        fprj.write(f)
        f.close()

def returnBaseFileName(fileName):
    """Overwrite this with OS stuff. """
    try:
        main = fileName.split("/")[-1]
    except:
        main = fileName
    return main
    

class GISWriter:
    """Writes STARS GIS Files"""
    def __init__(self, fileName, polyInfo):
        writer = CSV.writer(open(fileName, 'w'))
        for key in polyInfo.keys():
            writer.writerow([key])
            writer.writerow(polyInfo[key])


class GISReader:
    """Reads STARS GIS Files """
    def __init__(self, fileName):
        reader = CSV.reader(file(fileName))
        contents = []
        for row in reader:
            contents.append(row)
        n = len(contents)
        keyid = range(0, n, 2)
        ids = [ eval(contents[key][0]) for key in keyid ]
        polys = [ contents[key+1] for key in keyid]
        coords = [ map(eval, polycoords) for polycoords in polys]
        # ids can repeat for shapes with multiple parts
        self.ids = ids
        self.coords = coords
        self.info = zip(ids, coords)
        self.buildBridge()

    def buildBridge(self):
        """match shape to cross sectional ids
        
        
        1 shape can belong to only 1 cs id
        1 cs id can be associated with >= 1 shape
        """
        cs2shape = {}
        n = len(self.ids)
        ids = zip(range(n), self.ids)

        for shapeId, id in ids:
            if cs2shape.has_key(id):
                cs2shape[id].append(shapeId)
            else:
                cs2shape[id] = [shapeId]

        shape2cs = dict(ids)
        self.shape2cs = shape2cs
        self.cs2shape = cs2shape

class GALReader:
    """Reads a Geographic Algorithm Library weight matrix.
    
    
    Assumes all ids are integers and the file begins with the number of
    cross-sectional units:
    n
    id1 id1nn
    id11 id12 id13 .. 
    id2 id2nn
    id21 id22 id23...

    where n is the number of cross-sectional units,
    id1 is the id for an observation
    id1nn is the number of neighbors for id1
    id11-id13 are the ids of the id1nn neighbors to id1
    and so on.

    Attributes:
        galInfo (dictionary): keys are the ids, values is a list with two
        elements, the first is the number of neighbors (integer) and the
        second is a list (integer) of neighbor ids.
    """
    def __init__(self, fileName):
        """
        fileName (string): name of file holding GAL information (include .gal
        suffix)
        """
        reader = CSV.reader(file(fileName))
        galInfo = {}
        n = int(reader.next()[0])
        flag = 1
        while flag:
            try:
                id,nNeighbors = map(int, reader.next()[0].split())
                galInfo[id] = [nNeighbors, map(int, reader.next()[0].split())]
            except:
                flag = 0
        self.galInfo = galInfo
        

class GALWriter:
    """Writes a GAL object out to a text file."""
    def __init__(self, galInfo, fileName):
        """
        galInfo (dictionary): galInfo object created by GALReader, or in same
        format.

        fileName (string): name of file to write GAL to in ASCII format.
        """
        self.file = open(fileName,'w')
        keys = galInfo.keys()
        keys.sort()
        lines = []
        for key in keys:
            values = galInfo[key]
            nn = values[0]
            neighbors = values[1]
            lines.append("%d %d"%(key,nn))
            lines.append(" ".join(map(str,neighbors)))
        so="\n".join(lines)
        so = "%d\n%s"%(len(keys),so)
        self.file.write(so)
        self.file.close()


def testGal():
    gal = GALReader('states48.gal')
    GALWriter(gal.galInfo,'test.gal')
    return gal



if __name__ == '__main__':

    #csvTest = csvReaderCSTS("data/borderCSTSError.csv")
    #test = csvReader("borderCSTS.csv","CSTS")
    #test2 = csvReader("borderCS.csv","CS")
    d = {'data':'thisProject',
        'weights':[['gal','thisGal'],['full','thisFull'],['io','thisIO']],
        'gis':'thisGIS'}
    #p = projWriter(d)
    gal = testGal()


