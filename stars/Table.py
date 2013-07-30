"""
Preparation of formatted tables for printing to GUI
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006 Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW
"""

from numpy.oldnumeric import *
class Table:
    """Pretty table class for STARS"""
    def __init__(self,body,head=[],rowNames=[],colNames=[],fmt=[[8,3]],rowFmt=[8,3],colFmt=[8,3],origin=""):
        n,k=body.shape
        #print n
        #print body
        if head==[]:
            head="TABLE"

        # format body and find widest entry
        Body = []
        maxWidth=0
        if len(fmt)==1:
            fmt=fmt*k
            
        for i in range(n):
            row = []
            for j in range(k):
                val = body[i,j]
                valString = self.format(fmt[j],val)
                lenValString = len(valString)
                if lenValString > maxWidth:
                    maxWidth = lenValString
                row.append(valString)
            Body.append(row)
        self.body = Body
        self.maxBody = maxWidth

        # format column headers
        if colNames==[]:
            colNames = [str(x) for x in range(1,k+1)]
        strings = [x for x in colNames if type(x)==type("s")]
        if strings:
            colLabels = [ "%s"%(x) for x in strings]
        else:
            colLabels = [ self.format(colFmt,x) for x in colNames]
        self.colLabels = colLabels
        colWidth = 0
        for i in range(len(colLabels)):
            coliWidth = len(colLabels[i])
            if coliWidth > colWidth:
                colWidth = coliWidth
        self.colWidth = colWidth

        if self.colWidth > self.maxBody:
            for i in range(len(Body)):
                row = Body[i]
                row = [ self.pad(self.colWidth,x) for x in row]
                Body[i] = row
            colLabels = [self.pad(self.colWidth,x) for x in colLabels]
            self.colLabels = colLabels
            self.body = Body

        else:
            colLabels = [self.pad(self.maxBody,x) for x in self.colLabels]
            self.colLabels = colLabels

        if origin:
            originWidth = len(origin)
            self.origin = origin
        else:
            originWidth = 0
            origin = ""

        # format row headers
        if rowNames==[]:
            rowNames = [str(x) for x in range(1,n+1)]
        strings = [x for x in rowNames if type(x)==type("s")]
        if strings:
            rowLabels = [ "%s"%(x) for x in strings]
        else:
            rowLabels = [ self.format(rowFmt,x) for x in rowNames]
        self.rowLabels = rowLabels
        rowWidth = 0
        for i in range(len(rowLabels)):
            rowiWidth = len(rowLabels[i])
            if rowiWidth > rowWidth:
                rowWidth = rowiWidth

        rowLabels = [ self.pad(rowWidth,x) for x in rowLabels]
        self.rowWidth = rowWidth



        if originWidth > rowWidth:
            rowLabels = [ self.pad(originWidth,x) for x in rowLabels]
        else:
            self.origin = self.pad(rowWidth,origin)

        self.rowLabels = rowLabels


        top = [self.origin]
        top.extend(self.colLabels)
        self.top = " ".join(top)
        rows = []
        for i in range(n):
            #print i
            row = [self.rowLabels[i]]
            row.extend(self.body[i])
            rows.append(" ".join(row))
        self.rows = rows
        table = self.top+"\n"+"\n".join(rows)
        self.table = head+"\n"+table


    def format(self,fmt1,value):
        size = fmt1[0]
        decimal = fmt1[1]
        sv = str(value)
        com = "\"%"+str(size)+"."+str(decimal)+"f\"%("+sv+")"
        sv = eval(com)
        return(sv)

    def pad(self,width,string2pad):
        com = "\"%"+str(width)+"s\"%(string2pad)"
        sv = eval(com)
        return sv

if __name__ == '__main__':
    from numpy.oldnumeric import *
    x = reshape(arrayrange(20)*1.,[4,5])
    tab = Table(x,fmt=[[4,2]])
    t=tab.body
    print t

    t2 = Table(x,fmt=[[8,3]],colNames=["a","b","c","d","e"])
    print t2.body

    t3 = Table(x,fmt=[[8,3]],colNames=range(5))

    s="ONE LONG COL"
    t4 = Table(x,fmt=[[8,4],[8,0],[8,3],[8,1],[8,2]],colNames = [s]*5)

    t5 = ["Rank changes","short one","b","c","d"]
    t5 = Table(x,fmt=[[8,4],[8,0],[8,3],[8,1],[8,2]],colNames = t5)

        




