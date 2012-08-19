""" History.py

 ----------------------------------------------------------------------
 Command history modulefor Space-Time Analysis of # Regional Systems
 ----------------------------------------------------------------------
 AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
 ----------------------------------------------------------------------
 Copyright (c) 2000-2006 Sergio J. Rey
 ======================================================================
 This source code is licensed under the GNU General Public License, 
 Version 2.  See the file COPYING for more details.
 ======================================================================


"""

class CommandHistory:
    """Storage class for command history"""
    def __init__(self,name):
        self.history = {}
        self.cmdCount = 0
        self.name = name

    def addCommand(self,cmdString):
        self.history[self.cmdCount] = cmdString
        self.cmdCount += 1

    def save(self,file=None):
        if file==None:
            file = self.name
        so = ""
        k = self.history.keys()
        k.sort()
        for ck in k:
            cmdid = self.history[ck]
            so = so + "\n"+"%d\t%s"%(ck,cmdid)
        fo = open(file,'w')
        fo.write(so+"\n")
        fo.close()



if __name__ == '__main__':
    p = CommandHistory("test")
    p.addCommand("open project")
    p.addCommand("read Data")
    p.save()
    p.save(file="test1")

