"""
Matrix/Variable manager classes
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@sourceforge.net
----------------------------------------------------------------------

OVERVIEW
"""


from Errors import *

class Database:
    """Container class for a STARS project."""
    def __init__(self):
        self.variables = {}
        self.matrices = {}
        self.varTypes = {}

    def addMatrix(self,matrix):
        self.matrices[matrix.name] = matrix

    def deleteMatrix(self,matrix):
        del(self.matrices[matrix.name])

    def addVariable(self,variable):
        self.variables[variable.name] = variable
        varType = variable.varType
        if self.varTypes.has_key(varType):
            vnames = self.varTypes[varType]
            if vnames.count(variable.name) == 0:
                self.varTypes[varType].append(variable.name)
        else:
            self.varTypes[varType] = [variable.name]

    def deleteVariable(self,variable):
        variables = [ x for x in self.variables.items() if x[0] != \
            variable.name]
        self.variablesTemp = dict(variables)
        self.varTypes.clear()
        self.variables.clear()
        vars = self.variablesTemp.items()
        for var in vars:
            self.addVariable(var[1])
 
       

    def getMatrix(self,matrixName):
        try:
            return self.matrices[matrixName]
        except:
            mesg="Undefined Matrix: %s"%matrixName
            Error(mesg)
            return 0
    def getVariable(self,variableName):
        try:
            return self.variables[variableName]
        except:
            mesg="Undefined Variable: %s"%variableName
            Error(mesg)
            return 0

    def getVariableNames(self):
        return self.variables.keys()

    def getMatrixNames(self):
        return self.matrices.keys()

    def varTypeSummary(self):
        varTypes = self.varTypes.keys()
        so = "Variable Classifications\n"
        for varType in varTypes:
            vars = self.varTypes[varType]
            nv = len(vars)
            vars = " ".join(vars)
            so = so + "Type: "+varType
            so = so + "\nNumber: "+str(nv)
            so = so + "\n\t"+vars+"\n"
        return so

    def getVariableTypeNames(self,typeCode):
        try:
            variableNames = self.varTypes[typeCode]
        except:
            variableNames = []
        return variableNames

    def getCSTSVariableNames(self):
        return self.getVariableTypeNames('CSTS')

    def getTSVariableNames(self):
        return self.getVariableTypeNames('TS')

    def getCSVariableNames(self):
        return self.getVariableTypeNames('CS')


    def listItems(self):
        variableNames = self.variables.keys()
        matrixNames = self.matrices.keys()
        nvar=len(variableNames)
        nmat=len(matrixNames)
        so="Project has %d variables and %d matrices.\n"%(nvar,nmat)
        if nvar:
            so = "Time Frequency: "+self.timeFreq
            so = so+"\n"+"Variable Names: "+"\n\t"
            so = so + " ".join(variableNames)
            so = so + "\n" + self.varTypeSummary()
        if nmat:
            so = so + "\n"+"Matrix Names: "+"\n\t"
            so = so + " ".join(matrixNames)
        return so


