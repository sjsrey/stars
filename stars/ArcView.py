"""
Reading ArcView projects for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):   Serge Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

Handles parsing of ArcView dbf and shapefiles. Currently only supports polygon
shapes.

"""

   
from Common import Options
import os
import shapereader as shp
#import dbfreader as dbf
import dbfload as dbf
import Projection
options = Options()
STARSHOME = options.getSTARSHOME()

class ArcViewProject:
    """Handles the reading of ArcView shape and dbf files.
    
    """
    def __init__(self,shpName):
        projectDir = os.path.dirname(shpName)
        prefix = os.path.basename(shpName).split(".")[0]
        self.dbfFileName = projectDir + "/" + prefix + ".dbf"
        dbfFile = dbf.DbfLoader(self.dbfFileName)
        shpFile = shp.shapefile(shpName)
        self.dbfFile = dbfFile
        self.shapeFile = shpFile
        self.__table = 0

    def summary(self):
        self.shapeFile.summary()
        self.dbfFile.summary()


    def table2variables(self):
        """sets the variable attribute which is a dictionary with variable
        names as keys and values as values."""
        if not self.__table:
            t = self.dbfFile.table2list()
            varNames = self.dbfFile.get_field_names()
            variables = {}
            for variable in varNames:
                variables[variable] = [ record[varNames.index(variable)] for record in t]
            self.variables=variables
            self.__table = 1

    def table2list(self):
        """returns entire table in a list of n lists, where n is the number of
        records in the dbf file."""
        #return [ rec.values() for rec in self.dbfFile.table2list()]
        return self.dbfFile.table2list()

    def getVariableNames(self):
        return self.dbfFile.get_field_names()

    def getVariable(self,name):
        self.table2variables()
        varNames = self.variables.keys()
        if name not in varNames:
            print 'Variable not found: %s'%name
        else:
            return self.variables[name]

    def joinVariables(self,var1,var2,delim=""):
        """combines two character variables to make a new variable.
        use to identify unique records in a dbf - for example combining county
        fips with state fips into countystatefips"""
        try:
            v1=self.getVariable(var1)
            v2=self.getVariable(var2)
            vnew = [ a+delim+b for a,b in zip(v1,v2)]
            return vnew
        except:
            return 0
   
    def uniqueValues(self,name):
        """Returns the unique values in a sequence"""
        d={}
        variable = self.getVariable(name)
        for value in variable:
            d[value] = value
        return d.keys()

    def uniqueSortedValues(self,name):
        """Returns the sorted unique values in a sequence"""

        v = self.uniqueValues(name)
        v.sort()
        return v
 
    def _in(self,val,seq):
        """Returns the first position index of val in seq. if val is not in
        seq -1 is returned."""
        try:
            id=seq.index(val)
            return id
        except:
            return -1


    def match(self,seq1,seq2):
        """Returns a list of id bridges

        idsij bridge contains the first position of each element in seq1 in
        seq2.

        idsji bridge contains the first position of each element in seq2 in
        seq1.
        """
        idsij = [ self._in(i,seq2) for i in seq1 ]
        idsji = [ self._in(i,seq1) for i in seq2 ]
        return [idsij,idsji]


if __name__ == '__main__':
    import Projection
    import CanvasCoords
    import FileIO
    from Tkinter import *

    root = Tk()
    class View:
        """Simple wrapper to display map"""
        def __init__(self,master,map,buffer=1.1):
            self.master = master
            self.map = map
            self.buffer = buffer

        def plot(self,width=400,height=400):
            map = self.map
            c = Canvas(self.master,width=width,height=height)
            c.pack()
            C = CanvasCoords.CanvasCoords()
            xrange = map.xrange * self.buffer
            C.set_coordinate_system(width,height,width/2,height/2,xrange)
            p2c2 = C.physical2canvas2
            for key in map.projected.keys():
                polygon = map.projected[key]
                pnts = [ p2c2(point) for point in polygon]
                if key % 2:
                    fill='yellow'
                else:
                    fill='blue'

                c.create_polygon(pnts,fill=fill,outline='black')




    projectName = raw_input("Enter shapefile name (with .shp): ")
    if projectName:
        proj = ArcViewProject(projectName)
        proj.summary()
        table = raw_input("Show attribute table (y or n)?")
        if table.upper() == 'Y':

            columnLabels = proj.getVariableNames()
            lists = proj.table2list()
            from DataViewer import MixedDataTable
            table = MixedDataTable(root,lists,name=proj.dbfFileName,
                    columnLabels=columnLabels)

        map = Projection.Map(projectName)
        plot = raw_input("plot shapes (y or n)?")
        top = Toplevel(root)
        if plot.upper() == 'Y':
            v = View(top, map)
            v.plot()
        name = projectName+".gis"
        map.writer = FileIO.GISWriter(name, map.projected)


        #root.mainloop()

