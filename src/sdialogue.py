"""
Dialogue box module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

This is a candidate module for new Dialogues to replace SDialogue.

For now, the idea is to build up complex dialogues by using a container widget
(SDialogue) which then gets ChildWidgets attached to it. These ChildWidgets
can handle different types of user selections (i.e., single entries, paired
list boxes, spinboxes, etc).

Need to add different types of ChildWidgets.

Need to use more color on widgets.

Also need to at a status attribute for the main container widget to determine
if the dialogue was cancelled or not.
"""

import Tkinter as Tk
import tkSimpleDialog
import os
from stars import options
from stars import credits
import version
import time
from ScrolledText import ScrolledText

VERSION = version.VERSION
VERSIONDATE = version.DATE

GIFFILE = os.path.join(options.getSTARSHOME(),"splash.gif")

c1="Copyright (C) 2000-2006, Sergio J. Rey\n"
crnotice1="%sSTARS version %s from %s"%(c1,version.VERSION,version.DATE) 
crnotice2="http://stars-py.sf.net"

STARSHOME=options.getSTARSHOME()
AXISFONTSIZE=str(options.AXISFONTSIZE)
TITLEFONTSIZE=str(options.TITLEFONTSIZE)

def getLicense():
    fileName = os.path.join(STARSHOME,"COPYING")
    f=open(fileName,'r')
    l=f.readlines()
    f.close()
    l="\n".join(l)
    l=l.replace("\n\n","\n")
    return l

def getCredits():
    fileName = os.path.join(STARSHOME,"credits.txt")
    f=open(fileName,'r')
    l=f.readlines()
    f.close()
    l="\n".join(l)
    l=l.replace("\n\n","\n")
    return l



def cleanHelp(helpString):
    try:
        helpList = [ i.strip() for i in helpString.split("\n") ]
        help = "\n".join(helpList)
    except:
        help = helpString
    return help

def zipper(sequence):
    """Given a sequence return a list that has the same length as the original
    sequence, but each element is now a list with an integer and the original
    element of the sequence."""
    n = len(sequence)
    rn = range(n)
    data = zip(rn,sequence)
    return data


class SDialogue:
    """Parent Dialogue TopLevel Widget
    Container for children dialog widgets."""
    def __init__(self,title):
        self.title = title
        # center dialogue
        self.top = Tk.Toplevel()
        self.top.title(title)
        self.children = {}
        self.nChildren = 0
        self.status = 0

    def center(self):
        self.top.update_idletasks()
        xmax = self.top.winfo_screenwidth()
        if xmax > 1280:
            xmax = 1280 # prevent spreading across dual-extended displays
        ymax = self.top.winfo_screenheight()
        xo = (xmax - self.top.winfo_reqwidth()) / 2
        yo = (ymax - self.top.winfo_reqheight()) / 2
        self.top.geometry("+%d+%d" % (xo,yo))


    def addChild(self,widget):
        """add a widget to the container. widgets are gridded from top to
        bottom -- first one at top, second one row two, and so on."""
        self.children[self.nChildren]=widget
        self.nChildren +=1


    def draw(self):
        """show self on screen."""
        buttonFrame = Tk.Frame(self.top)
        ok = Tk.Button(buttonFrame,command=self.onOk,text="OK")
        cancel = Tk.Button(buttonFrame,command=self.onCancel,
                    text="Cancel")
        ok.grid(row=0,column=0)
        cancel.grid(row=0,column=1)
        buttonFrame.grid(sticky="E")
        self.center()
        self.top.grab_set()
        self.top.focus_set()
        self.top.wait_window()


    def onOk(self):
        """handler for clicking ok button"""
        results = {}
        children = self.children.keys()
        for child in children:
            results[child] = self.children[child].retrieve()

        self.results=results
        self.status = 1
        self.quit()
    
    def onCancel(self):
        """handler for clicking cancel button"""
        self.status = 0
        self.quit()

    def quit(self):
        """delete self"""
        self.top.destroy()

    def getResults(self):
        """Accessor for results of all ChildWidgets. 
        Results are stored in a dictionary with keys being the integer value
        for the order in which ChildWidget was added, entry for each key is  a
        sequence container (tuple, list or dictionary) with values for
        that widget."""

        return self.results

    def summarize(self):
        results = self.getResults()
        widgetIds = results.keys()
        widgetIds.sort()
        for widgetId in widgetIds:
            result = results[widgetId]
            s0="Widget %d "% widgetId
            s="%s had the following values specified by the user: "% s0
            print s
            print result



class ChildWidget:
    """Abstract Class for children widgets that build up parent dialogue
    through composition """
    def __init__(self,parent):
        self.parent = parent
        self.parent.addChild(self)
        self.draw()

    def retrieve(self):
        """get user specified values for each option"""
        print "Need to override"


    def draw(self):
        """draw self"""
        self.grid()

    def onHelp(self):
        HelpDialog(self.top,self.helpText,title=self.title)

class Message(ChildWidget):
    """Simple Text Label used as a stub for wizards"""
    def __init__(self, parent, message):
        self.parent = parent
        self.message = message
        ChildWidget.__init__(self, parent)

    def draw(self):
        Tk.Label(self.parent.top, text=self.message).grid()



class SpinEntry(ChildWidget):
    """Spin box entry """
    def __init__(self,parent,label='SpinBox', values=(), align="LEFT",
                 title='SpinBox',helpText=None, default=0):
        """
        parent: container widget
        label: (string) 
        values: (list) values for spinbox
        align: alignment specification
        title: title of widget
        helpText: (string) of specialized help info to be displayed when user
        clicks help.

        default: (int) index of element of spinbox to set.

        """
        self.parent = parent
        self.top = self.parent.top
        self.label = label
        self.align = align.upper()
        self.title = title
        self.helpText = helpText
        self.values = tuple(values)
        ChildWidget.__init__(self,parent)
        self.setDefault(default)

    def retrieve(self):
        self.value = self.sp.get()
        return self.value

    def get(self):
        return  self.value

    def draw(self):
        fr = Tk.LabelFrame(self.parent.top,text=self.title)
        lb = Tk.Label(fr,text=self.label)
        self.sp = Tk.Spinbox(fr, values=self.values, command=self.retrieve)
        lb.grid()
        self.sp.grid(row=0,column=1)
        helpButton=Tk.Button(fr,text="?",command=self.onHelp)
        helpButton.grid(row=0,column=2)
        HELPTXT="""DIALOGUE INSTRUCTIONS
        Click up or down arrows to increase (decrease) values."""
        if self.helpText:
            self.helpText = "SPECIFIC INSTRUCTIONS\n" + self.helpText + "\n" 
            self.helpText += HELPTXT
            self.helpText = cleanHelp(self.helpText)
        else:
            self.helpText = HELPTXT

        fr.grid(sticky="E")

    def setDefault(self,index):
        """Move spinbox to display element at index"""
        for i in range(index):
            self.sp.invoke('buttonup')


            
class UserEntry(ChildWidget):
    """Single entry for user to type a value into."""
    def __init__(self,parent,label='Entry',align="LEFT",title=None,
                 helpText=None, defaultValue=None):
        self.parent = parent
        self.top = self.parent.top
        self.label = label
        self.align = align.upper()
        self.title=title
        self.helpText = helpText
        self.defaultValue = defaultValue
        ChildWidget.__init__(self,parent)

    def retrieve(self):
        result = self.entry.get()
        return result

    def draw(self):
        fr = Tk.LabelFrame(self.parent.top,text=self.title)
        e = Tk.Entry(fr,background="white")
        l = Tk.Label(fr,text=self.label)
        helpButton = Tk.Button(fr,text="?",command=self.onHelp)
        self.entry = e
        if self.defaultValue:
            self.entry.insert(0,str(self.defaultValue))
        l.grid()
        e.grid(row=0,column=1,sticky='E')
        helpButton.grid(row=0,column=2)
        fr.grid(sticky="E")
        HELPTXT="""
        DIALOGUE INSTRUCTIONS 
        This is a user defined entry space.  
        """
        HELP = HELPTXT.split("\n")
        #HELP
        #print HELPTXT.strip()
        if self.helpText:
            self.helpText = "SPECIFIC INSTRUCTIONS\n" + self.helpText + "\n" 
            self.helpText += HELPTXT
            self.helpText = cleanHelp(self.helpText)
        else:
            self.helpText = HELPTXT


    def onHelp(self):
        HelpDialog(self.top,self.helpText,title=self.title)


    def setDefault(self, value):
        self.entry.set(value)

class UserEntries(ChildWidget):
    """ """
    def __init__(self, parent, labels, title='User Entries'):
        self.parent = parent
        self.title = title
        self.labels = labels
        ChildWidget.__init__(self, parent)

    def draw(self):
        fr = Tk.LabelFrame(self.parent.top, text=self.title)
        entries = {}
        i=0
        for label in self.labels:
            l = Tk.Label(fr, text=label) 
            e = Tk.Entry(fr, background='white')
            entries[i] = e
            l.grid(row=i, column=0, sticky='E')
            e.grid(row=i, column=1, sticky='E')
            i += 1
        fr.grid(sticky='E')
        self.entries=entries

    def retrieve(self):
        keys = self.entries.keys()
        keys.sort()
        entries = self.entries
        results = [ entries[key].get() for key in keys]
        return results

    def onHelp(self):
        HelpDialog(self.top,self.helpText,title=self.title)


class ButtonEntryLabel:
    """Wrapper for MultiEntry Button-Entry-Label widgets"""
    def __init__(self,parent,label,listbox,row):
        self.parent = parent
        self.lb = listbox
        buttonP = Tk.Button(parent,text="+",command=self.onSelectP,
                    foreground="blue",activebackground="blue",
                    activeforeground="white")
        buttonM = Tk.Button(parent,text="-",command=self.onSelectM,
                    foreground="red",activebackground="red",
                    activeforeground="white")
        self.entry = Tk.Entry(parent, background="white")
        self.label = Tk.Label(parent,text=label)
        self.buttonP = buttonP
        self.buttonM = buttonM
        self.buttonP.grid(row=row,column=0)
        self.buttonM.grid(row=row,column=1)
        self.entry.grid(row=row,column=2)
        self.label.grid(row=row,column=3)

    def onSelectP(self):
        index=self.lb.index('active')
        value = self.lb.get(index)
        self.entry.insert(Tk.END,value)
    def onSelectM(self):
        self.entry.delete(0,Tk.END)



class MultiEntry(ChildWidget):
    """Left listbox-scrollbar with selections getting sent to one of a number
    of entries on right side"""
    def __init__(self,parent,optionList,selectionEntries,title='MultiEntry',
            helpText=None):
        """
        parent -- application window
        optionList -- list of values to be selected from
        selectionEntries -- list of labels for entries
        """
        self.parent = parent
        self.top = self.parent.top
        self.title=title
        self.helpText = helpText
        self.options = optionList
        self.entryLabels = selectionEntries
        self.helpText=helpText
        ChildWidget.__init__(self,parent)

    def draw(self):
        masterFrame = Tk.LabelFrame(self.top, relief=Tk.RIDGE,borderwidth=2,
                text=self.title)
        frLb = Tk.Frame(masterFrame, relief=Tk.RIDGE,borderwidth = 2)
        self.lb = Tk.Listbox(frLb,height=6,width=16,background="white")
        self.sb = Tk.Scrollbar(frLb,command = self.lb.yview, width=10)
        self.lb.configure(yscrollcommand=self.sb.set)
        self.lb.grid(row=0,column=0)
        self.sb.grid(row=0,column=1)
        self.lb.bind("<Double-Button-1>",self.addSelectionE)
        for option in self.options:
            self.lb.insert(Tk.END,option)

        frE = Tk.Frame(masterFrame, relief=Tk.RIDGE,borderwidth = 2)
        nEntries = len(self.entryLabels)
        N=range(nEntries)
        container = {}
        for i in N:
            label = self.entryLabels[i]
            container[label] = ButtonEntryLabel(frE,label,self.lb,i)
        self.container = container

        frLb.grid(row=0,column=0)
        frE.grid(row=0,column=1,sticky="N")

        bottomFr = Tk.Frame(masterFrame,relief=Tk.RIDGE,borderwidth=2)
        helpB = Tk.Button(bottomFr,text="?",command=self.onHelp)
        helpB.grid(row=0,column=2)
        bottomFr.grid(row=1,column=1,sticky="E")
        HELPTXT="""
DIALOGUE INSTRUCTIONS
To select an item from the list box on the left and to place it in a
particular entry on the right do the following:

    1. Select the item name in the list box by clicking on it with the mouse.
    2. Click the + button to the left of the specific entry you want this item
       for.

To remove a selection from a specific entry, click the - button to its left.
            """
        if self.helpText:
            self.helpText = "SPECIFIC INSTRUCTIONS\n" + self.helpText + "\n" 
            self.helpText += HELPTXT
            self.helpText = cleanHelp(self.helpText)
        else:
            self.helpText = HELPTXT
        self.masterFrame = masterFrame
        self.masterFrame.grid()

    def retrieve(self):
        keys = self.container.keys()
        self.values = {} 
        for key in keys:
            item = self.container[key]
            value = item.entry.get()
            self.values[key] = value

        return self.values

    def onOk(self):
        self.retrieve()
        if self.values:
            self.status = 1
        else:
            self.status = 0
        self.quit()

    def onCancel(self):
        self.status = 0
        self.quit()

    def onHelp(self):
        HelpDialog(self.top,self.helpText,title=self.title)

    def quit(self):
        self.top.destroy()

    def addSelectionE(self,event):
        self.addSelection()

    def addSelection(self):
        index = self.lb.index('active')
        value = self.lb.get(index)
        for key in self.container.keys():
            item = self.container[key]
            item.entry.delete(0,Tk.END)
            value = item.entry.insert(Tk.END,value)





class DualListBoxes(ChildWidget):
    """Left and right listbox-scrollbar pairs. Left is used to select items
    which are sent to right lb-sb pair."""
    def __init__(self,parent,optionList,title=None,helpText=None,
            conditional=None):
        self.parent = parent
        self.top = self.parent.top
        self.optionList = optionList
        self.title=title
        self.helpText = helpText
        self.conditional=conditional
        ChildWidget.__init__(self,parent)

    def draw(self):
        mF=Tk.LabelFrame(self.top,relief=Tk.RIDGE,
                borderwidth=2,text=self.title)
        lFr = Tk.Frame(mF, relief=Tk.RIDGE, borderwidth=2)
        self.leftLb = Tk.Listbox(lFr,height=6,width=16,background="white")
        self.leftSb = Tk.Scrollbar(lFr,command=self.leftLb.yview,width=10)
        self.leftLb.configure(yscrollcommand=self.leftSb.set)
        self.leftLb.grid(column=0)
        self.leftSb.grid(row=0,column=1)
        for item in self.optionList:
            self.leftLb.insert(Tk.END,item)
        self.leftLb.bind("<Double-Button-1>",self.addSelectionE)
        frb = Tk.Frame(mF, relief=Tk.RIDGE, borderwidth=2)
        b1 = Tk.Button(frb,text='+ ',
             command=self.addSelection,foreground="blue")
        b2 = Tk.Button(frb,text='++',command=self.addAll,
             foreground="blue")
        b3 = Tk.Button(frb,text="- ",command=self.removeSelection,
             foreground="red")
        b4 = Tk.Button(frb,text="--",command=self.removeAll,
             foreground="red")
        b1.grid()
        b2.grid()
        b3.grid()
        b4.grid()
        if self.conditional:
            self.cLabel = Tk.Label(lFr,text="Conditional Variable")
            self.cLabel.grid(row=1,column=0)
            self.cButton = Tk.Button(frb,text="+",command=self.onConditional,
                    foreground="blue")
            self.cButton.grid()
        frb.grid(row=0,column=2)
        rFr = Tk.Frame(mF, relief=Tk.RIDGE, borderwidth=2)
        self.rightLb = Tk.Listbox(rFr,height=6,width=16, background="white")
        self.rightSb = Tk.Scrollbar(rFr,command=self.rightLb.yview,width=10)
        self.rightLb.configure(yscrollcommand=self.rightSb.set)
        self.rightLb.grid(row=0,column=3)
        self.rightSb.grid(row=0,column=4)
        self.rightLb.bind("<Double-Button-1>",self.removeSelectionE)
        if self.conditional:
            self.cEntry = Tk.Entry(rFr, background="white")
            self.cEntry.grid(row=1,column=3)
            self.cEntry.bind("<Double-Button-1>",self.condDelete)
        lFr.grid(row=0,column=0)
        frb.grid(row=0,column=1)
        rFr.grid(row=0,column=2)

        bottomFr = Tk.Frame(mF,relief=Tk.RIDGE,borderwidth=2)
        helpB = Tk.Button(bottomFr,text="?",command=self.onHelp)
        helpB.grid()
        bottomFr.grid(column=2,sticky="E")
        HELPTXT="""
DIALOGUE INSTRUCTIONS
A Double-Left-Click on an item in the left list box sends it to
the right listbox. A Double-Left-Click on an item in the right
list box deletes it from the selection set.

The buttons between the two list boxes work as follows:
    +  adds the currently selected item in the left list box to the
       right list box.
    ++ adds all the items from the left list box to the right list
       box.
    -  deletes the currently selected item from the right list
       box.
    -- deletes all items from the right list box.

Clicking OK closes the selection dialogue and saves the
selections.

Clicking Cancel closes the selection dialogue without saving any
selections.
            """


        if self.helpText:
            self.helpText = "SPECIFIC INSTRUCTIONS\n" + self.helpText + "\n" 
            self.helpText += HELPTXT
            self.helpText = cleanHelp(self.helpText)
        else:
            self.helpText = HELPTXT
        mF.grid()



    def addAll(self):
        for item in self.optionList:
            self.rightLb.insert(Tk.END,item)
            self.retrieve()

    def addSelectionE(self,event):
        self.addSelection()

    def addSelection(self):
        index = self.leftLb.index("active")
        value = self.leftLb.get(index)
        self.rightLb.insert(Tk.END,value)
        self.rightLb.see(Tk.END)
        self.retrieve()

    def removeSelectionE(self,event):
        self.removeSelection()

    def removeSelection(self):
        index = self.rightLb.index("active")
        self.rightLb.delete(index)
        self.rightLb.see(Tk.END)
        self.retrieve()

    def removeAll(self):
        self.rightLb.delete(0,Tk.END)
        self.retrieve()


    def setVaues(self):
        """
        update selection set
        """
        self.rightLb.activate(0)
        values =self.rightLb.get(0,Tk.END)
        self.values = values


    def retrieve(self):
        """
        return values to parent 
        """
        self.rightLb.activate(0)
        values =self.rightLb.get(0,Tk.END)
        self.values = values
        if self.conditional:
            cvalue = self.cEntry.get()
            self.values = [ self.values,cvalue]
            
        return self.values

    def getSelections(self):
        """
        Return a list of strings holding names of the selected items 
        """

        if not self.values:
            self.values = self.default
        return self.values

    def onOk(self):
        self.retrieve()
        self.status = 1
        self.quit()
        print self.status
        print self.values

    def onCancel(self):
        self.status = 0
        self.quit()
        print self.status

    def onHelp(self):
        print self.helpText
        HelpDialog(self.top,self.helpText,title=self.title)

    def quit(self):
        self.top.destroy()

    def onConditional(self):
        index = self.leftLb.index("active")
        value = self.leftLb.get(index)
        self.cEntry.insert(Tk.END,value)

    def condDelete(self,event):
        self.cEntry.delete(0,Tk.END)

class RadioButtons(ChildWidget):
    """Mutually exclusive selection from a set"""
    def __init__(self,parent,label='SpinBox', values=(), align="LEFT",
                 title='Radio Buttons',helpText=None):

        self.parent = parent
        self.top = self.parent.top
        self.label = label
        self.align = align.upper()
        self.title = title
        self.helpText = helpText
        self.values = values
        ChildWidget.__init__(self, parent)

    def draw(self):
        self.variable = Tk.IntVar()
        fr = Tk.LabelFrame(self.parent.top, text=self.title)
        var = Tk.IntVar
        n = len(self.values)
        records = zip(range(n), self.values)
        for id, text in records: 
            Tk.Radiobutton(fr, text=text, value=id,
                        variable=self.variable).grid(sticky="W")
        self.variable.set(0)
        helpButton=Tk.Button(fr,text="?",command=self.onHelp)
        helpButton.grid(row=0,column=1)
        HELPTXT="""
Select one of the mutually exclusive options.
"""
        if self.helpText:
            self.helpText = "SPECIFIC INSTRUCTIONS\n" + self.helpText + "\n" 
            self.helpText += HELPTXT
            self.helpText = cleanHelp(self.helpText)
        else:
            self.helpText = HELPTXT


        fr.grid(sticky='W')

    def retrieve(self):
        return self.variable.get()

    def get(self):
        return self.values[self.retrieve()]

class CheckButtons(ChildWidget):
    """Selection from a set"""
    def __init__(self,parent,label='Check Buttons', values=(), align="LEFT",
                 title='Check Buttons',helpText=None, allButton=Tk.TRUE, clearButton=Tk.TRUE,
                 multiView=Tk.TRUE):
        self.parent = parent
        self.top = self.parent.top
        self.label = label
        self.align = align.upper()
        self.title = title
        self.values = values
        self.clearButton = clearButton
        self.allButton = allButton
        buttons = {}
        vars = {}
        if multiView:
            data = zipper(values)
        else:
            data = [(0, values)]
        self.data = data
        self.helpText = helpText
        ChildWidget.__init__(self, parent)

    def draw(self):
        fr = Tk.LabelFrame(self.parent.top, text=self.title)
        vars={}
        buttons={}
        for i,label in self.data:
                    vars[i] = Tk.IntVar()
                    buttons[i] = Tk.Checkbutton(fr, text=label, variable=vars[i])
                    buttons[i].grid(row=0,column=i)
        self.buttons = buttons
        self.vars = vars
        if self.allButton:
            i +=1
            Tk.Button(fr,command=self.selectAll,text="All").grid(row=0,column=i)

        if self.clearButton:
            i +=1
            Tk.Button(fr,command=self.clear,text="None").grid(row=0,column=i)

        helpButton=Tk.Button(fr,text="?",command=self.onHelp)
        helpButton.grid(row=0,column=i+1)

        HELPTXT="""Select any, or all, of the individual buttons.
        To select all the buttons select the All button.
        To clear all slections, select the None button.
        """
        if self.helpText:
            self.helpText = "SPECIFIC INSTRUCTIONS\n" + self.helpText + "\n" 
            self.helpText += HELPTXT
            self.helpText = cleanHelp(self.helpText)
        else:
            self.helpText = HELPTXT


        fr.grid(sticky='W')

    def clear(self):
        for button in self.buttons:
            self.buttons[button].deselect()

    def selectAll(self):
        for button in self.buttons:
            self.buttons[button].select()


    def get(self):
        self.values = []
        for button in self.buttons:
            self.values.append((button,self.vars[button].get()))
        return self.values

    def retrieve(self):
        return self.get()



                



class HelpDialog:
    """Wrapper to allow context sensitive help dialogue to be attached to
    individual dialogue widgets.
    
    This provides for customized help to be prepended to the default help that
    is associated with each dialogue widget."""

    def __init__(self,parent,message,title):
        self.parent = parent
        self.message=message
        self.title="Help: "+title
        top = Tk.Toplevel(self.parent)
        top.title(self.title)
        text = Tk.Text(top,background='WHITE')
        sb = Tk.Scrollbar(top,command=text.yview)
        text.configure(yscrollcommand=sb.set)
        text.insert(Tk.END,self.message)
        text.grid(row=0,column=0)
        sb.grid(row=0,column=1)
        okButton = Tk.Button(top,text="Close Help",command=top.destroy)
        okButton.grid(row=1,column=1)




class aAbout(tkSimpleDialog.Dialog):
    """ The application's about box """
    def __init__(self, master=None):
	    tkSimpleDialog.Dialog.__init__(self, master)
 
    def buttonbox(self):
	# Stolen from tkSimpleDialog.py
        # add standard button box. override if you don't want the
        # standard buttons
        box = Tk.Frame(self)
        w = Tk.Button(box, text="OK", width=10)
        w.pack(side=Tk.RIGHT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        box.pack(side=Tk.BOTTOM,fill=X)

   
    def body(self, master):
        self.resizable(0,0)
        self.catIconImage = Tk.PhotoImage(file=GIFFILE) # statt file=
        self.catIcon = Tk.Label(master, image=self.catIconImage)
        self.catIcon.pack(side=Tk.TOP)
        label = Tk.Label(master, text=crnotice1)
        label.pack(side=Tk.TOP)
        font = "Helvetica "+TITLEFONTSIZE
        label = Tk.Label(master, font=font, text=crnotice2,
                justify=Tk.CENTER)
        label.pack(side=Tk.TOP)
        color = 'green'
        font = "Helvetica "+AXISFONTSIZE
        self.infoText = ScrolledText(master, relief=Tk.FLAT, 
                         padx=3, pady=3,
                         background=color, 
                         #foreground="black",
                         wrap='word',
                         width=60, height=12,
                         font=font)
        self.infoText.pack(expand=0, fill=X, side=Tk.BOTTOM)
        self.infoText.delete('0.0', Tk.END)
        self.infoText.insert('0.0', getLicense())	
        self.infoText.configure(state=Tk.DISABLED)
        self.title("STARS - About")


    def ok(self):
        print 'ok'



class About(tkSimpleDialog.Dialog):
    def body(self, master):
        self.image = Tk.PhotoImage(file=GIFFILE)
        self.icon = Tk.Label(master, image=self.image)
        self.icon.pack(side=Tk.TOP)
        label = Tk.Label(master, text= crnotice1)
        label.pack(side=Tk.TOP)
        font = "Helvetica "+TITLEFONTSIZE
        label = Tk.Label(master, font=font,text= 'License',
                foreground='blue',
                justify=Tk.CENTER)
        label.pack(side=Tk.TOP)
        font = "Helvetica "+AXISFONTSIZE
        self.infoText = ScrolledText(master, relief=Tk.FLAT, 
                         padx=3, pady=3,
                         background='white', 
                         foreground="blue",
                         wrap='word',
                         width=60, height=12,
                         font=font)
        self.infoText.pack(expand=0, fill=Tk.X, side=Tk.BOTTOM)
        self.infoText.delete('0.0', Tk.END)
        self.infoText.insert('0.0', getLicense())	
        self.infoText.configure(state=Tk.DISABLED)

class Credits(tkSimpleDialog.Dialog):
    def body(self, master):
        self.image = Tk.PhotoImage(file=GIFFILE)
        self.icon = Tk.Label(master, image=self.image)
        self.icon.pack(side=Tk.TOP)
        label = Tk.Label(master, text= crnotice1)
        label.pack(side=Tk.TOP)
        font = "Helvetica "+TITLEFONTSIZE
        label = Tk.Label(master, font=font,text= "Credits",
                justify=Tk.CENTER, foreground='blue')
        label.pack(side=Tk.TOP)
        font = "Helvetica "+AXISFONTSIZE
        self.infoText = ScrolledText(master, relief=Tk.FLAT, 
                         padx=3, pady=3,
                         background='white', 
                         foreground="blue",
                         wrap='word',
                         width=70, height=12,
                         font=font,
                         tabs=("4c"))
        self.infoText.pack(expand=0, fill=Tk.X, side=Tk.BOTTOM)
        self.infoText.delete('0.0', Tk.END)
        self.infoText.insert('0.0', getCredits())	
        self.infoText.configure(state=Tk.DISABLED)


class Warning(Tk.Toplevel):
    """Warning for time intensive operation """
    def __init__(self,master,text="Warning!"):
        Tk.Toplevel.__init__(self,master)
        self.master=master
        l=Tk.Label(self,bitmap="hourglass")
        l.pack()
        lt=Tk.Label(self,text=text)
        lt.pack()
        self.center()
        self.master.update()

    def center(self):
        xmax = self.winfo_screenwidth()
        ymax = self.winfo_screenheight()
        xneed = self.winfo_reqwidth()
        yneed = self.winfo_reqheight()
        x0 = (xmax - xneed) / 2
        y0 = (ymax - yneed) / 2
        self.geometry("+%d+%d" % (x0,y0))



if __name__ == '__main__':

    # Demonstration

    root = Tk.Tk()

    # create a dialogue instance to hold our widgets
    dialogue = SDialogue("Example Nested Dialog Widgets")

    # now start filling up the container widget
    # first we do a UserEntry
    UserEntry(dialogue,label="Name")

    # next a MultiEntry
    options = 'var1','var2','var3'
    entries = 'x','y','z'
    # txt is info we want to add to append to the built-in help for a
    # MultiEntry - this is txt is problem domain help, as opposed to how to
    # work the dialgoue (which is the built-in help).
    txt="""
A Conditional Scatter Plot shows two variables in an x-y plot, with individual
observations colored according to the value of the conditional variable. This
allows for an examination of how stable the bi-variate relationship between x
and y is over the range of z values.

"""
    MultiEntry(dialogue,options,entries,title="Conditional Scatter Plot",
            helpText=txt)


    # Another UserEntry
    UserEntry(dialogue,label="Height",title="A Tab Title")


    # How bout a DualListBox
    txt="""
A Parallel Coordinate Plot (PCP) plots a selection of variables on parallel
vertical axes  and connects a given observation across the individual axes
giving a multidimensional view of that observation.

    """
    items=range(20)
    DualListBoxes(dialogue,items,title="PC",helpText=txt,conditional="T")


     # One more Dual ListBox
    txt="""
Select one or more time periods. One graph will be generated for each of the
selected periods."""
    years=range(1969,2001)
    DualListBoxes(dialogue,years,title='Year',helpText=txt)

    # SpinEntry
    values=range(5)
    SpinEntry(dialogue,values=values)
    # now draw the container widget
    title='Input Data Type'
    values = ['ArcView', 'Other']
    RadioButtons(dialogue, values=values, title=title)

    # multiple entries
    labels=[ "Year 1 (yyyy)", "Month 1 (1-12)", "Year 2 (yyyy)", "Month 2 (1-12)"]
    UserEntries(dialogue, labels)
    dialogue.draw()
    
    # once the user clicks ok or cancel, we can process the results
    results = dialogue.getResults()
    print """"The results for each subwidget are placed in a dictonary, with the
    keys representing the order in which the subwidget was attached to the
    master."""
    widgetIds = results.keys()
    widgetIds.sort()
    for widgetId in widgetIds:
        result = results[widgetId]
        print "Widget %d had the following values specified by the user:"%widgetId
        print result
        print "\n"

    root.mainloop()

