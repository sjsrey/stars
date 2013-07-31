"""
Mixin class to build app level interface

----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
        
----------------------------------------------------------------------

OVERVIEW

An extended Frame that makes window menus and tool-bars automatically.
Use GuiMakerFrameMenu for embedded components (makes frame-based menus).
Use GuiMakerWindowMenu for top-level windows (makes Tk8.0 window menus).
Borrowed from Programming Python

"""

import sys
from Tkinter import *                     # widget classes
from types   import *                     # type constants

class GuiMaker(Frame):
    menuBar    = []                       # class defaults
    toolBar    = []                       # change per instance in subclasses
    helpButton = 0                        # set these in start() if need self

    def __init__(self, parent=None):
        Frame.__init__(self, parent) 
        self.pack(expand=YES, fill=BOTH)        # make frame stretchable
        self.start()                            # for subclass: set menu/toolBar
        self.makeMenuBar()                      # done here: build menu-bar
        self.makeToolBar()                      # done here: build tool-bar
        self.makeWidgets()                      # for subclass: add middle part
        self.setMenuState()

    def setMenuState(self):
        pass
        # override in subclass

    def makeMenuBar(self):
        """
        make menu bar at the top (Tk8.0 menus below)
        expand=no, fill=x so same width on resize
        """
        menubar = Frame(self, relief=RAISED, bd=2)
        menubar.pack(side=TOP, fill=X)
        self.menus = []

        for (name, key, items) in self.menuBar:
            mbutton  = Menubutton(menubar, text=name, underline=key)
            mbutton.pack(side=LEFT)
            pulldown = Menu(mbutton)
            self.addMenuItems(pulldown, items)
            mbutton.config(menu=pulldown)
            self.menus.append(mbutton)

        if self.helpButton: 
            Button(menubar, text    = 'Help', 
                            cursor  = 'gumby', 
                            underline = 0,
                            relief  = FLAT, 
                            command = self.help).pack(side=RIGHT)

    def addMenuItems(self, menu, items):
        for item in items:                     # scan nested items list
            if item == 'separator':            # string: add separator
                menu.add_separator({})
            elif type(item) == ListType:       # list: disabled item list
                for num in item:
                    menu.entryconfig(num, state=DISABLED)
            elif type(item[2]) != ListType:
                menu.add_command(label     = item[0],         # command: 
                                 underline = item[1],         # add command
                                 command   = item[2])         # cmd=callable
            else:
                pullover = Menu(menu)
                self.addMenuItems(pullover, item[2])          # sublist:
                menu.add_cascade(label     = item[0],         # make submenu
                                 underline = item[1],         # add cascade
                                 menu      = pullover) 

    def makeToolBar(self):
        """
        make button bar at bottom, if any
        expand=no, fill=x so same width on resize
        """
        if self.toolBar:
            toolbar = Frame(self, cursor='hand2', relief=SUNKEN, bd=2)
            toolbar.pack(side=BOTTOM, fill=X)
            for (name, action, where) in self.toolBar: 
                Button(toolbar, text=name, command=action).pack(where)

    def makeWidgets(self):
        """
        make 'middle' part last, so menu/toolbar 
        is always on top/bottom and clipped last;
        override this default, pack middle any side;
        for grid: grid middle part in a packed frame  
        """
        #self.commandVar = StringVar()
        #self.Commander = Entry(self,textvariable=self.commandVar,width=40,relief=SUNKEN,bg='white')
        #self.Commander.pack(expand=NO,fill=BOTH,side=TOP)
        self.Editor  =Text(self, 
                     width=40, height=10,
                     relief=SUNKEN, bg='white',   
                   # text   = self.__class__.__name__, 
                   #  text = "BUGGER",
                     cursor = 'crosshair')
        self.Scroll = Scrollbar(self,command=self.Editor.yview)
        self.Editor.configure(yscrollcommand=self.Scroll.set) 
        self.Editor.pack(expand=YES, fill=BOTH, side=LEFT)
        self.Scroll.pack(side=RIGHT, fill=Y)
        self.Editor.insert(END,">")
        #self.Commander.insert(0,"Enter command here.")
        #self.Commander.bind('<Return>',self.getCommand)
    def report(self,message):
        """enters messages into main application window. use for
        entering results, commands called by gui, etc."""
        self.Editor.insert(END,message)
        t=len(message)
        self.Editor.yview_scroll(t,UNITS)
        self.Editor.insert(END,"\n>")
    def getCommand(self,event):
        var = self.Commander.get()
        self.parseCommand(var)
    def setCommand(self,commandString):
        self.Commander.insert(0,commandString)

    def help(self):
        """
        override me in subclass
        """
        from tkMessageBox import showinfo
        showinfo('Help', 'Sorry, no help for ' + self.__class__.__name__)

    def start(self): pass  # override me in subclass


###############################################################################
# For Tk 8.0 main window menubar, instead of a frame
###############################################################################

GuiMakerFrameMenu = GuiMaker           # use this for embedded component menus

class GuiMakerWindowMenu(GuiMaker):    # use this for top-level window menus
    def makeMenuBar(self):
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        for (name, key, items) in self.menuBar:
            pulldown = Menu(menubar)
            self.addMenuItems(pulldown, items)
            menubar.add_cascade(label=name, underline=key, menu=pulldown)

        if self.helpButton: 
            if sys.platform[:3] == 'win':
                menubar.add_command(label='Help', command=self.help)
            else:
                pulldown = Menu(menubar)  # linux needs real pulldown
                pulldown.add_command(label='About', command=self.help)
                menubar.add_cascade(label='Help', menu=pulldown)


###############################################################################
# Self test when file run stand-alone: 'python guimaker.py'
###############################################################################

if __name__ == '__main__':
    from guimixin import GuiMixin            # mixin a help method

    menuBar = [ 
        ('File', 0,  
            [('Open',  0, lambda:0),         # lambda:0 is a no-op
             ('Quit',  0, sys.exit)]),       # use sys, no self here
        ('Edit', 0,
            [('Cut',   0, lambda:0),
             ('Paste', 0, lambda:0)]) ]
    toolBar = [('Quit', sys.exit, {'side': LEFT})]

    class TestAppFrameMenu(GuiMixin, GuiMakerFrameMenu):
        def start(self):
            self.menuBar = menuBar
            self.toolBar = toolBar
    class TestAppWindowMenu(GuiMixin, GuiMakerWindowMenu):
        def start(self):
            self.menuBar = menuBar
            self.toolBar = toolBar
    class TestAppWindowMenuBasic(GuiMakerWindowMenu):
        def start(self):
            self.menuBar = menuBar
            self.toolBar = toolBar    # guimaker help, not guimixin

    root = Tk()
    TestAppFrameMenu(Toplevel())
    TestAppWindowMenu(Toplevel())
    TestAppWindowMenuBasic(root)
    root.mainloop()
