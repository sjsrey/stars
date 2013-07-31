""" ProjectWorker.py

Utilities for ProjectMaker.py for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Mark V. Janikas mjanikas@users.sourceforge.net
            Sergio J. Rey sjrey@sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

Utilities for ProjectMaker.py.


"""

from Common import Options
import Utility as UTIL
import Data as DATA
import Matcher as MATCH
import ArcView as ARCVIEW
import FileIO as FIO
import Projection
from Tkinter import *
import Gis
import os as OS
import shutil as SHUTIL
import weight

import stars
options = Options()
STARSHOME = options.getSTARSHOME()

def notDone():
    print 'Not implemented'

class ProjVariable:
    """Variables for STARS Project

    name = str() name of the variable
    type = str() = CS, CSTS, TS
    values = list for CS and TS, list of list for CSTS
    methods:
        returnValues(): returns the list of values
        checkIn(): checks the variable into a dictionary
    """
    def __init__(self,name,type,values):
        self.name = name
        self.type = type
        self.values = values

class ProjectMaker:
    """Creates STARS Project

    projectName = str() default prefix from shpfile
    arc = 0 if using an csv file
    arc = 1 if using a arcview file
    """
    def __init__(self,fileName,arc=1,prj=0):
        self.fileName = fileName
        self.setProjectFiles(fileName)
        self.setOriginalFiles(fileName)
        self.initialFileName = fileName
        self.arc = arc
        self.prj = prj
        self.varDict = {}
        self.prjInfo = {}
        self.matrices = {}
        if self.prj == 1:
            self.useExisting()
        else:
            self.initiate()

    def changeProjPrefix(self,newPrefix):
        """Changes the project name prefix for output files.

        newPrefix = (str) = new name of the output project files.
        """
        self.projPrefix = newPrefix

    def setProjectFiles(self,fileName):
        self.projectDir = OS.path.dirname(fileName)
        self.projPrefix = OS.path.basename(fileName)
        try:
            self.projPrefix = self.projPrefix.split(".")[0]
        except:
            pass

    def setOriginalFiles(self,fileName):
        self.originalDir = OS.path.dirname(fileName)
        self.originalPrefix = OS.path.basename(fileName)
        try:
            self.origPrefix = self.origPrefix.split(".")[0]
        except:
            pass
        

    def useExisting(self):
        self.stars = StarsProject(self.fileName)
        self.arc = 0
        timeType =  self.stars.timeFreq
        start = self.stars.timeInfo[1]
        end = self.stars.timeInfo[2]
        within = ['MONTHLY', 'QUARTERLY']
        if timeType in within:
            s = start.split("/")
            startYear = s[-1]
            startSub = s[0]
            e = end.split("/")
            endYear = e[-1]
            endSub = e[0]
            if timeType == "MONTHLY":
                self.createMonthly(startM, startYear, endM, endYear)
            else:
                self.createQuarterly(startM, startYear, endM, endYear)
        else:
            if timeType == "DECADAL":
                self.createDecadal(start, end)
            elif timeType == "ANNUAL":
                self.createAnnual(start, end)
            else:
                self.createIrregular(int(end))
            
        regionNames = self.stars.regionNames
        ids = range(len(regionNames))
        self.n = len(regionNames)
        self.createVariable('csnames', 'CS', [regionNames])
        self.createVariable('csids', 'CS', [ids])
        variableNames = self.stars.getVariableNames()
        self.initial = {}
        for variable in variableNames:
            var = self.stars.dataBase.getVariable(variable)
            name = var.name
            type = var.varType
            varType = type.upper()
            if varType == "CSTS":
                n = var.n
                values = []
                for i in range(n):
                    row = var[i,:].tolist()
                    values.append(row)
                values =UTIL.TransposeList(values) 
                self.createVariable(name,varType,values)
                self.initial[name] = values
            elif varType == "CS":
                values = var[:,0].tolist()
                self.createVariable(name,varType,[values])
                self.initial[name] = values
            else:
                values = var[0,:].tolist()
                self.createVariable(name,varType,values)
                self.initial[name] = values

        try:
            self.report("Processing GIS Files")
            gisFiles = self.stars.listGISNames
            self.gisFileMain = gisFiles[0].split(".gis")[0]
        except:
            self.report("No GIS Files associated with this project")

        try:
            self.report("Processing Existing Binary Gal (*.gal) Files")
            galFiles = self.stars.options["weight"]["gal"][0].split()
            for galFile in galFiles:
                gfile = OS.path.join(self.projectDir,galFile) 
                print gfile, "GFILE"
                self.importMatrix(gfile+".gal","gal")
        except:
            self.report("No Existing Binary Gal Files.")
                
        try:
            self.report("Processing Existing Sparese Valued Gal (*.spv) Files")
            galFiles = self.stars.options["weight"]["spv"][0].split()
            for galFile in galFiles:
                gfile = OS.path.join(self.projectDir,galFile) 
                self.importMatrix(gfile+".spv","spv")
        except:
            self.report("No Existing Sparse Valued Gal Files.")

        try:
            self.report("Processing Existing Full Matrix (*.fmt) Files")
            galFiles = self.stars.options["weight"]["fmt"][0].split()
            for galFile in galFiles:
                gfile = OS.path.join(self.projectDir,galFile) 
                self.importMatrix(gfile+".fmt","fmt")
        except:
            self.report("No Existing Full Matrix Files.")

        self.projectSummary()


    def initiate(self):
        """Decides which type of initial data file to read"""

        if self.arc == 1:
            self.readArcView()
        else:
            self.readAttributeInfo()

    def readArcView(self):
        """Reads ArcView Files

        self.initial = (dict) with dbf field names as keys and list of values
        as values.
        """
        arc = ARCVIEW.ArcViewProject(self.fileName)
        arc.summary()
        arc.table2variables()
        self.initial = arc.variables 
        self.addInitialShapesVariable()
        self.arcInfo = arc
        self.projectedMaps = {}
        self.shapeFileName = self.createOutputFile(self.projPrefix,".shp")
        print self.shapeFileName
        
    def readAttributeInfo(self):
        """Reads CSV File for Project of type CS

        self.initial = (dict) with first row names as keys and list of values
        as values
        """
        file = self.fileName
        info = FIO.csvReaderCS(file)
        self.initial = info.newVars 
        self.addInitialShapesVariable()

    def addInitialShapesVariable(self):
        iKeys = self.initial.keys()
        s = range(len(self.initial[iKeys[0]]))
        self.initial["Shape IDs"] = s 

    def createInitialTable(self,sample=1):
        """Returns a tableList from the initial project info."""

        tableList = []
        fields = self.initial.keys()
        rows = len(self.initial[fields[0]])
        if sample == 1:
            if rows > 50:
                rows = 50
        for row in range(rows):
            tableList.append( [ self.initial[var][row] for var in fields ] )
        return tableList

    def createJoinTable(self,sample=1):
        """Returns a tableList from the join data info."""
        joinVars = self.data2Join.newVars
        tableList = []
        fields = joinVars.keys()
        rows = len(joinVars[fields[0]])
        csnames = self.getVariable("csnames")
        joinVars["csnames"] = csnames[0]
        fields = ["csnames"] + fields
        if sample == 1:
            if rows > 50:
                rows = 50
        for row in range(rows):
            tableList.append( [ joinVars[var][row] for var in fields ] )
        return tableList

    def createTableList(self,varNames):
        """Returns a tableList based on created STARS Project Variables.

        varNames = (list) = variable names from varDict
        returns a list of lists: first list has the names of the variables for
        the table to be created.  The second is a tableList for the body of
        the table.
        """
        tableList = []
        varList = []
        for var in varNames:
            v = self.varDict[var]
            vals = v.values
            if v.type == 'CSTS':
                t = 0
                for time in self.stringTime:
                    varList.append(var + ": " + time)
                    tableList.append(vals[t])
                    t = t+1
            else:
                varList.append(var)
                tableList.append(vals[0])
        tableList = UTIL.TransposeList(tableList)
        return [varList, tableList]

    def createNamesAndIDs(self,var1=[],var2=[],var3=[],delim="_"):
        """Create Names and IDs for Cross-Sections in the STARS Project.

        var1 = (list) = optional list of values for matching. default = shape integers
        var2 = (list) = optional list of values for joining before matching.
        var3 = (list) = optional list of values for CS labels AFTER matching.
        delim = (str) = delimiter for joining var1 and var2 forr matching.
        """
        name = "csnames"
        if var1:
            var1 = var1
        else:
            var1 = self.initial["Shape IDs"]
        if var2:
            var = UTIL.joinListValues(var1,var2,delim=delim)
        else:
            var = var1
        m = MATCH.Matcher(name,var)
        self.matchedIDs = m.matched
        self.unique = m.unique
        self.csIDs = range(len(self.unique))
        self.id2Row = m.scheme2Master
        self.row2Id = m.master2Scheme
        if var3:
            self.unique = [ var3[ self.id2Row[i][0] ] for i in self.csIDs ]
        self.varDict[name] = self.unique
        self.createVariable(name, 'CS', [self.unique])
        self.createVariable('csids', 'CS', [self.csIDs])            
        self.n = len(self.unique)
        self.csNameVar = name
        self.name2CSID = {}
        for i in range(len(self.unique)):
            self.name2CSID[ self.unique[i] ] = i
        if len(self.row2Id.keys()) != self.n:
            print """Aggregation Employed:  More shapes than cross-sectional units."""
            self.aggOn = 1
        else:
            self.aggOn = 0

    def getMatchedIDs(self):
        return self.matchedIDs

    def csSummary(self):
        """Creates summary of cross-sectional information."""
        cs1 = "Cross-Sectional Name Variable: csnames" 
        cs2 = "n = " + str(self.n)
        return "\n".join( [cs1,cs2] )

    def createRegionNames(self,vector):
        """Create Region Names for Project

        vector = list of items for names
        """
        self.regionNames = vector
        
    def createVariable(self,name,type,values):
        """Creates a STARS variable.

        name = (str) = the name of the variable for the STARS project (user defined)
        type = (str) = { 'CS', 'CSTS', 'TS' }
        values = a list of values
        """
        var = ProjVariable(name,type,values)
        self.varDict[name] = var
        
    def deleteVariable(self,varName):
        del self.varDict[varName]

    def getDBFVariableNames(self):
        """Returns list of DBF Variable Names"""

        return self.initial.keys()

    def getDBFVariable(self,name):
        """Returns list of values from named dbf field.

        name = (str) = name of dbf field
        """
        return self.initial[name]

    def getAllVariableNames(self):
        """Returns list of Project Variable Names"""

        return self.varDict.keys()

    def getTSVariableNames(self):
        """Returns list of Project Variable Names"""

        varList = []
        for i in self.varDict.keys():
            if self.varDict[i].type == "TS":
                varList.append(i)
        return varList

    def getCSVariableNames(self):
        """Returns list of Project Variable Names"""

        varList = []
        for i in self.varDict.keys():
            if self.varDict[i].type == "CS":
                varList.append(i)
        return varList

    def getCSTSVariableNames(self):
        """Returns list of Project Variable Names"""

        varList = []
        for i in self.varDict.keys():
            if self.varDict[i].type == "CSTS":
                varList.append(i)
        return varList

    def getVariableTypes(self):
        """Returns list of Project Variable Types"""

        keys = self.varDict.keys()
        types = [ self.varDict[i].type for i in keys ]

    def getVariable(self,name):
        """Returns a list of values from specified variable.

        name = (str) = variable name from self.varDict
        """
        return self.varDict[name].values

    def getVariableType(self,name):
        """Returns the type of the specified variable.

        name = (str) = variable name from self.varDict
        """
        return self.varDict[name].type

    def tsVariableSummary(self):
        """Creates a summary string for ts variables for report"""

        tsVars = self.getTSVariableNames()
        if tsVars:
            res = "Time Series Variables: " + ", ".join(tsVars)
        else:
            res = "No Pure Time Series Variables"
        return res

    def csVariableSummary(self):
        """Creates a summary string for cs variables for report"""

        csVars = self.getCSVariableNames()
        if csVars:
            res = "Cross-Sectional Variables: " + ", ".join(csVars)
        else:
            res = "No Pure Cross-Sectional Variables"
        return res

    def cstsVariableSummary(self):
        """Creates a summary string for csts variables for report"""

        cstsVars = self.getCSTSVariableNames()
        if cstsVars:
            res = "Panel Variables: " + ", ".join(cstsVars)
        else:
            res = "No Panel Variables"
        return res

    def variableSummary(self):
        """Creates a summary string for all types of variables in project for
        report.

        """
        ts = self.tsVariableSummary()
        cs = self.csVariableSummary()
        csts = self.cstsVariableSummary()
        leadIn = "Project Variable Summary"
        return "\n".join([leadIn,ts,cs,csts])

    def cs2Panel(self,varNames,newName,delete=0):
        """Creates a CSTS variable out of a series of EXISTING CS variables.
        varNames: list of CS varNames in temporal order
        newName: str() for the name of the new CSTS variable.
        delete: binary option. 0 = retain the CS vars the new CSTS variable
        was made out of.  1 = erase the CS variables from the project.  """
        newVals = []
        for var in varNames:
            newVals.append(self.getVariable(var)[0])
            if delete == 1:
                self.deleteVariable(var)
        self.createVariable(newName, "CSTS", newVals)

    def panel2CS(self,varName,delete=0):
        """Create t CS variables out of an existing panel variable.
        varName = str() the name of the panel variable to parse.
        delete = binary option. 0 = retain the panel var the new CS variables
        1 = erase the CS variables from the project.  """
        var = self.getVariable(varName)
        tLabs = self.stringTime
        tRange = range(self.t)
        for t in tRange:
            csName = varName+tLabs[t]
            vals = var[t]
            self.createVariable(csName, "CS", [vals])
        if delete == 1:
            self.deleteVariable(varName)


        
    def convertArcViewVariable(self,cohesionType,varName,colNames=[]):
        """Convert column(s) in dbf file to STARS variables.
           For CS and CSTS Variables only**

           cohesionType = (string) Type of data cohesion method
                Choices: Sum, Average, Max, Min
           colNames = list of column names in header file
           varName = (string) new variable name
           XXX WE NEED TO ADD A CHECK AGAINST LENGTH TIME PERIODS **
        """
        if len(colNames) > 1:
            type = "CSTS"
        else:
            type = "CS"
        sids = range(len(self.id2Row.keys()))
        newVariable = []
        for name in colNames:
            newColumn = []
            vals = self.initial[name]
            for id in sids:
                allRows = self.id2Row[id] 
                allVals = [ vals[row] for row in allRows ]
                if cohesionType != 'String':
                    allVals = [ float(i) for i in allVals ]
                if cohesionType == 'Sum':
                    newColumn.append( sum(allVals) )
                elif cohesionType == 'Average':
                    newColumn.append( (sum(allVals)) / (len(allVals) * 1.) )
                elif cohesionType == 'Max':
                    newColumn.append( max(allVals) )
                elif cohesionType == 'Min':
                    newColumn.append( min(allVals) )
                elif cohesionType == 'String':
                    newColumn.append( allVals[0] )
                else:
                    print "Incorrect or no cohesion method specified"
            newVariable.append(newColumn)
        self.createVariable(varName, type, newVariable)

    def importMatrix(self,fileName,type):
        self.report("Including matrix: " + OS.path.basename(fileName))
        self.matrices[fileName] = type 

    def readCSV_CS(self,fileName,delimiter=","):
        """Reads csv file with CS variables

        fileName = str() path/filename of csv file
        checks new vars into ProjectMaker
        returns list of new variable names
        """
        cs = FIO.csvReaderCS(fileName,delimiter=delimiter)
        for i in cs.names:
            self.createVariable(i, "CS", [cs.newVars[i]])
        return cs.names

    def readJoinCSV(self,fileName,delimiter=","):
        """Reads csv file with CS variables

        fileName = str() path/filename of csv file
        nameField = str() string to identify which column will be used to
        match with csnames
        checks new vars into ProjectMaker
        returns list of new variable names
        """
        self.data2Join = FIO.csvReaderCS(fileName,delimiter=delimiter)
        self.joinData = self.createJoinTable()

    def joinCS(self,master,slave):
        """Joins csv CSTS variables based on user defined matching.
        master = str() existing CS variable to serve as the master.
        slave = str() field name from the data file for matching.
        """        
        cs = self.data2Join
        slaveVals = cs.newVars[slave]
        masterVals = self.getVariable(master)[0]
        masterVals = [ i.strip("\"") for i in masterVals ]
        bridge = MATCH.createBridge(slaveVals,masterVals)
        print bridge
        fields = cs.names
        fields.remove(slave)
        for i in fields:
            new = MATCH.mapValues(bridge,cs.newVars[i])
            self.createVariable(i, "CS", [new] )

    def joinCSTS(self,master,slave):
        """Joins csv CSTS variables based on user defined matching.
        master = str() existing CS variable to serve as the master.
        slave = str() field name from the data file for matching.
        """
        cs = self.data2Join
        slaveVals = cs.newVars[slave]
        masterVals = self.getVariable(master)[0]
        masterVals = [ i.strip("\"") for i in masterVals ]
        bridge = MATCH.createBridge(slaveVals,masterVals)
        
        fields = cs.names
        fields.remove(slave)
        batch = MATCH.batchSplit(fields)
        varNames = batch['strings']
        varNames.sort()
        timeInfo = map(int,batch['ints'])
        timeInfo.sort()
        timeInfo = map(str,timeInfo)
        ordered = {}
        for i in varNames:
            ts = map(str,timeInfo)
            names = [ i+ts[t] for t in range(len(ts)) ]
            ordered[i] = names
        for i in ordered.keys():
            newName = i
            allTime = ordered[i]
            newVar = []
            for t in allTime:
                column = cs.newVars[t]
                newVar.append(column)
            newVar = UTIL.TransposeList(newVar)
            reordered = []
            for ind in bridge:
                reordered.append(newVar[ind])
            reordered = UTIL.TransposeList(reordered)
            self.createVariable(i, "CSTS", reordered )

    def readCSV_TS(self,fileName,delimiter=","):
        """Reads csv file with TS variables

        fileName = str() path/filename of csv file
        checks new vars into ProjectMaker
        returns list of new variable names
        """
        ts = FIO.csvReaderTS(fileName,delimiter=delimiter)
        for i in ts.names:
            self.createVariable(i, "TS", [ts.newVars[i]])
        return ts.names

    def readCSV_CSTS(self,fileName,delimiter=","):
        """Reads csv file with CSTS variable

        fileName = str() path/filename of csv file
        checks new vars into ProjectMaker
        returns variable name 
        """
        csts = FIO.csvReaderCSTS(fileName,delimiter=delimiter)
        self.createVariable(csts.name, "CSTS", csts.newVars[csts.name]) 
        return csts.name

    def readGAL(self,fileName):
        """Stub for reading Gal Matrices."""

        if self.prjInfo.has_key('weights'):
            self.prjInfo['weights'].append( ['gal',fileName] )
        else:
            self.prjInfo['weights'] = [['gal',fileName]]

    def createOutputFile(self,fileName,extension):
        """Creates the output file in question.  Places it in the correct
        directory and adds the extension.
        fileName = str() name of the file
        extension = str() the type of file
            e.g. .gis, .prj, .dat etc....
        """
        return self.projectDir + "/" + fileName + extension
    

    def makeGalWeights(self,wtType=weight.WT_ROOK):
        galInfo = weight.spweight(self.shapeFileName, wtType=type)
        galInfo.fixIslands()
        n = len(galInfo.numneigh)
        sout= []
        sout.append("%d"%n)
        for i in range(n):
            sout.append("%d %d"%(i, galInfo.numneigh[i]))
            sout.append(" ".join(["%d"%id for id in galInfo.neighbors[i]]))
        sout = "\n".join(sout)
        return sout
        
    def makeGalWeightsAgg(self,wtType=weight.WT_ROOK):
        galInfo = weight.spweight(self.shapeFileName, wtType=type)
        galInfo.fixIslands()
        csids = range(self.n)
        sout= []
        sout.append("%d"%self.n)
        for i in csids:
            neighs = []
            shapeIds = self.id2Row[i]
            for shape in shapeIds:
                neighs = neighs + galInfo.neighbors[shape]
            neighs = [ self.row2Id[neigh] for neigh in neighs ]
            unique = MATCH.uniqueList(neighs) 
            try:
                unique.remove(i)
            except:
                pass
            unique = map(str,unique)
            sout.append("%d %d"%(i, len(unique)))
            sout.append(" ".join(unique))
        sout = "\n".join(sout)
        return sout    

    def writeDHT(self,delimiter=","):
        """Writes the STARS header file.

        writes projectName.dat file for STARS
        """
        tInfo = [[self.timeType,self.stringTime[0],self.stringTime[-1]]]
        csnames = self.varDict["csnames"]
        name = [["csnames"]]
        vals = UTIL.splitList(csnames.values[0])
        info = tInfo + name + vals
        dhtFile = self.createOutputFile(self.projPrefix, ".dht")
        fdht = FIO.csvWriter(dhtFile, info, delimiter=" ")

    def writeCSO(self):
        """Writes the cross-sectional order for matching additional data"""
        csnames = self.varDict["csnames"]
        vals = UTIL.splitList(csnames.values[0])
        csoFile = self.createOutputFile(self.projPrefix, ".cso")
        f = FIO.csvWriter(csoFile, vals, delimiter=" ")

    def writeDAT(self,delimiter=","):
        """Writes the STARS dat file.

        writes projectName.dat file for STARS
        """
        info = []
        varNames = self.getAllVariableNames()
        varNames.remove("csnames")
        varNames.remove("csids")
        header = [ len(varNames) ] + varNames
        info.append(header)
        for var in varNames:
            v = self.varDict[var]
            info.append( [v.name, v.type] )
            vals = v.values
            if v.type == "CSTS":
                for id in range(self.n):
                    csYearVals = [ vals[year][id] for year in range(self.t) ]
                    info.append(csYearVals)
            else:
                info.append(vals[0])
        datFile = self.createOutputFile(self.projPrefix, ".dat")
        fdat = FIO.csvWriter(datFile, info, delimiter=" ")


    def processMatrices(self):
        format = {'gal':[], 'spv':[], 'fmt':[]}
        for matrixFile in self.matrices.keys():
            baseName = OS.path.basename(matrixFile)
            self.copyFile2Dir(matrixFile,self.projectDir)
            type = self.matrices[matrixFile]
            rootName = baseName.split(".")[0]
            format[type].append(rootName)
        for type in format.keys():
            files = format[type]
            if len(files) != 0:
                self.prjInfo[type] = " ".join(files)

    def copyFile2File(self,file1,file2):
        """Copies file1 to file2"""
        cmd = "cp " + file1 + " " + file2
        OS.popen(cmd)
        print "copying " + file1 + "\n" + file2

    def copyFile2Dir(self,file,dir):
        """Copies file to new dir"""
        fileName = OS.path.basename(file)
        file2 = OS.path.join(dir,fileName)
        self.copyFile2File(file,file2)
    
    def setScreenInfo(self):
        h = self.map.screenHeight
        w = self.map.screenWidth
        h += 0.0001 # sr kludge to get initial project read in stars correct
        coords = str(w) + " " + str(h)
        self.prjInfo['coords'] = coords

    def writePRJ(self):
        if len(self.matrices.keys()) != 0:
            self.processMatrices()
        self.prjInfo['data'] = self.projPrefix
        if self.arc == 1:
            self.prjInfo['gis'] = self.projPrefix
            self.prjInfo['projection'] = self.map.projectionName
            self.setScreenInfo()
        if self.prj == 1:
            gisFile = OS.path.join(self.originalDir,self.gisFileMain+".gis")
            if self.originalPrefix != self.projPrefix:
                newGIS = OS.path.join(self.projectDir,self.projPrefix+".gis")
                self.copyFile2File(gisFile,newGIS)
            else:
                gisFile = OS.path.join(self.originalDir,self.gisFileMain+".gis")
                self.copyFile2Dir(gisFile,self.projectDir)
            self.prjInfo['gis'] = self.projPrefix
        self.prjInfo['main'] = self.createOutputFile(self.projPrefix, ".prj")
        FIO.projWriter(self.prjInfo)

    def writeGIS(self, map):
        """Writes the scaled coordinates and centroids for last map drawn.

        Two files are generated: projectName.gis which has the coordinates for
        the polygons, and projectName.cnt which has information for the
        centroids. This method also needs to update the project file to
        specify the screen resolution that the coordinates were scaled for.
        """
        gisFile = self.createOutputFile(self.projPrefix, ".gis")
        fout = open(gisFile,'w')
        centroidFileName = self.projPrefix +".cnt"
        centroidFile = open(centroidFileName,'w')

        # XXX get cs-poly bridge, for now it is one to one, the format of the file
        # is as follows. first row is a header with three integers [1] csid,
        # [2] polygon count (start at 0, go to nk, where nk is the number of
        # polygons associated with csid, [3] number of coordinates. Following
        # this header the x,y points are written in stack form (i.e., newline
        # between x and y, not a tab. polygon keys are in order found in
        # original shapeFile.
        
        coords = map.screenCoords
        # get shape-parts bridges
        shape2poly = map.map.shape2poly
        poly2shape = map.map.poly2shape

        npolygons = len(coords)
        polys = []
        csidPolyCount = {}
        pid = 0
        for polyid in range(npolygons):
            coord = coords[polyid]
            # build up string of stacked xy points
            t = [ "%f\n%f"%(p[0],p[1]) for p in coord]
            t = "\n".join(t)
            # header: csid polyid numberOfCoords
            # XXX key will have to be changed to a cs id, and the 0 will also
            # have to be change to reflect the current part (or polygon)
            # belonging to the cs unit
            shapeId = poly2shape[polyid]
            csid = self.row2Id[shapeId]
            if csidPolyCount.has_key(csid):
                csidPolyCount[csid] = csidPolyCount[csid] + 1 
            else:
                csidPolyCount[csid] = 0
            count = csidPolyCount[csid]
            head="%d\t%d\t%d\n"%(csid,count,len(coord)*2)
            fout.write(head+t+"\n")

            # centroid
            #newCoords = []
            #t = [ newCoords.extend(list(p)) for p in coord ]
            #polys.append(Gis.Polygon(newCoords))
            #centroid = polys[-1].getCentroid()
            #area = polys[-1].getArea()
            #centroid/poly info
            #polygonId x y area
            #st ="%d\t%f\t%f\t%f\n"%(key,centroid[0],centroid[1],area)
            #centroidFile.write(st)


        #fout.close()
        #centroidFile.close()
        self.polys = polys


        # XXX add screen coords to prj file
    def createMap(self,shapeFile,projectionType):
        self.map = Projection.Map(shapeFile, projectionType)

    def createDecadal(self,startYear,endYear):
        """Create Decadal Time Series.

        startYear = (int) = start year, endYear = (int) = end year
        """
        time = DATA.Decadal(startYear,endYear)
        self.numericTime = time.numeric
        self.stringTime = time.string
        self.t = len(self.numericTime)
        self.timeType = time.timeType
        self.timeSummary = time.timeSummary
            
    def createAnnual(self,startYear,endYear):
        """Create Annual Time Series.

        startYear = (int) = start year, endYear = (int) = end year
        """
        time = DATA.Annual(startYear,endYear)
        self.numericTime = time.numeric
        self.stringTime = time.string
        self.t = time.t
        self.timeType = time.timeType
        self.timeSummary = time.timeSummary

    def createQuarterly(self,startSub,startYear,endSub,endYear):
        """Create Quarterly Time Series.

        startSub = (int) = {1,2,3,4}, startYear = (int) = start year
        endYear = (int) = {1,2,3,4}, endYear = (int) = end year
        """
        time = DATA.SubAnnual(startSub,startYear,endSub,endYear,division=4)
        self.numericTime = time.numeric
        self.stringTime = time.string
        self.t = len(self.numericTime)
        self.timeType = time.timeType
        self.timeSummary = time.timeSummary
        
    def createMonthly(self,startSub,startYear,endSub,endYear):
        """Create Monthly Time Series.

        startSub = (int) = {1:12}, startYear = (int) = start year
        endYear = (int) = {1:12}, endYear = (int) = end year
        """
        time = DATA.SubAnnual(startSub,startYear,endSub,endYear,division=12)
        self.numericTime = time.numeric
        self.stringTime = time.string
        self.t = len(self.numericTime)
        self.timeType = time.timeType
        self.timeSummary = time.timeSummary
        
    def createIrregular(self,t):
        """Create Irregular Time Series.
        
        t = (int) = number of time periods
        """
        time = DATA.Irregular(t)
        self.numericTime = time.numeric
        self.stringTime = time.string
        self.t = len(self.numericTime)
        self.timeType = time.timeType
        self.timeSummary = time.timeSummary

    def reportTimeInfo(self):
        """Reports Time Series Information."""

        self.report(self.timeSummary)

    def matrixSummary(self):
        try:
            info = []
            for matrixFile in self.matrices.keys():
                entry = self.matrices[matrixFile] + ": " + matrixFile 
                info.append(entry)
            info = "\n".join(info)
            intro = "Matrix Summary\nType File\n"
            output = intro + info
        except:
            output = "There are no matrices currently associated with this project."
        return output

    def changeTimeLabels(self,tsVarName):
        """Changes the time period labels for the project.  Allows the user to
        read in a TS variable via self.readCSV_TS and apply it as time string
        labels.

        tsVarName = (str) = name of the TS variable to use as labels
        """
        tsVar = self.getVariable(tsVarName)
        tsVals = tsVar.values
        if len(tsVals) == self.t:
            self.stringTime = tsVals
        else:
            print "Time period labels do not match the number of time periods"
        
    def projectSummary(self):
        """Reports all the summary information for the current project."""
        intro = "\nProject Description\nProject Name: " + self.fileName
        csSum = self.csSummary()
        tsSum = self.timeSummary
        vSum = self.variableSummary()
        mSum = self.matrixSummary()
        body = [csSum, tsSum, vSum, mSum]
        body = "\n\n".join(body)
        self.report(body)
        return intro + "\n" + body
        
    def report(self,string2Print):
        """Prints summary strings to the screen.

        string2Print = (str) string to print to screen
        """
        print string2Print

    # shape stuff
    def getPolygons(self):
        """scale and return unprojected polygons"""
        self.map = Projection.Map(self.fileName)
        return self.map.projected

    def getPolygonsMercator(self):
        """scale and return unprojected polygons"""
        self.map = Projection.Map(self.fileName, Projection.MercatorProj)
        return self.map.projected
    

        
class StarsProject(stars.Project):
    """Wrapper to read/handle exisiting stars project"""
    def __init__(self, name):
        """
        name: (string) STARS project file with .prj extension.
        """
        stars.Project.__init__(self,name)
        self.ReadProjectFile(name)



if __name__ == '__main__':
    pass


