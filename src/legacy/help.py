"""
help module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

help classes for STARS.


"""
from Tkinter import *
from ScrolledText import ScrolledText

BGCOLOR="white"
FGCOLOR="black"
hfg="blue"

class MyThing (Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.textBox = ScrolledText(self, height=30, width=85)
        self.textBox.pack()
        self.addText()

    def leftMouseClick(self,event):
        print "got a click"
        mouseIndex =  "@%d,%d" % (event.x, event.y)
        current = self.textBox.index(mouseIndex)
        row = current.split(".")[0] + ".0"
        rowFl = float(row)+1.0
        row = str(rowFl)
        target = self.rowIndex[row]
        target = float(target)+12.0
        target = str(target)
        print "moving to target",target
        self.textBox.see(target)

    def rightMouseClick(self,event):
        self.textBox.see("0.0")



    def addText(self):
        f=open("help.txt",'r')
        lines = f.readlines()
        f.close()
        flag = 1
        i=0
        sectionOrder = {}
        sectionHeads = {}
        outlines = {} 
        targetId = 0
        defaultTarget = ""
        tocEntries = []
        lineId=0
        for line in lines:
            if line[0:1] =="#":
                tocEntries.append(line)
                if flag:
                    top = lineId
                    flag = 0
            lineId+=1



        self.tocEntries = tocEntries
        # header text
        header = lines[0:top]

        for line in header:
            hid=self.textBox.insert(END,line,"header")
            self.textBox.tag_config("header",foreground=FGCOLOR)
            self.textBox.tag_config("header",background=BGCOLOR)

        

        self.textBox.insert(END,"Table of Contents\n","toc")
        self.textBox.tag_config("toc",foreground="red")
        self.textBox.tag_config("toc",background=BGCOLOR)
        self.textBox.insert(END,
            "(Left-click entry to navigate, right-click to return)\n\n","directions")
        self.textBox.tag_config("directions",background=BGCOLOR)
        self.textBox.tag_config("directions",foreground="purple")



        sectionDict = {}
        rowIndex = {}
        for tocEntry in tocEntries:
            if tocEntry[0:2] == "##":
                line = "\t"+tocEntry[2:]
            else:
                line = tocEntry[1:]
            rowPosition = self.textBox.index(END).split(".")[0] + ".0"
            rowIndex[rowPosition] = "0.0"
            sectionDict[tocEntry] = rowPosition
            self.textBox.insert(END,line,"tocEntry")

        self.textBox.tag_bind("tocEntry",'<ButtonRelease-1>',
                               self.leftMouseClick)
        self.textBox.tag_config("tocEntry",background=BGCOLOR)
        self.textBox.tag_config("tocEntry",foreground=hfg)
        for i in range(50):
            self.textBox.insert(END,"\n","regular")

        lines = lines[top:]
        for line in lines:
            if sectionDict.has_key(line):
                print "section id",line
                position = self.textBox.index(END)
                tocPosition = sectionDict[line]
                rowIndex[tocPosition] = position
                line = line.replace("#","")

            self.textBox.insert(END,line,"regular")

        self.rowIndex = rowIndex

        self.sectionDict = sectionDict

        self.textBox.see("0.0")

        self.textBox.bind_all('<ButtonRelease-3>',
                              self.rightMouseClick)
        self.textBox.tag_config("regular",background=BGCOLOR)
        self.textBox.tag_config("regular",foreground="black")

def main(master):
    root = Toplevel(master)
    mything = MyThing(root)
    #mything.mainloop()
    root.title = "STARS Help"
    return mything

if __name__ == '__main__':
    from help import *
    master = Tk()
    test=main(master)
    test.mainloop()


