"""
Core module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW
"""

import ConfigParser
import Errors
import sys
import os
cf=ConfigParser.ConfigParser()
#env = os.environ
#if env.has_key("STARSHOME"):
#    STARSHOME=env['STARSHOME']
#else:
#    s="Please set your STARSHOME environment variable."
#    Errors.Error(s)
#    sys.exit()
#STARSHOME="/Users/serge/Research/starssf/stars/src/"

import Common
options = Common.Options()
import Data

cf=ConfigParser.ConfigParser()
try:
    cf.read(".starsrc")
    CANVASBACKGROUND=cf.get('graphics','canvasBackground')
    DEVICE=cf.get('graphics','device')
except:
    #cfile = os.path.join(options.getSTARSHOME(),".starsrc")
    #print cfile
    #cf.read(cfile)
    CANVASBACKGROUND="lightgray"
    DEVICE="desktop"




from pickle import *
from Database import *
from Messages import *
from Table import *
import string
import os.path

from Esda import *
from Inequality import *
from Markov import *
from Mobility import *
#from SpEcon import *
import version

BODYFMT=[[8,3]]


P="STARS: Space-Time Anaysis of Regional Systems\nVersion"
PROGRAM="%s %s from %s.\n"%(P,version.VERSION,version.DATE)
PROGRAM=PROGRAM+"\n"+"""STARS is free software and comes with ABSOLUTELY NO WARRANTY.
You are welcome to redistribute it under certain conditions."""
PROGRAM=PROGRAM+"\nType  \"Copyright()\", \"Credits()\" or \"License()\" for more information."
PROGRAM=PROGRAM+"\nType  \"shelp()\" for help." 

copyright="""Copyright (C) 2000-2011, Sergio J. Rey.\n"""
copyright="""Copyright (C) 2012-2014, STARS Developers.
All rights reserved.
email: sjrey@users.sourceforge.net
web: http://stars-py.sourceforge.net/"""
credits="""\nSTARS Team (a.k.a. the 'All-STARS')\n
PROJECT DIRECTOR
Sergio J. Rey         sjrey@users.sourceforge.net

DEVELOPERS
Core group with write access to STARS source, currently
consisting of

Jared Aldstadt       aldstadt@users.sourceforge.net
Boris Dev            borisdev@users.sourceforge.net
Mark V. Janikas      mjanikas@users.sourceforge.net
Young-Sik Kim        oriys@users.sourceforge.net
Sergio J. Rey        sjrey@users.sourceforge.net
Tadesse Sefer        tsefer@users.sourceforge.net
Crystal English      crystal.english.127@gmail.com
Daisaku Yamamoto     daisakuy@users.sourceforge.net
Tong Zhang           leibi@users.sourceforge.net 

COLLABORATORS
STARS has benefitted from the invaluable help of
these people, who contributed suggestions, data,
bug fixes or documentation:

Charlotte Coulter    coulter@rohan.sdsu.edu
Julie Le Gallo       jlegallo@uiuc.edu
Liang Guo            guo@rohan.sdsu.edu
Dennis Larson        larson@rohan.sdsu.edu
Youngwoo Lee         giant890@dreamwiz.com
Yuying Li            yli@rohan.sdsu.edu
Daniel Mattheis      mattheis@rohan.sdsu.edu

As STARS is an open source and collaborative project, we would like to invite
any interested developer, user, or researcher to join us. Feel free to drop any
of the Developers an email or stop by our home page:
http://stars-py.sourceforge.net/ """


def Credits():
    print credits

def Copyright():
    print copyright

def License():
    f=open("license.txt",'r')
    l=f.readlines()
    s="".join(l)
    print s
    f.close()

def Opening():
    print PROGRAM
    

class Project:
    """Stars project.
    
    Example Usage:
        >>> from stars import Project
        >>> s=Project("s")
        >>> s.ReadData("csiss")
        >>> income=s.getVariable("pcincome")
        >>> region=s.getVariable("bea")
        >>> w=spRegionMatrix(region)
        >>> mi=Moran(income,w)
        >>> print(mi.mi[70])
        0.38918107312
    """
    def __init__(self,name):
        self.name = name
        self.dataBase = Database()
        self.getVariable = self.dataBase.getVariable
        self.getMatrix = self.dataBase.getMatrix
        self.addMatrix = self.dataBase.addMatrix
        self.getMatrixNames = self.dataBase.getMatrixNames
        self.getVariableNames = self.dataBase.getVariableNames
        self.getTSVariableNames = self.dataBase.getTSVariableNames
        self.getCSVariableNames = self.dataBase.getCSVariableNames
        self.getCSTSVariableNames = self.dataBase.getCSTSVariableNames


    def initialize(self):
        #options is a dictionary with sections as keys, values are
        #
        options={}
        options["data"] = {"files":[]} 
        options["gis"] ={"gis":[]}
        options["graphics"] = {"screen":[]}
        options["weight"] = {"gal":[], "spv":[], "fmt":[]} 
        options["projection"] = {"type":[]}
        self.options = options

        
    def ReadProjectFile(self,fileName):
        #assumes extension is passed into fileName

        #check for file existence
        if os.path.exists(fileName):
            self.initialize()
            config = ConfigParser.ConfigParser()
            config.read(fileName)
            projectDir = os.path.dirname(fileName)
            #print config.sections()
            for section in config.sections():
                options = config.options(section)
                for option in options:
                    value = config.get(section,option)
            #        print section,option,value
                    sec=self.options[section]
                    opt=sec[option]
                    opt.append(value)
                    sec[option]=opt
                    self.options[section]=sec
           # self.summarizeOptions()


            # read data files
            dataFiles = self.options["data"]["files"]
            for dataFile in dataFiles:
           #     print dataFile
                dfile = os.path.join(projectDir,dataFile)
           #     print dfile
                self.ReadData(dfile)
            #print "data files"

            # read any gal matricies
            try:
                galFiles = self.options["weight"]["gal"][0].split()
                print galFiles
                for galFile in galFiles:
           #         print galFile
                    gfile = os.path.join(projectDir,galFile)
                    self.ReadGalMatrix(gfile)
            #print "gal"
            except:
                print "No Weights Matrices"

            # read any gis boundary files
            self.listGISNames = []
            gisFiles = self.options["gis"]["gis"]
            for gisFile in gisFiles:
                fileName = gisFile+".gis"
                self.listGISNames.append(fileName)
                fileName = os.path.join(projectDir,fileName)
                self.ReadGisFile(fileName)

                fileName = os.path.join(projectDir,gisFile+".cnt")
                if os.path.exists(fileName): 
                    self.readCentroids(fileName)
                else:
                    self.__calcCentroids()
            self.gisResolution = self.options["graphics"]["screen"]
        else:
            print "Error: Cannot read project file: %s"%fileName

    def writeProjectFile(self,fileName):
        dataFile = fileName.split(".")[0]
        dataFileName = dataFile+".dat"
        dataHeaderName = dataFile+".dht"
        self.writeData(dataFileName)
        self.writeDataHeader(dataHeaderName)
        fo = open(fileName,'w')
        so = "[data]\nfiles: %s"%os.path.basename(dataFile)
        fo.write(so)
        so = "\n[weight]\n"
        fo.write(so)
        options = self.options
        wnames = options["weight"]
        gal = wnames["gal"]
        if len(gal) > 0:
            so = "gal: "+(" ").join(gal)
            so = so+"\n"
            fo.write(so)

        gis = options["gis"]
        gisfiles = gis["gis"]
        so = "\n[gis]\n"
        fo.write(so)
        if len(gisfiles) > 0:
            so = "gis: "+(" ").join(gisfiles)
            so = so+"\n"
            fo.write(so)

        graphics = options["graphics"]
        screenfiles = graphics["screen"]
        so = "\n[graphics]\n"
        fo.write(so)
        if len(screenfiles) > 0:
            so = "screen: "+(" ").join(screenfiles)
            so = so+"\n"
            fo.write(so)
        else:
            fo.write("screen: None")

        fo.close()        
        if self.options["graphics"]["screen"]:
            self.writeGis()
            self.writeCentroids()

    def writeGis(self):
        filePrefix =self.options["gis"]["gis"][0]
        fo = os.path.join(self.directory,filePrefix+".gis")
        f = open(fo,"w")
        c = self.newcoords
        keys = c.keys()
        csCount = {}
        sall=[]
        for key in keys:
            coords = c[key]
            cs = self.poly2cs[key][0]
            if csCount.has_key(cs):
                csCount[cs] +=1
            else:
                csCount[cs] = 0
            sout = "%d\t%d\t%d"%(cs,csCount[cs],len(coords))
            cs = ["%12.8f"% coord for coord in coords]
            s = [sout]
            s.extend(cs)
            sall.extend(s)
        s = ("\n").join(sall)
        f.write(s)
        f.close()

    def writeCentroids(self):
        filePrefix =self.options["gis"]["gis"][0]
        fo = os.path.join(self.directory,filePrefix+".cnt")
        f = open(fo,"w")
        c = self.centroids
        keys = c.keys()
        keys.sort()
        csCount = {}
        sall=[]
        for key in keys:
            x,y = c[key]
            sout = "%d\t%12.8f\t%12.8f"%(key,x,y)
            sall.append(sout)
        s = ("\n").join(sall)
        f.write(s)
        f.close()

    def summarizeOptions(self):
        skeys= self.options.keys()
        for sectionKey in skeys:
            section = self.options[sectionKey]
       #     print section
            optionKeys = section.keys() 
            for optionKey in optionKeys:
                values = section[optionKey]
       #         print section,optionKey,values
        
    def writeData(self,fileName):
        fo = open(fileName,'w')
        db = self.dataBase
        variableNames = db.variables.keys()
        nVar = len(variableNames)
        varString = (" ").join(variableNames)
        so = "%d %s\n"%(nVar,varString)
        fo.write(so)
        for variable in variableNames:
            var = db.getVariable(variable)
            so = "%s %s\n"%(var.name,var.varType)
            fo.write(so)
            varType = var.varType.upper()
            if varType == "CSTS":
                n = var.n
                for i in range(n):
                    rowi = var[i,:]
                    rowi = rowi.tolist()
                    s = [ "%-.3f"%x for x in rowi]
                    s = (" ").join(s)
                    fo.write(s+"\n")
            elif varType == "TSCS":
                t = var.t
                for i in range(t):
                    rowi = var[i,:]
                    rowi = rowi.tolist()
                    s = [ "%-.3f"%x for x in rowi]
                    s = (" ").join(s)
                    fo.write(s+"\n")
            elif varType == "CS":
                rowi = var[:,0]
                rowi = rowi.tolist()
                s = [ "%-.3f"%x for x in rowi]
                s = (" ").join(s)
                fo.write(s+"\n")
            else:
                print var
                print shape(var)
                rowi = var[:,0]
                rowi = rowi.tolist()
                s = [ "%-.3f"%x for x in rowi]
                s = (" ").join(s)
                fo.write(s+"\n")

        fo.close()
    
    def writeDataHeader(self,fileName):
        fo = open(fileName,'w')
        db = self.dataBase
        timeFreq = self.timeFreq
        so = timeFreq+" "+str(self.timeInfo[1])+" "+str(self.timeInfo[2])
        so = so+"\n"
        so = so +"csnames"+"\n"
        fo.write(so)
        so = ("\n").join(self.regionNames)
        fo.write(so)
        fo.close()

    def ReadData(self,fileName):
       # print fileName
        d = Data.DataReader(fileName)
        t = Data.DataParser(d.Info,self)
        self.regionNames = d.regionNames
        self.regionType = d.regionType
        self.timeInfo = d.timeInfo
        self.timeFreq = d.timeFreq
       # print self.timeFreq
        self.timeClass = d.timeClass
        self.timeString = d.timeString()
        self.timeNumeric = d.timeNumeric()
        self.d = d.Info
        self.setVarStrings()
        self.catalogue()

    def setVarStrings(self):
        db = self.dataBase
        variableNames = db.variables.keys()
        for variableName in variableNames:
            variable = db.getVariable(variableName)
            variable.setTimeString(self.timeString)
            variable.setRegionNames(self.regionNames)

    def ReadGalMatrix(self,fileName):
        #print 'galfilename: ',fileName
        g = Data.GalReader(fileName)
        self.g = g
        self.dataBase.addMatrix(g.w)

    def ReadGisFile(self,fileName):
        gis = open(fileName,'r')
        gisdata = gis.readlines()
        gis.close()
        nl = len(gisdata)
        #print "ReadGisFile",nl,fileName
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
        coords=polyDict
        self.coords = coords
        self.poly2cs = poly2cs
        self.cs2poly = cs2poly

    def __calcCentroids(self):
        #print 'calcCentroids'
        coords = self.coords
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

    def readCentroids(self, fileName):
        f = open(fileName,'r')
        lines = f.readlines()
        self.centroids = {}
        for line in lines:
            key,x,y = line.split()
            key = int(key)
            x=float(x)
            y=float(y)
            self.centroids[key] = [x,y]
        f.close()

    
    def gis2Contiguity(self,coords,poly2cs,cs2poly):
        vert2cs = {} 
        polykeys = coords.keys()
        csids = cs2poly.keys()
        for poly in polykeys:
            vertices = coords[poly]
            n = len(vertices)
            r = range(0,n,2)

            pnts = [ (vertices[i],vertices[i+1])  for i in r]
            csid = poly2cs[poly][0]
            for pnt in pnts:
                if vert2cs.has_key(pnt):
                    if csid not in vert2cs[pnt]:
                        vert2cs[pnt].append(csid)
                else:
                    vert2cs[pnt] = [csid]
        galinfo = {}
        pnts = vert2cs.keys()
        for pnt in pnts:
            ids = vert2cs[pnt]
            nids = len(ids)
            rn = range(nids)
            if nids > 1:
                for i in rn[0:-1]:
                    for j in rn[i:nids]:
                        idi = ids[i]
                        idj = ids[j]
                        if idi != idj:
                            if galinfo.has_key(idi):
                                if idj not in galinfo[idi]:
                                    galinfo[idi].append(idj)
                            else:
                                galinfo[idi]=[idj]
        
                            if galinfo.has_key(idj):
                                if idi not in galinfo[idj]:
                                    galinfo[idj].append(idi)
                            else:
                                galinfo[idj]=[idi]
                
        keys = galinfo.keys()
        islands = [ csid  for csid in csids if csid not in keys]
        if islands:
            print "unconnected observation(s): ",islands
            return 0
        else:
            items = galinfo.items()
            g2 = dict( [(item[0],(len(item[1]),item[1])) for item in items  ] )
            return g2




    def catalogue(self):
        db = self.dataBase
        variableNames = db.variables.keys()
        matrixNames = db.matrices.keys()
        nvar=len(variableNames)
        nmat=len(matrixNames)
        
        so = "PROJECT DATABASE SUMMARY\n"
        so = so +"Time Frequency: "+self.timeFreq
        so = so +"\nTime Span: "+str(self.timeInfo[1])+" "+str(self.timeInfo[2])
        so = so +"\nCross Sectional Units: "+str(len(self.regionNames))
        so=so+"\nProject has %d variables and %d matrices.\n"%(nvar,nmat)
        if nvar:
            so = so+"\n"+"Variable Names: "+"\n\t"
            so = so + " ".join(variableNames)
            so = so + "\n" + db.varTypeSummary()
        if nmat:
            so = so + "\n"+"Matrix Names: "+"\n\t"
            so = so + " ".join(matrixNames)
        try:
            pdirectory = self.directory
            so = so + '\n'+"Project directory: "+pdirectory
        except:
            pass
        return so

    def listRegionNames(self):
        rnames = self.regionNames
        id = range(len(rnames))
        t = zip(id,rnames)
        s = "\n".join(["%d\t%s"%x for x in t])
        s= "\nId\tRegion\n"+s
        return s

    def listTimeIds(self):
        tnames = self.timeString
        id = range(len(tnames))
        t = zip(id,tnames)
        s = "\n".join(["%d\t%s"%x for x in t])
        s= "\nId\tTime\n"+s
        return s

        


    def listVariablesPartial(self):
        db = self.dataBase
        variableNames = db.variables.keys()
        nvar=len(variableNames)
        so="\nProject has %d variables.\n"%nvar
        if nvar:
            so = so+"\n"+"Variable Names: "+"\n\t"
            so = so + " ".join(variableNames)
            so = so + "\n" + db.varTypeSummary()
        return so

    def listVariables(self,varNames=[],maxCol=10,fmt=[8,0]):
        db = self.dataBase
        if varNames==[]:
            varNames =db.variables.keys()
        print varNames
        vtype = {}
        # organize variables by type
        for var in varnames:
            v = db.getVariable(var)
            if vtype.has_key(v.varType):
                vtype[v.varType].append(v)
            else:
                vtype[v.varType]=[v]
        # print variables by type
        so = []
        for varType in vtype.keys():
            vars = vtype[varType]
            if varType=="CSTS":
                t = len(self.timeString)
                rowLabels = self.regionNames
                nr = t/maxCol
                klast = t - nr * maxCol
                nr += 1
                if nr == 1:
                    kwidth = [klast]
                else:
                    kwidth = [maxCol] * (nr  - 1)
                    kwidth.append(klast)
                for var in vars:
                    vname = var.name
                    c1=0
                    for c in kwidth:
                        c2 = c1 + c
                        x = var[:,c1:c2]
                        colLabels = self.timeString[c1:c2]
                        tab = Table(body=x,head=vname,rowNames=rowLabels,colNames=colLabels,fmt=fmt)
                        so.append(tab.table)
                        #so = so+"\n"+tab.table
                        c1 = c2
                #so = "\n".join(so)
            elif varType=="CS":
                n = len(self.regionNames)
                rowLabels = self.regionNames
                t = len(vars) #number of columns
                nr = t/maxCol
                klast = t - nr * maxCol
                nr += 1
                if nr == 1:
                    kwidth = [klast]
                else:
                    kwidth = [maxCol] * (nr - 1)
                    kwidth.append(klast)
                v1=0
                for row in kwidth:
                    v2 = row 
                    print v1,v2
                    x = vars[v1:v2]
                    colLabels = [var.name for var in x]
                    body = transpose(array([var[:,0] for var in x]))
                    print body
                    tab = Table(body,colNames=colLabels,rowNames=rowLabels,fmt=fmt)
                    print tab
                    so.append(tab.table)
                    print "so",so
                    v1 = v2
            else:
                print "not implemented yet"
              
        so ="\n".join(so)
        return so

if __name__ == '__main__':
    from stars import Project
    import sys
    import stars
    import Esda
    import Markov
    import Inequality
    import Mobility
    import Data
    import Markov
    from Table import *
    from SDialog import *
    from numpy.oldnumeric import *


    args = sys.argv
    nargs = len(args)

    if nargs == 1:
        Opening()
    elif nargs == 2:
        t=execfile(args[1])
    else:
        print "Bad command arguments"
