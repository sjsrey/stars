"""
Standalone Utility for conversion of ArcView files to STARS project.
----------------------------------------------------------------------
AUTHOR(S):  Mark V. Janikas janikas@users.sourceforge.net
            Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------

"""

from guimixin import *        
from guimaker import *  
import os
import sys
import string
from math import *
import sdialogue as sd
#from Common import Options
from ProjectWorker import *
from DataViewer import MixedDataTable
import Matcher as MATCH
import Tkinter as tk

class SProjectMaker(GuiMixin, GuiMaker):   # or GuiMakerFrameMenu
    """Application level GUI Wrapper"""
    
    def start(self):
        self.hellos = 0
        self.master.title("SPM: STARS Project Maker")
        self.master.iconname("SPM")
        h = self.winfo_screenheight()
        self.screenHeight = h
        w = self.winfo_screenwidth()
        self.screenWidth = w
        if w > 1280:
            w = 1280
        windowWidth = w/2.
        windowHeight = h/2.
        x0 = int((w - windowWidth) / 2.)
        y0 = int((h - windowHeight) / 2.)
        geom = "%dx%d+%d+%d"%(windowWidth,windowHeight,0,0)
        print geom
        self.master.geometry(geom)
        self.root = self.master
        self.project = None
        self.starsProjectOn = 0
        self.projectedCoordsOn = 0

        self.menuBar = [ 
        
          ('File', 0,                                  
                [ 
                 ('Create New STARS Project',0,self.createNewSTARSProject),
                 ('Open STARS Project',0,self.openSTARSProject),
                 'separator',
                 ('Save STARS Project',0,self.saveProject),
                 ('Save As STARS Project',2,self.saveAsProject),
                 ('Write Cross-Section Names',0,self.writeCSO),
                 #('Write Project Files',2,self.writeProjectFiles),
                 'separator',
                 ('Exit', 1, self.quit) 
                ] 
           ),
          
          ('Data',0,
               [ ('Variable',0,
               [
                 ('Convert',0,
                     [ 
                     ('Base Data to CS',0,self.convertCSVariables),
                     ('Base Data to CSTS',0,self.convertCSTSVariable), 
                     ('Base Data to CSTS (Batch)',0,self.convertCSTSVariableBatch), 
                     ('Cross-Section to Panel',0,self.cs2Panel),
                     ('Panel to Cross-Section',0,self.panel2CS) 
                     ]
                  ),
                 ('Merge',0,
                     [
                     ('CS Data',0,self.readCSV_CS),
                     ('TS Data',0,self.readCSV_TS),
                     ('CSTS Data',0,self.readCSV_CSTS)
                     ]
                  ),
                 ('Join',0,
                     [
                     ('CS Data',0,self.joinCS),
                     ('CSTS Data',0,self.joinCSTS)
                     ]
                  ),
               ] 
               ),
                 'separator',
                 ('Matrix',0,
               [
                 ('Import GAL Binary',0,self.importGalBinary),
                 ('Create GAL Binary from Shapefile',0,self.createGalAppend),
                 #('Import GAL Valued',0,self.importGalValued),
                 #('Import Full',0,self.importFullMatrix)
               ]
                  ), ]
           ),

          ('Tables',0,
                [
                 ('Specific Variable(s)',0,self.variableSpecificTable),
                 ('CS Variables',0,self.variableCSTable),
                 ('TS Variables',0,self.variableTSTable),
                 ('CSTS Variables',0,self.variableCSTSTable),
                 ('CS and CSTS Variables',0,self.variableCS_CSTSTable),
                 ('Base Data Variables',0,self.baseVariableTable) ]
           ),

          ('Plot',0,
               [('Plot Map',0,self.doMaps)])]


    def createNewSTARSProject(self):
        """
        Creates a new STARS project.
        Callback.
        """
        d = sd.SDialogue('Create New STARS Project')
        values='ArcView', 'CSV'
        txt="Choose the type of file you want to use as your base data.\n"
        rbutton = sd.RadioButtons(d, label='Base Data', values=values,
                align='LEFT', title='Types', helpText=txt)
        d.draw()
        if d.status:
            type = d.results[0]
            if type == 0:
                fileType = "*.dbf"
            else:
                fileType = "*.csv"
            FILE_TYPES=[("Files",fileType)]
            baseFileName = askopenfilename(filetypes=FILE_TYPES, title="Choose Base Data File.")
            if baseFileName:
                self.prj = 0
                type = baseFileName.split(".")[-1]
                if type == "dbf":
                    arc = 1
                    self.report("Base data generated from an ArcView Project")
                else:
                    arc = 0
                    self.report("Base data generated from a Comma Delimited File")
                self.proj = ProjectMaker(baseFileName,arc=arc)
            d = sd.SDialogue('Create STARS Project Name')
            txt = """Choose a name for the STARS project you want to create."""
            sd.UserEntry(d,label="Project Prefix", 
                     align="LEFT", title="",helpText=txt)
            d.draw()
            if d.status:        
                self.proj.changeProjPrefix(d.results[0])
            self.baseVariableTable()
            
            d = sd.SDialogue('Choose Time Series Type')
            values='Decadal', 'Annual', 'Quarterly', 'Monthly', 'Irregular'
            txt="Choose the type of file you want to use as your base data.\n"
            rbutton = sd.RadioButtons(d, label='Time-Series', values=values,
                    align='LEFT', title='Types', helpText=txt)
            d.draw()
            if d.status:
                type = d.results[0]
                self.evalTimeInfo(values[type])

            self.createIdsAndNames()
            if arc == 1:
                self.createGal()
            self.starsProjectOn = 1


    def openSTARSProject(self):
        """
        Open an Existing STARS Project.
        Callback.
        """

        fileName = askopenfilename(filetypes=[('Project Files',"*.prj")], 
            title="Open STARS project.")
        if fileName:
            self.prj = 1
            self.proj = ProjectMaker(fileName,prj=1)
            print self.proj.stars.catalogue()
            timeType =  self.proj.stars.timeFreq
            start = self.proj.stars.timeInfo[1]
            end = self.proj.stars.timeInfo[2]
            within = ['MONTHLY', 'QUARTERLY']
            if timeType in within:
                s = start.split("/")
                startYear = s[-1]
                startSub = s[0]
                e = end.split("/")
                endYear = e[-1]
                endSub = e[0]
                if timeType == "MONTHLY":
                    self.proj.createMonthly(startM, startYear, endM, endYear)
                
            varNames = self.proj.stars.getVariableNames()
            d = {}
            for var in varNames:
                v = self.proj.stars.dataBase.getVariable(var)
                type = v.varType
            self.starsProjectOn = 1
            self.projectedCoordsOn = 1
            self.report(self.proj.projectSummary())

    def writeCSO(self):
        try:
            self.proj.writeCSO()
        except:
            self.report("""Could not export region names.  Perhaps they have not
            been identified yet.""")
    
    def evalTimeInfo(self,type):
        tDict = {'Decadal':self.createDECADAL, 
                 'Annual':self.createANNUAL, 
                 'Quarterly':self.createQUARTERLY, 
                 'Monthly':self.createMONTHLY,
                 'Irregular':self.createIRREGULAR}
        tDict[type]()
            
    def createDECADAL(self):
        d = sd.SDialogue('Decadal Time-Series Dialogue')
        txt = "Choose the start year for your project."
        sd.UserEntry(d,label="Start Year", align="LEFT", title="",helpText=txt)
        txt = "Choose the end year for your project."
        sd.UserEntry(d,label="End Year", align="LEFT", title="",helpText=txt)
        d.draw()
        if d.status:
            start = d.results[0]
            end = d.results[1]
            self.proj.createDecadal(start, end)
            self.report(self.proj.timeSummary)

    def createANNUAL(self):
        d = sd.SDialogue('Annual Time-Series Dialogue')
        txt = "Choose the start year for your project."
        sd.UserEntry(d,label="Start Year", align="LEFT", title="",helpText=txt)
        txt = "Choose the end year for your project."
        sd.UserEntry(d,label="End Year", align="LEFT", title="",helpText=txt)
        d.draw()
        if d.status:
            start = d.results[0]
            end = d.results[1]
            self.proj.createAnnual(start, end)
            self.report(self.proj.timeSummary)

    def createQUARTERLY(self):
        d = sd.SDialogue('Quarterly Time-Series Dialogue')
        txt = "Choose the starting quarter for your project."
        quarters = range(1,5)
        entries = ['Start Quarter']
        sd.MultiEntry(d,quarters, entries, title='',
                      helpText=txt)          
        txt = "Choose the start year for your project."
        sd.UserEntry(d,label="Start Year", align="LEFT", title="",helpText=txt)      
        txt = "Choose the ending quarter for your project."
        entries = ['End Quarter']
        sd.MultiEntry(d,quarters, entries, title='',
                      helpText=txt)             
        txt = "Choose the end year for your project."
        sd.UserEntry(d,label="End Year", align="LEFT", title="",helpText=txt)
        d.draw()
        if d.status:
            startQ = int(d.results[0]['Start Quarter'])
            startYear = int(d.results[1])
            endQ = int(d.results[2]['End Quarter'])
            endYear = int(d.results[3])
            self.proj.createQuarterly(startQ, startYear, endQ, endYear)
            self.report(self.proj.timeSummary)

    def createMONTHLY(self):
        d = sd.SDialogue('Monthly Time-Series Dialogue')
        txt = "Choose the starting month for your project."
        months = range(1,13)
        entries = ['Start Month']
        sd.MultiEntry(d,months, entries, title='',
                      helpText=txt)          
        txt = "Choose the start year for your project."
        sd.UserEntry(d,label="Start Year", align="LEFT", title="",helpText=txt)      
        txt = "Choose the ending month for your project."
        entries = ['End Month']
        sd.MultiEntry(d,months, entries, title='',
                      helpText=txt)             
        txt = "Choose the end year for your project."
        sd.UserEntry(d,label="End Year", align="LEFT", title="",helpText=txt)
        d.draw()
        if d.status:
            startM = int(d.results[0]['Start Month'])
            startYear = int(d.results[1])
            endM = int(d.results[2]['End Month'])
            endYear = int(d.results[3])
            self.proj.createMonthly(startM, startYear, endM, endYear)
            self.report(self.proj.timeSummary)

    def createIRREGULAR(self):
        d = sd.SDialogue('Irregular Time-Series Dialogue')
        txt = "Choose the number of time periods (Integer)"
        sd.UserEntry(d,label="Number of Time Periods (t)", align="LEFT", title="",helpText=txt)
        d.draw()
        if d.status:
            t = int(d.results[0])
            self.proj.createIrregular(t)
            self.report(self.proj.timeSummary)

    def createIdsAndNames(self):
        d = sd.SDialogue('Create Region Names and Ids')
        txt = """You must identify names for the regions in your project.  
        *** All the options in this dialogue are optional.  If you leave them
        blank, your regions will be identified by the integers associated with
        the number of rows in the input .dbf or .csv file.  

        1.  Use the Unique Field to identify unique labels that match the
        number of cross-sections in your study.  Examples would include NUTS
        or FIPS codes.
        2.  If there are no Fields that can be used to determine the
        uniqueness of each cross-section you may combine the values from two
        fields to create region ids.  The Join Field term will be combined
        with the Unique Field to create a "more unique" identifier.  
        3.  Use the Optional Name Field if you have identified regions with
        either the Unique or Joined method, but you want the names of the
        regions to be determined by this field.
        4.  The user can select the type of delimiter used join field entries.
        The default delimiter is an underscore:  field1_field2
        """
        varNames = self.proj.getDBFVariableNames()
        varNames.sort()
        entries = ['Unique Field', 'Join Field', 'Optional Name Field', 'Delimiter']        
        sd.MultiEntry(d,varNames, entries, title='Optional Arguments', helpText=txt)
        d.draw()
        if d.status:
            nameField = d.results[0]['Unique Field']
            if nameField:
                nameField = self.proj.getDBFVariable(nameField)
            else:
                nameField = []
            joinField = d.results[0]['Join Field']
            if joinField:
                joinField = self.proj.getDBFVariable(joinField)
            else:
                joinField = []
            finalField = d.results[0]['Optional Name Field']
            if finalField:
                finalField = self.proj.getDBFVariable(finalField)
            else:
                finalField = []
            delimiter = d.results[0]['Delimiter']
            if delimiter:
                pass
            else:
                delimiter = "_"
            self.proj.createNamesAndIDs(var1=nameField,
                                        var2=joinField,
                                        var3=finalField,
                                        delim=delimiter)
            self.report(self.proj.variableSummary())
        
    def createGalAppend(self):
        if self.proj.arc == 1:
            self.createGal()
        else:
            self.report("""You must be using an arcview type project for this
            option.""")
        
    def createGal(self):
        d = sd.SDialogue('Create Contiguity Matrices')
        txt="""Rook contiguity is based on shared edges, while Queen
        contiguity is based on shared vertices between pairs of polygons."""
        types = "Rook", "Queen"
        sd.CheckButtons(d, title='Criterion', label='Criterion', values=types,
                        helpText=txt)
        d.draw()
        if d.status:
            criterion = d.results[0]
            mats = []
            matNames = []
            self.master.update()
            if criterion[0][1]: # rook
                text="Creating Rook Based Contiguity Weights"
                rd=sd.Warning(self.master,text=text)
                if self.proj.aggOn == 1:
                    mats.append(self.proj.makeGalWeightsAgg())
                else:
                    mats.append(self.proj.makeGalWeights())
                matNames.append('rook')
                rd.destroy()

            if criterion[1][1]: # queen
                txt="Creating Queen Based Contiguity Weights."
                qd=sd.Warning(self.master,txt)
                if self.proj.aggOn == 1:
                    mats.append(self.proj.makeGalWeightsAgg(2))
                else:    
                    mats.append(self.proj.makeGalWeights(2))
                matNames.append('queen')
                qd.destroy()
            for name,stringOut in zip(matNames,mats):
                print 'writing GAL file(s)'
                nameOut = self.proj.projPrefix+"_"+name+".gal"
                nameOut = os.path.join(self.proj.projectDir,nameOut)
                fo=open(nameOut,'w')
                fo.write(stringOut)
                fo.close()
                self.proj.matrices[nameOut]='gal'
                print 'done writing GAL files(s)'
                





    def convertCSVariables(self):
        d = sd.SDialogue('Convert Initial Field(s) to STARS Cross-Sectional Variables(s)')
        varNames = self.proj.getDBFVariableNames()
        varNames.sort()
        txt="""Select one or more initial variables to convert into pure
        cross-sectional STARS variables."""
        sd.DualListBoxes(d,varNames,title='Fields', helpText=txt)
        entries = ['Aggregation Method']
        txt = """If the same cross-sectional unit has more than one value
        associated with it, ProjectMaker will have to combine the values in
        some way.  You have the following options:
            Sum: will sum up any values associated with the same cross-section.
            Max: will take the maximum value of any values associated with the same cross-section.
            Min: will take the minimum value of any values associated with the same cross-section.
            Average: will average the values associated with the same cross-section.
            String: will essentially use the value of the last instance for
            each cross-section.  Furthermore the value is a string.  Use this
            for categorical data.
            
        ***The default method is "Average"."""
        types = ['Sum', 'Max', 'Min', 'Average', 'String']
        sd.MultiEntry(d,types, entries, title='Optional Arguments', helpText=txt)
        d.draw()
        if d.status:
            varList = d.results[0]
            cohesion = d.results[1]['Aggregation Method']
            if cohesion:
                pass
            else:
                cohesion = 'Average'
            createVars = [ self.proj.convertArcViewVariable(cohesion,var,[var]) for var in varList ]
            self.report(self.proj.variableSummary())
            

    def convertCSTSVariable(self):
        d = sd.SDialogue('Convert Initial Fields to a STARS Panel Variables')
        varNames = self.proj.getDBFVariableNames()
        varNames.sort()
        txt="""Select the fields in time order to be create a panel variable."""
        time = str(self.proj.t)
        tRemind = "Choose t = " + time + " fields"
        sd.DualListBoxes(d,varNames,title=tRemind, helpText=txt)
        txt = "Choose a name for your STARS Panel variable."
        sd.UserEntry(d,label="Choose Panel Variable Name", align="LEFT", title="",helpText=txt)
        entries = ['Aggregation Method']
        txt = """If the same cross-sectional unit has more than one value
        associated with it, ProjectMaker will have to combine the values in
        some way.  You have the following options:
            Sum: will sum up any values associated with the same cross-section.
            Max: will take the maximum value of any values associated with the same cross-section.
            Min: will take the minimum value of any values associated with the same cross-section.
            Average: will average the values associated with the same cross-section.
            String: will essentially use the value of the last instance for
            each cross-section.  Furthermore the value is a string.  Use this
            for categorical data.
            
        ***The default method is "Average"."""
        types = ['Sum', 'Max', 'Min', 'Average', 'String']
        sd.MultiEntry(d,types, entries, title='Optional Arguments', helpText=txt)
        d.draw()
        if d.status:
            varList = d.results[0]
            varName = d.results[1]
            cohesion = d.results[2]['Aggregation Method']
            if cohesion:
                pass
            else:
                cohesion = 'Average'
            createVar = self.proj.convertArcViewVariable(cohesion,varName,varList)
            self.report(self.proj.variableSummary())

    def convertCSTSVariableBatch(self):
        d = sd.SDialogue('Convert Initial Fields to a STARS Panel Variables')
        varNames = self.proj.getDBFVariableNames()
        batch = MATCH.batchSplit(varNames)
        varNames = batch['strings']
        varNames.sort()
        timeInfo = batch['ints']
        timeInfo.sort()
        txt="""Select the fields to create panel variables via the batch method."""
        time = str(self.proj.t)
        add = """Remember that field must have " + time + " time periods
        associated with it."""
        txt = txt + "\n" + add
        title = "Choose fields for batch CSTS creation"
        sd.DualListBoxes(d,varNames,title=title, helpText=txt)
        
        txt = """Choose a variable associated with the first time period in
        your study, and an additional oone for the year time period.  You may
        also type this in manuallly."""
        timeStuff = ['Start Period for Batch', 'End Period for Batch']
        sd.MultiEntry(d,timeInfo, timeStuff, title='Time Period Arguments',
                      helpText=txt)
        
        txt="""Provide the time period increment:
            I.e.    Annual:   1
                    BiAnnual: 2
                    Decadal:  10
            """        
        sd.UserEntry(d,label="Integer Value", align="LEFT", 
                     title="User Defined Time Increment",helpText=txt)        
        
        entries = ['Aggregation Method']
        txt = """If the same cross-sectional unit has more than one value
        associated with it, ProjectMaker will have to combine the values in
        some way.  You have the following options:
            Sum: will sum up any values associated with the same cross-section.
            Max: will take the maximum value of any values associated with the same cross-section.
            Min: will take the minimum value of any values associated with the same cross-section.
            Average: will average the values associated with the same cross-section.
            String: will essentially use the value of the last instance for
            each cross-section.  Furthermore the value is a string.  Use this
            for categorical data.
            
        ***The default method is "Average"."""
        types = ['Sum', 'Max', 'Min', 'Average', 'String']
        sd.MultiEntry(d,types, entries, title='Optional Arguments', helpText=txt)
        d.draw()
        if d.status:
            vars = MATCH.Matcher('vars',d.results[0])
            varList = vars.unique
            start = int( d.results[1]['Start Period for Batch'] )
            end = int( d.results[1]['End Period for Batch'] )
            step = int( d.results[2] )
            cohesion = d.results[3]['Aggregation Method']
            if cohesion:
                pass
            else:
                cohesion = 'Average'
            for var in varList:
                try:
                    newVar = [ var+str(i) for i in range(start,end+step,step) ]
                    createVar = self.proj.convertArcViewVariable(cohesion,var,newVar)
                except:
                    beg = "Could not create new variable for " + var + "."
                    end = "\nPerhaps the the time series does not match."
                    self.report(beg+end)            
                    self.report(self.proj.variableSummary())
        
    def cs2Panel(self):
        d = sd.SDialogue('Convert Existing CS Variables to a CSTS Variable')
        varNames = self.proj.getCSVariableNames()
        varNames.sort()
        time = str(self.proj.t)
        txt="""Select the CS variables in temporal order.  Make sure that you
        have the same number of CS vars as time periods"""
        tRemind = "Choose t = " + time + " CS Variables"
        sd.DualListBoxes(d,varNames,title=tRemind, helpText=txt)
        txt = "Choose a name for your STARS Panel variable."
        sd.UserEntry(d,label="Choose Panel Variable Name", align="LEFT", 
                     title="",helpText=txt)
        title='Would you like to delete the original CS Variables?'
        values = ['No', 'Yes']
        txt = """If you select Yes, then the original CS variables will be erased.  ***The default is No"""
        sd.RadioButtons(d, values=values, title=title,helpText=txt)
        d.draw()
        if d.status:
            varList = d.results[0]
            panelName = d.results[1]
            delete = d.results[2]
            if len(varList) == self.proj.t:
                self.proj.cs2Panel(varList,panelName,delete=delete)
                self.report(self.proj.variableSummary())
            else:
                s = """ERROR:  The number of CS Variables you provided do not match the number of time periods in your project."""
                self.report(s)

    def panel2CS(self):
        d = sd.SDialogue('Convert Existing Panel Variable to CS Variables')
        varNames = self.proj.getCSTSVariableNames()
        varNames.sort()
        txt="""Choose the name of the Panel variable(s) that you would like to
        decompose by time periods into seperate cross-sectional variables.
        You may choose more than one at a time"""
        sd.DualListBoxes(d,varNames,title='Panel Variables', helpText=txt)
        title='Would you like to delete the original Panel Variables?'
        values = ['No', 'Yes']
        txt = """If you select Yes, then the original Panel variables will be erased.  ***The default is No"""
        sd.RadioButtons(d, values=values, title=title,helpText=txt)
        d.draw()
        if d.status:
            varList = d.results[0]
            delete = d.results[1]
            for var in varList:
                self.proj.panel2CS(var,delete=delete)
            self.report(self.proj.variableSummary())
        
                     
    def variableSpecificTable(self):
        d = sd.SDialogue('View Specific Variable(s)')
        txt = """Choose the name(s) of the CS and CSTS variable(s) you want to
        view in tabular format."""
        cvars = self.proj.getCSVariableNames()
        cstvars = self.proj.getCSTSVariableNames()
        varNames = cvars + cstvars        
        sd.DualListBoxes(d,varNames,title="CS and CSTS Variables", helpText=txt)
        tsVars = self.proj.getTSVariableNames()
        txt = """Choose the name(s) of the TS variable(s) you want to view in
        tabular format.""" 
        sd.DualListBoxes(d,tsVars,title="TS Variables", helpText=txt)
        d.draw()
        if d.status:
            csVars = d.results[0]
            try:
                tab = self.proj.createTableList(csVars)
                names = tab[0]
                vals = tab[1]
                top = Toplevel(self.root)
                table = MixedDataTable(top,vals,
                        name="STARS Variables (CS, CSTS)",
                        columnLabels = names)
            except:
                print "No CS or CSTS Variables identified"
            tsVars = d.results[1]
            try:
                tab = self.proj.createTableList(tsVars)
                names = tab[0]
                vals = tab[1]
                top = Toplevel(self.root)
                table = MixedDataTable(top,vals,
                        name="STARS Variables (TS)",
                        columnLabels = names)
            except:
                print "No TS Variables identified"
            
    def variableCSTable(self):
        vars = self.proj.getCSVariableNames()
        tab = self.proj.createTableList(vars)
        names = tab[0]
        vals = tab[1]
        top = Toplevel(self.root)
        table = MixedDataTable(top,vals,
                               name="STARS Variables (CS)",
                               columnLabels = names)        
        
    def variableCSTSTable(self):
        vars = self.proj.getCSTSVariableNames()
        tab = self.proj.createTableList(vars)
        names = tab[0]
        vals = tab[1]
        top = Toplevel(self.root)
        table = MixedDataTable(top,vals,
                               name="STARS Variables (CSTS)",
                               columnLabels = names)   
        
    def variableTSTable(self):
        vars = self.proj.getTSVariableNames()
        tab = self.proj.createTableList(vars)
        names = tab[0]
        vals = tab[1]
        top = Toplevel(self.root)
        table = MixedDataTable(top,vals,
                               name="STARS Variables (TS)",
                               columnLabels = names)  
        
    def variableCS_CSTSTable(self):
        cvars = self.proj.getCSVariableNames()
        cstvars = self.proj.getCSTSVariableNames()
        vars = cvars + cstvars
        tab = self.proj.createTableList(vars)
        names = tab[0]
        vals = tab[1]
        top = Toplevel(self.root)
        table = MixedDataTable(top,vals,
                               name="STARS Variables (CS and CSTS)",
                               columnLabels = names)  
        
    def baseVariableTable(self,sample=1):
        baseData = self.proj.createInitialTable(sample=sample)
        top = Toplevel(self.root)
        table = MixedDataTable(top,baseData,name="Base Data",
                            columnLabels=self.proj.initial.keys())  

    def readCSV_CS(self):
        FILE_TYPES=[("Files","*.csv")]
        fileName = askopenfilename(filetypes=FILE_TYPES, title="MERGE Additional CS Data.")
        if fileName:        
            self.proj.readCSV_CS(fileName)
            self.report(self.proj.variableSummary())

    def readCSV_TS(self):
        FILE_TYPES=[("Files","*.csv")]
        fileName = askopenfilename(filetypes=FILE_TYPES, title="MERGE Additional TS Data.")
        if fileName:        
            self.proj.readCSV_TS(fileName)
            self.report(self.proj.variableSummary())


    def readCSV_CSTS(self):
        FILE_TYPES=[("Files","*.csv")]
        fileName = askopenfilename(filetypes=FILE_TYPES, title="MERGE Additional CSTS Data.")
        if fileName:        
            self.proj.readCSV_CSTS(fileName)
            self.report(self.proj.variableSummary())

    def joinCS(self):
        FILE_TYPES=[("Files","*.csv")]
        fileName = askopenfilename(filetypes=FILE_TYPES, title="JOIN Additional CS Data.")
        if fileName:        
            self.proj.readJoinCSV(fileName)        
            d = sd.SDialogue('Join Data Dialogue')
            txt = """Identify the existing cross-sectional field in the
            project to serve as the master in the matching process.           
            """
            varNames = self.proj.getCSVariableNames()
            varNames.sort()
            entries = ['Field']        
            sd.MultiEntry(d,varNames, entries, title='Identify Master Field', helpText=txt)
            
            txt = """Identify the field in your new data that will serve as
            the slave in the matching process.           
            """
            varNames = self.proj.data2Join.names
            varNames.sort()
            entries = ['Field']        
            sd.MultiEntry(d,varNames, entries, title='Identify Slave Field', helpText=txt)
            
            d.draw()
            if d.status:
                master = d.results[0]['Field']
                slave = d.results[1]['Field']
                self.proj.joinCS(master,slave)
                self.report(self.proj.variableSummary())

    def joinCSTS(self):
        FILE_TYPES=[("Files","*.csv")]
        fileName = askopenfilename(filetypes=FILE_TYPES, title="JOIN Additional CSTS Data.")
        if fileName:        
            self.proj.readJoinCSV(fileName)        
            d = sd.SDialogue('Join Data Dialogue')
            txt = """Identify the existing cross-sectional field in the
            project to serve as the master in the matching process.           
            """
            varNames = self.proj.getCSVariableNames()
            varNames.sort()
            entries = ['Field']        
            sd.MultiEntry(d,varNames, entries, title='Identify Master Field', helpText=txt)
            
            txt = """Identify the field in your new data that will serve as
            the slave in the matching process.           
            """
            varNames = self.proj.data2Join.names
            varNames.sort()
            entries = ['Field']        
            sd.MultiEntry(d,varNames, entries, title='Identify Slave Field', helpText=txt)
            d.draw()
            if d.status:
                master = d.results[0]['Field']
                slave = d.results[1]['Field']
                self.proj.joinCSTS(master,slave)
                self.report(self.proj.variableSummary())

    def importGalBinary(self):
        FILE_TYPES=[("Files","*.gal")]
        fileName = askopenfilename(filetypes=FILE_TYPES, title="Import Binary Gal File.")
        if fileName:        
            self.proj.importMatrix(fileName,'gal')

    def importGalValued(self):
        FILE_TYPES=[("Files","*.spv")]
        fileName = askopenfilename(filetypes=FILE_TYPES, title="Import Sparse Valued Gal File.")
        if fileName:        
            self.proj.importMatrix(fileName,'spv')
            
    def importFullMatrix(self):
        FILE_TYPES=[("Files","*.fmt")]
        fileName = askopenfilename(filetypes=FILE_TYPES, title="Import Full Matrix File.")
        if fileName:        
            self.proj.importMatrix(fileName,'fmt')
            

    def saveAsProject(self):
        """
        Saves STARS project under a new name.
        Callback.
        Stub XXX.
        """
        if self.saveCheck():
            fileName = asksaveasfilename(filetypes=[("STARS Projects","*.prj")],
                                         title="Save STARS Project Name",
                                         initialdir=self.proj.projectDir,
                                         initialfile=self.proj.projPrefix)
            if fileName:
                    self.proj.setProjectFiles(fileName)
                    self.writeProjectFiles()

    def saveProject(self):
        """
        Saves STARS project under current name.
        Callback.
        Stub XXX.
        """
        if self.saveCheck():
            self.writeProjectFiles()

    def openProject(self):
        """
        Opens an exisiting STARS Project.
        Callback.
        Stub XXX.
        """
        starsFile = askopenfilename(filetypes=[("STARS Projects","*.prj")])
        if starsFile:
            print starsFile
            self.starsFile = starsFile
        

    def plot(self):
        """
        Plots the current ArcView Shapefile scaled for STARS Map.
        Callback.
        """
        self.avproject.draw()
        self.projectedCoordsOn = 1

    def summarize(self):
        """
        Reports on current ArcView Project.
        Callback.
        """
        try:
            self.avproject.summary()
        except:
            print 'No ArcView Project Open'

    def writeProjectFiles(self):
        """Wrapper to write all files necessary for a STARS Project."""
        #if self.saveCheck():
        self.proj.writePRJ()
        if self.prj != 1:
            if self.proj.arc == 1:
                self.proj.writeGIS(self.projected)
        self.proj.writeCSO()
        self.proj.writeDHT(delimiter=" ")
        self.proj.writeDAT(delimiter=" ")
        print "Finished creating project!"
        self.report("Finished creating project!")


    
    def doMaps(self):
        # XXX maybe wrap alternative projected maps in a dictionary so that the
        # final selection of a projection does not require another projection
        # of the coordinates. i.e., if the user firsts looks at mercator, then
        # uprojected, then albers, the last map is albers. but, if the user
        # wants their project to use none or mercator, they would need to
        # reproject it at this point. for now this is in self.projectedMaps
        if self.proj.prj == 1:
            self.report("Your GIS File has already been created!")
        else:
            if self.proj.arc == 1:
                d = sd.SDialogue('Map Views')
                values=('None', 'Mercator', 'Albers', 'Transverse Mercator',
                    'Cylindrical Equidistant')
                txt="Select Map Projection (or none for unprojected)\n"
                rbutton = sd.RadioButtons(d, label='Projection', values=values,
                        align='LEFT', title='Projections', helpText=txt)
                d.draw()
                if d.status:
                    type = d.results[0]
                    projections = {1:Projection.MercatorProj,
                                   2:Projection.AlbersEqualAreaProj,
                                   3:Projection.TransverseMercatorProj,
                                   4:Projection.CylindricalEquidistantProj,
                                   0:"None"}
                    self.proj.createMap(self.proj.shapeFileName, projections[type])
                    top = Toplevel(self.root)
                    self.projected=Projection.MapView(top, self.proj.map)
                    self.projected.plot()
                    top.title(self.proj.map.projectionName)
                    self.proj.projectedMaps[self.proj.map.projectionName] = self.proj.map
                    self.projectedCoordsOn = 1
            else:
                self.report("No Shapefile declared for this project")
    

    def writeGAL(self):
        print 'writing GAL'
        iGal = ReadGisFile(self.filePrefix+".gis")
        mGal = gis2Contiguity(iGal[0], iGal[1], iGal[2])
        gKeys = mGal.keys()
        gKeys.sort()
        fgal = open(self.filePrefix+".gal", "w")
        fgal.write("%s\n"%(len(gKeys)))
        for i in gKeys:
            fgal.write("%s %s\n"%(i, mGal[i][0]))
            try:
                neighs = [ str(i) for i in mGal[i][1] ]
                neighs =  (" ").join(neighs) 
                print neighs
                fgal.write("%s\n"%(neighs))
            except:
                fgal.write("%s\n"%(""))
                print 'attention: island'
        fgal.close()
        
    def saveCheck(self):
        """Wraps all the checks necessary to write a project file"""
        flag = 1
        flag *= self.starsProjectOn
        if self.proj.arc == 1:
            flag *= self.projectedCoordsOn

        if not self.starsProjectOn: print 'No Stars Project Defined.'
        if self.proj.arc == 1:
            if not self.projectedCoordsOn:
                print 'Please plot shapefile before saving project.'
        return flag


    def notDone(self):
        self.report("This method is not done yet!")


if __name__ == '__main__':
    from Tkinter import *
    v = SProjectMaker()
    v.mainloop()
