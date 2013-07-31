"""
Spreadsheet like grid for displaying (editing/selecting) arrays.
----------------------------------------------------------------------
AUTHOR(S):  Serge Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW

Implements a grid view that can be used to display an array of values.

Two different classes are available, DataTable is intended for pure Numeric
arrays, while MixedDataTable is for data that has hetergeneous types (strings
and numeric values).

"""


from Tkinter import *
from Utility import format
from numpy.oldnumeric import shape
from types import *

import tkFont



class DataTable:
    """
    Spreadsheet-like grid to display an array of values.

    Each cell has at least three identifiers associated with it. The first is
    the row id, the second a column id , and the third is a row/col string.

    """
    def __init__(self, master, values, name=None, rowLabels=None,
                 columnLabels=None, fmt=[12,8], listener=None,
                 labelFamily="times", labelSize="12", cellFamily="times",
                 cellSize="12"):

        """
        master: top-level container widget
        values: array (Numeric) of values to be displayed. dimension n by k.
        name: string
        rowLabels: length(n) list of strings for row names.
        columnLabels: length(k) list of strings for column names.
        fmt: list of number of places and digits to the right of decimal
        labelFamily: font family for row/col labels
        labelSize: size of font for row/col labels
        cellFamily: font family for grid cells
        cellSize: size of font for grid cells
        
        """
        self.master=master
        self.values=values
        self.name=name
        self.rowLabels=rowLabels
        self.columnLabels=columnLabels
        self.fmt=fmt
        self.labelFamily=labelFamily
        self.labelSize=labelSize
        self.cellFamily=cellFamily
        self.cellSize=cellSize
        self.__highlightColor='yellow'


        if name:
            self.setName(name)

        self.buildGrid()

    def buildGrid(self):
        master = self.master
        values = self.values
        # determine the largest width of a cell
        labelFont = tkFont.Font ( family=self.labelFamily, size=self.labelSize)
        cellFont = tkFont.Font (family=self.cellFamily, size =self.cellSize)
        n,k = shape(values)
        self.n = n
        self.k = k

        # try to speed up value formatting
        ijs = [ (i,j) for i in range(n) for j in range(k) ]
        svalues = [ format(self.fmt, values[i,j]) for i,j in ijs ]
        self.svalues = svalues
        maxv = values.max()
        maxS=format(self.fmt,maxv)
        maxSize = cellFont.measure(maxS)
        height = cellFont.measure('H')
        height = height * 1.6

        rowLabels = self.rowLabels

        if not rowLabels:
            rowLabels = [ str(i) for i in range(n) ]
        rsize = [ labelFont.measure(lab) for lab in rowLabels ]
        maxRL = max(rsize) * 1.10

        columnLabels = self.columnLabels
        if not columnLabels:
            columnLabels = [ str(i) for i in range(k) ]
        maxL = max([ len(label) for label in columnLabels])
        maxCL = labelFont.measure(maxL)

        if maxCL > maxSize:
            maxSize = maxCL


        # determine the size of each cell, the width/height of the canvas and
        # the area we want to display within the scrolling window
        width = 1.20 * maxSize
        canWidth = width * (k+1)
        canHeight = height * (n+1)
        canWidth = canWidth * 1.01



        # build a frame to hold summary information about size of array,
        # current row and column
        frame = Frame(master, bd=2, relief=SUNKEN)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        fLabel = Frame(frame, bd=2, relief=RAISED)
        ltext = "Size: %d rows %d columns"%(n,k)
        label = Label(fLabel,text = ltext,foreground='blue')
        label.grid(row=0,column=0)


        # widget to keep track of which row the mouse is in
        self.rowVariable = StringVar()
        rowCLabel = Label(fLabel,text="Row: ")
        rowCLabel.grid(row=0,column=1)
        rowEntry = Entry(fLabel,background='white',
            textvariable=self.rowVariable)
        rowEntry.grid(row=0,column=2)

        # widget to keep track of which column the mouse is in
        self.colVariable = StringVar()
        colCLabel = Label(fLabel,text="Column: ")
        colCLabel.grid(row=0,column=3)
        colEntry = Entry(fLabel,background='white',
            textvariable=self.colVariable)
        colEntry.grid(row=0,column=4)

        self.valueVariable = StringVar()
        valCLabel = Label(fLabel,text="Value: ")
        valCLabel.grid(row=0,column=5)
        valEntry = Entry(fLabel,background='white',
                textvariable=self.valueVariable)
        valEntry.grid(row=0,column=6)
        fLabel.grid(row=0,column=0)
        



        # build the horizontal and vertical scrollbars as well as the grid
        # itself
        xscrollbar = Scrollbar(frame, orient=HORIZONTAL)
        xscrollbar.grid(row=2, column=0, sticky=E+W)
        yscrollbar = Scrollbar(frame)
        yscrollbar.grid(row=1, column=1, sticky=N+S)

        # determine size of Table to display within scroll area
        screenWidth = master.winfo_screenwidth()
        screenHeight = master.winfo_screenheight()
        sWidth = 0.75 * canWidth
        if sWidth > screenWidth:
            sWidth =  0.5 *screenWidth

        sHeight = 0.75 * canWidth 
        if sHeight > screenHeight:
            sHeight = 0.75 * screenHeight

        # we are trimming too much on right side of grid, need to fix as the
        # following is a kludge XXX
        sHeight = 500
        sWidth = 500
        


        # canvas will hold grid as well as row/column labels.
        canvas = Canvas(frame, bd=0, scrollregion=(0, 0, canWidth, canHeight),
                        xscrollcommand=xscrollbar.set,
                        yscrollcommand=yscrollbar.set,width = sWidth,
                        height=sHeight,
                        yscrollincrement = height,
                        xscrollincrement = width)

        canvas.grid(row=1, column=0, sticky=N+S+E+W)
        self.canvas=canvas
        yscrollbar.config(command=self.canvas.yview)
        xscrollbar.config(command=self.canvas.xview)
        frame.grid(sticky=E+S)
        master.update_idletasks()
        x0 = maxRL
        ij = zip(range(n),rowLabels)
        x1 = 0
        x2 = x0


        cell2widget = {}
        widget2cell = {}
        text2cell = {}

        fillColors = {}


        self.rowLabels = rowLabels
        # draw row labels
        for i,label in ij:
            y1 = height + height * i
            y2 = y1 + height
            rtag = "r"+str(i)
            ctag = "c-1"
            rctag = rtag+ctag
            wid = canvas.create_rectangle(x1,y1,x2,y2,fill="grey",
                tag=(rtag,ctag,rctag,'rlabel','label'))
            fillColors[wid] = 'grey'
            wid=canvas.create_text(x2,y2,text=label,anchor=SE,
                    font=labelFont,tag=(rtag,ctag,rctag,'rlabel','labelText'))
            fillColors[wid]='black'
            widget2cell[wid] = (i,-1)
            cell2widget[(i,-1) ] = wid
        master.update_idletasks()

        # draw column labels
        self.columnLabels = columnLabels
        ij = zip(range(k), columnLabels)
        y1 = 0
        y2 = height
        for i,label in ij:
            x1 = x0 + i * width
            x2 = x1 + width
            rtag = "r-1"
            ctag = "c"+str(i)
            rctag = rtag+ctag
            wid=canvas.create_rectangle(x1,y1,x2,y2,fill="grey",
                tag=(rtag,ctag,rctag,'clabel','label'))
            fillColors[wid]="grey"
            wid=canvas.create_text(x2,y2,text=label,anchor=SE,font=labelFont,
                tag=(rtag,ctag,rctag,'clabel','labelText'))
            fillColors[wid]="black"
            cell2widget[(-1,i)] = wid
            widget2cell[wid] = (-1,i)
        master.update_idletasks()


        # draw grid
        y0 = height
        idcount = 0
        id2cell={}
        cid = 0
        flattenedIds = {}
        for r in range(n):
            for c in range(k):
                x1 = c * width + x0
                x2 = x1 + width
                y1 = r * height + y0
                y2 = y1 + height
                t = str(c)
                rt = "r"+str(r)
                ct = "c"+str(c)
                rctag = rt+ct
                cid=canvas.create_rectangle(x1,y1,x2,y2,tag=(rt,ct,rctag,"cell"),
                        fill='white',outline='grey')
                fillColors[cid]="white"
                #svalue = format(self.fmt,values[r,c])
                widget2cell[cid] = (r,c)
                cell2widget[(r,c)] = cid

                wid = canvas.create_text(x2,y2,text =
                        svalues[r*k+c],anchor=SE,tag=(rt,ct,rctag,"text"))
                fillColors[wid]="black"
                widget2cell[wid] = (r,c)
                text2cell[wid] = cid
                id2cell[idcount] = (r,c)
                flattenedIds[(r,c)] = idcount
                idcount+=1
            master.update_idletasks()
        self.id2cell = id2cell
        self.fillColors = fillColors
        self.flattenedIds = flattenedIds
        # set up event-widget-callback bindings
        self.widget2cell = widget2cell
        self.cell2widget = cell2widget
        self.text2cell = text2cell
        canvas.tag_bind('cell',"<1>",self.selectCell)
        canvas.tag_bind('cell',"<Shift-1>",self.onShiftButton1)
        canvas.tag_bind('text',"<1>",self.selectCellText)
        canvas.tag_bind('text',"<Shift-1>",self.onShiftButton1Text)
        canvas.tag_bind('cell',"<Enter>",self.entered)
        canvas.tag_bind('text',"<Enter>",self.entered)

        canvas.tag_bind('rlabel',"<1>",self.selectLabel)
        canvas.tag_bind('clabel',"<1>",self.selectLabel)
        canvas.tag_bind("labelText","<1>",self.selectLabel)

        canvas.tag_bind('rlabel',"<Shift-1>",self.selectLabelExtend)
        canvas.tag_bind('clabel',"<Shift-1>",self.selectLabelExtend)
        canvas.tag_bind("labelText","<Shift-1>",self.selectLabelExtend)
            
        self.__highlightColor="yellow"


        geom = self.master.geometry()
        wh,sxo,syo = geom.split("+")
        w,h = wh.split("x")
        h=int(h)
        w=int(w)
        
        #print geom
        # determine if we need scroll bars
        if canHeight < h:
        #    print "shrink height of table view"
            h=canHeight*1.40 # factor in bar
            
        if canWidth < w:
        #    print "shrink width of table view"
            w=canWidth*1.10
        geom="%dx%d+%s+%s"%(w,h,sxo,syo)
        #print geom
        self.master.geometry(geom)


    def setHighlightColor(self,color):
        self.__highlightColor=color

    def moveXview(self,fraction):
        """move viewable portion of canvas so that top edge is at fraction of
        entire canvas."""
        self.canvas.xview_moveto(fraction)
    def moveYview(self,fraction):
        """move viewable portion of canvas so that left edge is at fraction of
        entire canvas."""
        self.canvas.yview_moveto(fraction)

    def showCell(self,cell):
        """move viewable portion of canvas so that cell is visible."""
        x,y = cell
        xfraction = 0.9 * y*1./self.k 
        yfraction = 0.9 * x*1./self.n
        self.moveXview(xfraction)
        self.moveYview(yfraction)

    def showHighlightCell(self,cell):
        """move viewable portion of canvas so that cell is selected and visible."""
        self.selectCells([cell])
        self.showCell(cell)
        


    def entered(self,event):
        """Update the entries reporting what col/row the mouse is in."""
        tg = self.canvas.gettags('current')
        rowId = tg[0]
        colId = tg[1]
        wid = self.canvas.find_withtag('current')
        row,col = self.widget2cell[wid[0]]
        self.rowVariable.set(self.rowLabels[row])
        self.colVariable.set(self.columnLabels[col])
        self.valueVariable.set(str(self.values[row,col]))

    def unHighlightSelectedSet(self):
        """Clear the currently selected set"""
        selected = self.canvas.find_withtag('selected')
        if selected:
            sci = self.canvas.itemconfigure
            tmp = [ sci(id,fill=self.fillColors[id]) for id in selected]
            self.canvas.dtag('selected','selected')
            scg = self.canvas.gettags


    def highlightSelected(self):
        """Highlight the currently selected cell set."""
        self.canvas.itemconfigure('selected',fill=self.__highlightColor)
        self.setSelected()

    def labelColumnSelect(self,event):
        """Select all cells associated with a given column label."""
        tg = self.canvas.gettags('current')
        self.unHighlightSelectedSet()
        ct = tg[1]
        self.canvas.addtag_withtag('selected',ct)
        self.canvas.dtag('text','selected')
        self.highlightSelected()

    def labelRowSelect(self,event):
        """Select all cells associated with a given row label."""
        tg = self.canvas.gettags('current')
        self.unHighlightSelectedSet()
        rt = tg[0]
        self.canvas.addtag_withtag('selected',rt)
        self.canvas.dtag('text','selected')
        self.highlightSelected()

    def selectCell(self,event):
        """Select an individual cell."""
        tg = self.canvas.gettags('current')
        rctag = tg[2]
        self.unHighlightSelectedSet()
        self.canvas.addtag_withtag('selected',rctag)
        self.canvas.dtag('text','selected')
        self.highlightSelected()

    def selectCellText(self,event):
        """Select an individual cell underneath text value."""
        tg = self.canvas.gettags('current')
        rctag = tg[2]
        self.unHighlightSelectedSet()
        self.canvas.addtag_withtag('selected',rctag)
        self.canvas.dtag('text','selected')
        self.highlightSelected()

    def selectLabel(self,event):
        """Select a column or row  underneath label text value."""
        tg = self.canvas.gettags('current')
        if 'rlabel' in tg:
            stag = tg[0]
        else:
            stag = tg[1]
        ctag = tg[2]
        self.ctag=tg
        

        self.unHighlightSelectedSet()
        self.canvas.addtag_withtag('selected',stag)
        self.canvas.dtag('text','selected')
        self.canvas.dtag('labelText','selected')
        tg = self.canvas.gettags('current')
        self.highlightSelected()

    def selectLabelExtend(self,event):
        """Extended selection of row or columns."""
        tg = self.canvas.gettags('current')
        if 'rlabel' in tg:
            stag = tg[0]
        else:
            stag = tg[1]
        self.canvas.addtag_withtag('selected',stag)
        self.canvas.dtag('text','selected')
        self.canvas.dtag('labelText','selected')
        self.highlightSelected()


    def onShiftButton1(self,event):
        tg = self.canvas.gettags('current')
        rctag = tg[2]
        self.canvas.addtag_withtag('selected',rctag)
        self.canvas.dtag('text','selected')
        self.highlightSelected()

    def getSelectedIds(self):
        return self.canvas.find_withtag('selected')

    def setSelected(self):
        self.selected = self.getSelectedIds()

    def onShiftButton1Text(self,event):
        tg = self.canvas.gettags('current')
        rctag = tg[2]
        self.canvas.addtag_withtag('selected',rctag)
        self.canvas.dtag('text','selected')
        self.highlightSelected()

    def setName(self,name):
        """Set the title of the master window."""
        self.__name = name
        self.master.title(self.__name)

    # the following are methods used to handle messages from other objects to
    # select/unselect cells

    def selectCells(self,listofCellTuples):
        tags = [ "r"+str(row)+"c"+str(col) 
                for row,col in listofCellTuples ]
        self.unHighlightSelectedSet()
        temp = [ self.canvas.addtag_withtag('selected',tag)
                for tag in tags ]
        self.canvas.dtag('text','selected')
        self.highlightSelected()

    def selectRows(self,listofRowIds):
        self.selectAxis(listofRowIds)

    def selectColumns(self,listofColIds):
        self.selectAxis(listofColIds,axis=1)

    def selectAxis(self,listofIds,axis=0):
        lab='r'
        if axis:
            lab='c'
        tags = [ lab+str(id) for id in listofIds ]
        self.unHighlightSelectedSet()
        temp = [ self.canvas.addtag_withtag('selected',tag)
                for tag in tags ]
        self.canvas.dtag('text','selected')
        self.canvas.dtag('labelText','selected')
        self.highlightSelected()

    def selectAxisExtend(self,listofIds,axis=0):
        lab='r'
        if axis:
            lab='c'
        tags = [ lab+str(id) for id in listofIds ]
        temp = [ self.canvas.addtag_withtag('selected',tag)
                for tag in tags ]
        self.canvas.dtag('text','selected')
        self.canvas.dtag('labelText','selected')
        self.highlightSelected()


    def selectRowsExtend(self,listofRowIds):
        """Extended row selection."""
        self.selectAxisExtend(listofRowIds)


    def selectColumnsExtend(self,listofColIds):
        """Extended column selection."""
        self.selectAxisExtend(listofColIds,axis=1)

    def cleanLabels(self):
        """Removes label cells from selected set."""
        self.canvas.dtag('label','selected')


    def getSelectedCellIds(self):
        """Returns a list of row,col tuples"""
        self.cleanLabels()
        self.setSelected()
        return [ self.widget2cell[id] for id in self.selected ]

    def getSelectedValues(self):
        """Returns a list of values associated with selected cells."""
        cells = self.getSelectedCellIds()
        return [ self.values[rc] for rc in cells]

    def getSelectedItems(self):
        """Returns a tuple with two elements, first is a list of cell Ids
        (each a tuple), the second is a list of values associated with those
        cells, in the appropriate order."""
        ids = self.getSelectedCellIds()
        values = self.getSelectedValues()
        return (ids,values)

    def getFlattenedSelectedCellIds(self):
        """Returns flattened indices of grid cells.
        i.e., first k values are row 1 ids, k+2 to 2k point to cells in row 2,
        and so on.
        """
        cids = [ self.widget2cell[id] for id in self.selected 
            if 'label' not in self.canvas.gettags(id) ]
        return [ self.flattenedIds[cid] for cid in cids ]
        

class MixedDataTable(DataTable):
    """
    Spreadsheet-like grid to display grid of mixed nuermic and character values. 

    Each cell has at least three identifiers associated with it. The first is
    the row id, the second a column id , and the third is a row/col string.

    """

    def __init__(self, master, values, name=None, rowLabels=None,
                 columnLabels=None, fmt=[12,8],listener=None,
                 labelFamily="times", labelSize="12", cellFamily="times",
                 cellSize="12"):

        """
        master: top-level container widget
        values: list of lists to be displayed. each list correspondes to a row
        of grid cells and can itself contain heterogeneous elements (numeric
        or string).
        name: string
        rowLabels: length(n) list of strings for row names.
        columnLabels: length(k) list of strings for column names.
        fmt: list of number of places and digits to the right of decimal
        labelFamily: font family for row/col labels
        labelSize: size of font for row/col labels
        cellFamily: font family for grid cells
        cellSize: size of font for grid cells
        """
        DataTable.__init__(self,master,values,name=name, rowLabels=rowLabels,
            columnLabels=columnLabels,fmt=fmt,listener=listener,
            labelFamily=labelFamily,
            labelSize=labelSize,cellFamily=cellFamily,cellSize=cellSize)

    def buildGrid(self):
        v = self.values[0]
        self.types = [ type(i) for i in v]

        master = self.master
        # determine the largest width of a cell
        labelFont = tkFont.Font ( family=self.labelFamily, size=self.labelSize)
        cellFont = tkFont.Font (family=self.cellFamily, size =self.cellSize)
        n = len(self.values)
        k = len(self.values[0])
        self.n = n
        self.k = k
        nk = n * k

        # process columns (unified type) to get largest element
        # get indices for each column
        ij = [ range(j,nk,k) for j in range(k) ]
        rn = range(n)
        rk = range(k)
        values = [ self.values[i][j] for i in rn for j in rk]
        c = 0
        colMax = []
        ts = type('s')
        for colIds in ij:
            cType = self.types[c]
            if cType == ts: 
                maxLen = max([ cellFont.measure(values[i]) for i in colIds ])
            else:
                maxValue = max([values[i] for i in colIds ])
                maxLen = cellFont.measure(format(self.fmt,maxValue))

            colMax.append(maxLen)
            c+=1
        self.colMax = colMax

        # all cols same width and that width is the maximum col width

        maxSize = max(colMax)
        height = cellFont.measure('H')
        height = height * 1.6

        rowLabels = self.rowLabels

        if not rowLabels:
            rowLabels = [ str(i) for i in range(n) ]
        rsize = [ labelFont.measure(lab) for lab in rowLabels ]
        maxRL = max(rsize) * 1.10

        columnLabels = self.columnLabels
        if not columnLabels:
            columnLabels = [ str(i) for i in range(k) ]
        maxL = max([ len(label) for label in columnLabels])
        maxCL = labelFont.measure(maxL)

        if maxCL > maxSize:
            maxSize = maxCL


        # determine the size of each cell, the width/height of the canvas and
        # the area we want to display within the scrolling window
        width = 1.20 * maxSize
        canWidth = width * (k+1)
        canHeight = height * (n+1)
        canWidth = canWidth * 1.01



        # build a frame to hold summary information about size of array,
        # current row and column
        frame = Frame(master, bd=2, relief=SUNKEN)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        fLabel = Frame(frame, bd=2, relief=RAISED)
        ltext = "Size: %d rows %d columns"%(n,k)
        label = Label(fLabel,text = ltext,foreground='blue')
        label.grid(row=0,column=0)


        # widget to keep track of which row the mouse is in
        self.rowVariable = StringVar()
        rowCLabel = Label(fLabel,text="Row: ")
        rowCLabel.grid(row=0,column=1)
        rowEntry = Entry(fLabel,background='white',
            textvariable=self.rowVariable)
        rowEntry.grid(row=0,column=2)

        # widget to keep track of which column the mouse is in
        self.colVariable = StringVar()
        colCLabel = Label(fLabel,text="Column: ")
        colCLabel.grid(row=0,column=3)
        colEntry = Entry(fLabel,background='white',
            textvariable=self.colVariable)
        colEntry.grid(row=0,column=4)

        self.valueVariable = StringVar()
        valCLabel = Label(fLabel,text="Value: ")
        valCLabel.grid(row=0,column=5)
        valEntry = Entry(fLabel,background='white',
                textvariable=self.valueVariable)
        valEntry.grid(row=0,column=6)
        fLabel.grid(row=0,column=0)
        



        # build the horizontal and vertical scrollbars as well as the grid
        # itself
        xscrollbar = Scrollbar(frame, orient=HORIZONTAL)
        xscrollbar.grid(row=2, column=0, sticky=E+W)
        yscrollbar = Scrollbar(frame)
        yscrollbar.grid(row=1, column=1, sticky=N+S)

        # determine size of Table to display within scroll area
        screenWidth = master.winfo_screenwidth()
        screenHeight = master.winfo_screenheight()
        sWidth = 0.75 * canWidth
        if sWidth > screenWidth:
            sWidth =  0.5 *screenWidth

        sHeight = 0.75 * canWidth 
        if sHeight > screenHeight:
            sHeight = 0.75 * screenHeight

        # we are trimming too much on right side of grid, need to fix as the
        # following is a kludge XXX
        sHeight = 500
        sWidth = 500
        


        # canvas will hold grid as well as row/column labels.

        canvas = Canvas(frame, bd=0, scrollregion=(0, 0, canWidth, canHeight),
                        xscrollcommand=xscrollbar.set,
                        yscrollcommand=yscrollbar.set,width = sWidth,
                        height=sHeight, yscrollincrement = height,
                        xscrollincrement = width)
        canvas.grid(row=1, column=0, sticky=N+S+E+W)
        self.canvas=canvas
        yscrollbar.config(command=self.canvas.yview)
        xscrollbar.config(command=self.canvas.xview)
        frame.grid(sticky=E+S)
        master.update_idletasks()
        x0 = maxRL
        ij = zip(range(n),rowLabels)
        x1 = 0
        x2 = x0


        cell2widget = {}
        widget2cell = {}
        text2cell = {}

        fillColors = {}

        self.rowLabels = rowLabels
        # draw row labels
        for i,label in ij:
            y1 = height + height * i
            y2 = y1 + height
            rtag = "r"+str(i)
            ctag = "c-1"
            rctag = rtag+ctag
            wid = canvas.create_rectangle(x1,y1,x2,y2,fill="grey",
                tag=(rtag,ctag,rctag,'rlabel','label'))
            fillColors[wid] = 'grey'
            wid=canvas.create_text(x2,y2,text=label,anchor=SE,
                    font=labelFont,tag=(rtag,ctag,rctag,'rlabel','labelText'))
            fillColors[wid]='black'
            widget2cell[wid] = (i,-1)
            cell2widget[(i,-1) ] = wid
        master.update_idletasks()

        # draw column labels
        self.columnLabels = columnLabels
        ij = zip(range(k), columnLabels)
        y1 = 0
        y2 = height
        for i,label in ij:
            x1 = x0 + i * width
            x2 = x1 + width
            rtag = "r-1"
            ctag = "c"+str(i)
            rctag = rtag+ctag
            wid=canvas.create_rectangle(x1,y1,x2,y2,fill="grey",
                tag=(rtag,ctag,rctag,'clabel','label'))
            fillColors[wid]="grey"
            wid=canvas.create_text(x2,y2,text=label,anchor=SE,font=labelFont,
                tag=(rtag,ctag,rctag,'clabel','labelText'))
            fillColors[wid]="black"
            cell2widget[(-1,i)] = wid
            widget2cell[wid] = (-1,i)
        master.update_idletasks()


        # draw grid
        y0 = height
        idcount = 0
        id2cell={}
        cid = 0
        flattenedIds = {}
        for r in range(n):
            for c in range(k):
                x1 = c * width + x0
                x2 = x1 + width
                y1 = r * height + y0
                y2 = y1 + height
                t = str(c)
                rt = "r"+str(r)
                ct = "c"+str(c)
                rctag = rt+ct
                cid=canvas.create_rectangle(x1,y1,x2,y2,tag=(rt,ct,rctag,"cell"),
                        fill='white',outline='grey')
                fillColors[cid]="white"
                value = self.values[r][c]
                if self.types[c] == ts:
                    svalue = value
                else:
                    svalue = format(self.fmt,value)
                widget2cell[cid] = (r,c)
                cell2widget[(r,c)] = cid

                wid = canvas.create_text(x2,y2,text =
                        svalue,anchor=SE,tag=(rt,ct,rctag,"text"))
                fillColors[wid]="black"
                widget2cell[wid] = (r,c)
                text2cell[wid] = cid
                id2cell[idcount] = (r,c)
                flattenedIds[(r,c)] = idcount
                idcount+=1
            master.update_idletasks()
        self.id2cell = id2cell
        self.fillColors = fillColors
        self.flattenedIds = flattenedIds
        # set up event-widget-callback bindings
        self.widget2cell = widget2cell
        self.cell2widget = cell2widget
        self.text2cell = text2cell
        canvas.tag_bind('cell',"<1>",self.selectCell)
        canvas.tag_bind('cell',"<Shift-1>",self.onShiftButton1)
        canvas.tag_bind('text',"<1>",self.selectCellText)
        canvas.tag_bind('text',"<Shift-1>",self.onShiftButton1Text)
        canvas.tag_bind('cell',"<Enter>",self.entered)
        canvas.tag_bind('text',"<Enter>",self.entered)

        canvas.tag_bind('rlabel',"<1>",self.selectLabel)
        canvas.tag_bind('clabel',"<1>",self.selectLabel)
        canvas.tag_bind("labelText","<1>",self.selectLabel)

        canvas.tag_bind('rlabel',"<Shift-1>",self.selectLabelExtend)
        canvas.tag_bind('clabel',"<Shift-1>",self.selectLabelExtend)
        canvas.tag_bind("labelText","<Shift-1>",self.selectLabelExtend)
            


        geom = self.master.geometry()
        wh,sxo,syo = geom.split("+")
        w,h = wh.split("x")
        h=int(h)
        w=int(w)
        
        #print geom
        # determine if we need scroll bars
        if canHeight < h:
        #    print "shrink height of table view"
            h=canHeight*1.40 # factor in bar
            
        if canWidth < w:
        #    print "shrink width of table view"
            w=canWidth*1.10
        geom="%dx%d+%s+%s"%(w,h,sxo,syo)
        #print geom
        self.master.geometry(geom)


    def entered(self,event):
        """Update the entries reporting what col/row the mouse is in."""
        tg = self.canvas.gettags('current')
        rowId = tg[0]
        colId = tg[1]
        wid = self.canvas.find_withtag('current')
        row,col = self.widget2cell[wid[0]]
        self.rowVariable.set(self.rowLabels[row])
        self.colVariable.set(self.columnLabels[col])
        self.valueVariable.set(str(self.values[row][col]))










if __name__ == '__main__':

    # here is how we would use our new Table class
    from numpy.oldnumeric import *

    # cook up some data
    n=300
    k=33
    nk = n * k
    rowLabels = [ "Region %d"%i for i in range(n) ]
    columnLabels = [ str(i) for i in range(k) ]
    values = arange(nk)
    values = reshape(values,(n,k))

    # get a master
    root=Tk()

    # create an instance
    #t=DataTable(root,values,name="Variable Name Here",rowLabels=rowLabels,
    #    columnLabels=columnLabels,fmt=[8,0])
   # 

    from stars import Project
    from Markov import *
    s=Project('s')
    s.ReadData("data/csiss")
    y = s.getVariable('pcr')
    n,k = shape(y)
    #values=y
    #ijs = [ (i,j) for i in range(n) for j in range(k) ]
    #svalues = [ format([8,3], values[i,j]) for i,j in ijs ]
    s.ReadGalMatrix('states48')
    w=s.getMatrix('states48')
    sm = SpMarkov(y,w=w)
    classes = [ "%5.3f"% value for value in sm.upperBounds ]
    k=len(classes)
    rowLabels = [ c+" | "+r for r in classes for c in classes ]
    mat = sm.pMat
    mat = reshape(mat,(k*k,k))
    st = DataTable(root,mat,rowLabels=rowLabels,
            columnLabels=classes,fmt=[8,3],
            name='Spatial Markov Transition Probabilities')
    top = Toplevel(root)
    yt = DataTable(top,y,
            rowLabels=s.regionNames,
            columnLabels=s.timeString,
            fmt=[8,3],name="PCR")
    #mtop = Toplevel(root)
    #ym=ClMarkov(y)
    #labels = [ "%8.3f"%value for value in ym.upperBounds ]
    #tm = DataTable(mtop,ym.pMat,rowLabels=labels,
    #        columnLabels=labels,name="Classic Markov Transitions",
    #        fmt=[8,3])

    #matTop = Toplevel(root)
    #wf = w.full()
    #matTab = DataTable(matTop,wf,
    #        rowLabels=s.regionNames,
    #        columnLabels=s.regionNames,
    #        fmt=[8,3],
    #        name="Simple Contiguity Matrix")

    mtop = Toplevel(root)

    # make up mixed character and numeric data
    #regionNames = s.regionNames
    #pcr = [ region.tolist() for region in s.getVariable('pcr') ]
    #z = zip(regionNames,pcr)
    #rn = range(len(z))
    #a = [ z[i][1].insert(0,z[i][0]) for i in rn ]
    #m = [ row[1] for row in z]
    #clabels = [ str(c) for c in range(len(pcr[0])) ]
    #clabels.insert(0,'Region')


    #mt = MixedDataTable(mtop,m,name="mixed", columnLabels=clabels)
        

