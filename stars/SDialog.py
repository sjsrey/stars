"""
Dialog classes module for Space-Time Analysis of Regional  Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW
"""


from Tkinter import *
from glob import glob
from stars import options
import os
import version

GIFFILE = os.path.join(options.getSTARSHOME(),"splash.gif")

c1="Copyright (C) 2000-2011, Sergio J. Rey\n"
c1 += "Copyright (c) 2011-2014 STARS Developers\n"
crnotice1="%sSTARS version %s from %s"%(c1,version.VERSION,version.DATE) 
crnotice2="STARS comes with ABSOLUTELY NO WARRANTY.\n"\
          "This is free software, and you are welcome to redistribute\n"\
          "it under certain conditions. See COPYING for details."

class SDialog(Toplevel):
    """Dialog to obtain arguments for underlying stars classes via the
    gui.

    Arguments (3):
        title: the title of the dialog window (string)
        optbridge: a dictionary of lists. each list has two elements,
        the first is the label for the entry in the Dialog. this should
        match an option in the underlying class method the dialog is
        prompting for. the second element of the list is a StringVar
        used to store the dialog entry value.  
        listDict: dictionary having key id (for option) and list of
        values to display in a scrollable listbox. This is optional
    """
    def __init__(self, title, optBridge,listDict=[]):
        self.top=Toplevel.__init__(self)
        frames=[]
        entries=[]
        self.title(title)
        self.listDict = listDict
        lTitle = len(title)
        optionIds=optBridge.keys()
        optionIds.sort()
        fcount=0
        # get maximum label width
        labelWidth = max([ len(optBridge[x][0]) for x in optBridge.keys()])
        #entryWidth = labelWidth * 2
        entryWidth = 50 
        self.optionLabels = []

        for id in optionIds:
            prompt=optBridge[id]
            optionName=prompt[0]
            self.optionLabels.append(optionName)
            optionDefault=prompt[1]
            frames.append(Frame(self,width=200))
            if fcount==0:
                frames[fcount].pack(anchor=N, expand=YES, fill=X,padx=lTitle)
                Label(frames[fcount], text=optionName, relief=RIDGE, width=labelWidth).pack(side=LEFT)
                entries.append(Entry(frames[fcount],relief=SUNKEN,width=entryWidth))
                entries[fcount].pack(side=RIGHT, expand=YES, fill=X)
            else:
                frames[fcount].pack(anchor=CENTER, expand=YES, fill=X,padx=lTitle)
                Label(frames[fcount], text=optionName, relief=RIDGE, width=labelWidth).pack(side=LEFT)
                entries.append(Entry(frames[fcount],relief=SUNKEN,width=entryWidth))
                entries[fcount].pack(side=RIGHT, expand=YES, fill=X)
            fcount=fcount+1
        buttonFrame=Frame(self,width=200)
        Button(buttonFrame, text="OK",  underline=0,
                command=self.destroy).pack(side=LEFT)
        Button(buttonFrame, text="Reset",  underline=0,
                command=self.reset).pack(side=LEFT)
        Button(buttonFrame, text="Cancel",  underline=0,
                command=self.destroy).pack(side=LEFT)
        buttonFrame.pack()
        self.entries = entries
        #print self.entries
        self.fcount = fcount
        if listDict:
            self.commands = {}
            for key in listDict.keys():
                items  = listDict[key]
                entries[key-1].bind("<Double-1>",self.itemselector)
                self.optionTitle = key
                entries[key-1]['background']="YELLOW"
                e = entries[key-1]
                self.commands[e] = [items,key-1]

        fcount=0
        for id in optionIds:
            entries[fcount]['textvariable'] = optBridge[id][1] 
            fcount=fcount+1

        self.optBridge = optBridge
        self.optionIds = optionIds

        # get defaults for resets
        self.defaults = [ entry.get() for entry in entries]

        mysize=self.geometry() 
        mysize = mysize.split("x")
        width = 100
        mysize[0] = str(width)
        mysize = "x".join(mysize)
        xmax = self.winfo_screenwidth()
        if xmax > 1280:
            xmax = 1280 # prevent spread across dual-extended displays
        ymax = self.winfo_screenheight()
        wxmax = self.winfo_reqwidth()
        wymax = self.winfo_reqheight()
        x = (xmax - wxmax) / 2
        y = (ymax - wymax) / 2
        self.geometry("+%d+%d" % (x,y))
        #print xmax,ymax,wxmax,wymax,x,y

        self.grab_set() #make model
        self.focus_set() # mouse grab
        self.wait_window()

    def itemselector(self,event):
        entryKey = self.commands[event.widget][1]
        entries = self.commands[event.widget][0]
        self.entries[entryKey].delete(0,END)
        #print entryKey
        self.grab_release()
        class dialogScrolledList(ScrolledList):
            def __init__(self,master,entries):
                ScrolledList.__init__(self,master)
                self.entries = entries
                self.master = master
            def on_select(self,index):
                item = self.get(index)
                self.entries[entryKey].insert(END,item)
                self.master.destroy()
            def on_extendedSelect(self,index):
                item = self.get(index)
                item = item+" "
                self.entries[entryKey].insert(END,item)
            def clearContents(self):
                self.entries[entryKey].delete(0,END)

        master = Toplevel(self.top) 
        position ="+%d+%d"%(event.x_root,event.y_root)
        master.wm_geometry(position)
        master.title(self.optionLabels[entryKey])
        s = dialogScrolledList(master,self.entries)
        for item in entries:
            s.append(item)
        s.master.focus_set()
        s.master.wait_window()

    def reset(self):
        """Resets any defaults of entries"""
        for i in range(self.fcount):
            self.entries[i].delete(0,END)
        i = 0
        for default in self.defaults:
            self.entries[i].insert(0,default)
            i += 1




class Options:
    """ """
    def __init__(self,options):
        n=len(options)
        option={}
        id=range(n)
        for i in id:
            option[i]=[options[i],StringVar()]
        self.option=option

class SRadioQuery(Toplevel):
    def __init__(self,title):
        Toplevel.__init__(self)
        frame=Frame(self)
        frame.pack(anchor=N,expand=YES,fill=X)
        var=IntVar()
        for text, value in [('Passion fruit',1),('Loganberries',2), ('Mangoes in syrup',3)]:

                Radiobutton(frame,text=text,value=value,variable=var).pack(anchor=W)
        var.set(3)
        Button(frame,text="OK",command=self.destroy).pack(anchor=S)



class ScrolledList:

    default = "(None)"

    def __init__(self, master, singleSelect=1,**options):
        # Create top frame, with scrollbar and listbox
        self.master = master
        self.singleSelect = singleSelect
        self.selections = []
        self.frame = frame = Frame(master)
        self.frame.pack(fill="both", expand=1)
        self.vbar = vbar = Scrollbar(frame, name="vbar")
        self.vbar.pack(side="right", fill="y")
        self.listbox = listbox = Listbox(frame, exportselection=0,
            background="white")
        if options:
            listbox.configure(options)
        listbox.pack(expand=1, fill="both")
        # Tie listbox and scrollbar together
        vbar["command"] = listbox.yview
        listbox["yscrollcommand"] = vbar.set
        # Bind events to the list box
        listbox.bind("<ButtonRelease-1>", self.click_event)
        listbox.bind("<ButtonRelease-2>", self.click_2)
        listbox.bind("<Double-ButtonRelease-1>", self.double_click_event)
        listbox.bind("<ButtonRelease-3>", self.click_3)
        #listbox.bind("<ButtonPress-3>", self.popup_event)
        listbox.bind("<Key-Up>", self.up_event)
        listbox.bind("<Key-Down>", self.down_event)
        # Mark as empty
        self.clear()

    def close(self):
        self.frame.destroy()

    def clear(self):
        self.listbox.delete(0, "end")
        self.empty = 1
        self.listbox.insert("end", self.default)

    def append(self, item):
        if self.empty:
            self.listbox.delete(0, "end")
            self.empty = 0
        self.listbox.insert("end", str(item))

    def get(self, index):
        return self.listbox.get(index)

    def click_event(self, event):
        self.listbox.activate("@%d,%d" % (event.x, event.y))
        index = self.listbox.index("active")
        self.select(index)
        self.selections.append(index)
        self.on_select(index)
        return "break"

    def click_3(self,event):
        self.listbox.activate("@%d,%d" % (event.x, event.y))
        index = self.listbox.index("active")
        self.select(index)
        self.selections.append(index)
        self.on_extendedSelect(index)
        return "break"

    def click_2(self,event):
        self.clearContents()
        return "break"

    def clearContents(self):
        pass

    def double_click_event(self, event):
        index = self.listbox.index("active")
        self.select(index)
        self.on_double(index)
        return "break"

    menu = None

    def popup_event(self, event):
        if not self.menu:
            self.make_menu()
        menu = self.menu
        self.listbox.activate("@%d,%d" % (event.x, event.y))
        index = self.listbox.index("active")
        self.select(index)
        menu.tk_popup(event.x_root, event.y_root)

    def make_menu(self):
        menu = Menu(self.listbox, tearoff=0)
        self.menu = menu
        self.fill_menu()

    def up_event(self, event):
        index = self.listbox.index("active")
        if self.listbox.selection_includes(index):
            index = index - 1
        else:
            index = self.listbox.size() - 1
        if index < 0:
            self.listbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def down_event(self, event):
        index = self.listbox.index("active")
        if self.listbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= self.listbox.size():
            self.listbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def select(self, index):
        self.listbox.focus_set()
        self.listbox.activate(index)
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        self.listbox.see(index)

    # Methods to override for specific actions
    def getSelections(self):
        return self.selections

    def fill_menu(self):
        pass

    def on_select(self, index):
        pass

    def on_double(self, index):
        pass

    def on_extendedSelect(self,index):
        pass

def test():
    root = Tk()
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    class MyScrolledList(ScrolledList):
        def fill_menu(self): self.menu.add_command(label="pass")
        def on_select(self, index):
            print "select", self.get(index)
            print "fill entry with",self.get(index)
        def on_double(self, index):
            print "double", self.get(index)
            print "fill entry with",self.get(index)
    s = MyScrolledList(root,singleSelect=0)
    for i in range(30):
        s.append("item %02d" % i)

    return root


class SplashScreen(Toplevel):
    """Stars Splash Screen """
    def __init__(self,master=None):
        Toplevel.__init__(self,master,relief=RAISED,borderwidth=5)
        self.main = master
        if self.main.master !=None:
            self.main.master.withdraw()
        self.main.withdraw()
        #self.overriderdirect(1)
        self.CreateWidgets()
        self.after_idle(self.CenterOnScreen)
        self.update()


    def CenterOnScreen(self):
        self.update_idletasks()
        xmax = self.winfo_screenwidth()
        if xmax > 1920:
            xmax = 1920 # prevent spreading across dual-extended displays
        ymax = self.winfo_screenheight()
        xo = (xmax - self.winfo_reqwidth()) / 2
        yo = (ymax - self.winfo_reqheight()) / 2
        self.geometry("+%d+%d" % (xo,yo))

    def CreateWidgets(self):
        self.image = PhotoImage(file=GIFFILE)
        self.label = Label(self,image=self.image)
        self.label.pack(side=TOP)
        self.label = Label(self,text=crnotice1)
        self.label.pack(side=TOP)
        label = Label(self,font="Helvetica 10",text = crnotice2,
            justify=CENTER)
        label.pack(side=TOP)




    def Destroy(self):
        #raw_input("pause")
        self.after(1000)
        self.main.update()
        self.main.deiconify()
        self.withdraw()
    

    


def zipper(sequence):
    n = len(sequence)
    rn = range(n)
    data = zip(rn,sequence)
    return data



class Option_Dialogue(Toplevel):
    """Container Dialogue.
    """
    def __init__(self,title="OptionDialogue"):
        Toplevel.__init__(self)
        self.set_status(0)
        self.title(title)

    def set_status(self,status):
        self.status = status

    def toggle_ok(self):
        self.set_status(1)
        self.destroy()

    def toggle_cancel(self):
        self.set_status(0)
        self.destroy()

    def show(self):
        fr = LabelFrame(self,text="")
        Button(fr,text="Ok",command=self.toggle_ok).grid(row=0,column=0)
        Button(fr,text="Cancel",command=self.toggle_cancel).grid(row=0,column=1)
        fr.grid(columnspan=2,sticky=E)

        mysize=self.geometry() 
        mysize = mysize.split("x")
        width = 100
        mysize[0] = str(width)
        mysize = "x".join(mysize)
        xmax = self.winfo_screenwidth()
        if xmax > 1280:
            xmax = 1280 # prevent spread across dual-extended displays
        ymax = self.winfo_screenheight()
        wxmax = self.winfo_reqwidth()
        wymax = self.winfo_reqheight()
        x = (xmax - wxmax) / 2
        y = (ymax - wymax) / 2
        self.geometry("+%d+%d" % (x,y))
        self.grab_set() #make model
        self.focus_set() # mouse grab
        self.wait_window()




class Radio_Buttons:
    """

    """
    def __init__(self, parent, labels, clearButton = TRUE):
        buttons = {}
        var = IntVar()
        data = zipper(labels)
        for i,label in data:
            buttons[i] = Radiobutton(parent, text=label, variable=var, value=i)
            buttons[i].grid(row=0,column=i)
        self.buttons = buttons
        if clearButton:
            i += 1
            Button(parent,command=self.clear,text="None").grid(row=0,column=i)
        self.var = var

    def clear(self):
        for button in self.buttons:
            self.buttons[button].deselect()

    def get(self):
        self.values = self.var.get() 
        return self.values
    

class Check_Buttons:
    """ """
    def __init__(self, parent, labels, clearButton = TRUE, multiView = TRUE):
        buttons = {}
        vars = {}
        if multiView:
            data = zipper(labels)
        else:
            data = [(0, labels)]
        for i,label in data:
            vars[i] = IntVar()
            buttons[i] = Checkbutton(parent, text=label, variable=vars[i])
            buttons[i].grid(row=0,column=i)
        self.buttons = buttons
        self.vars = vars
        if clearButton:
            i += 1
            Button(parent,command=self.clear,text="None").grid(row=0,column=i)

    def clear(self):
        for button in self.buttons:
            self.buttons[button].deselect()

    def get(self):
        self.values = []
        for button in self.buttons:
            self.values.append((button,self.vars[button].get()))
        return self.values

class Single_Entry:
    """ """
    def __init__(self, parent, values=(), label=None):
        n_col,n_row = parent.grid_size()
        l = Label(parent,text=label)
        l.grid(row=n_row, column=0, sticky=E)
        sp = Spinbox(parent,values=values,command = self.retrieve)
        sp.grid(row=n_row, column=1, sticky=W)
        self.sp = sp
        self.retrieve()

    def retrieve(self):
        self.value = self.sp.get()

    def get(self):
        return self.value

class User_Entry:
    """Class that serves as an alternative to Single_Entry.  It does not
    require a tuple of options as in Single_Entry.  You use User_entry
    when you want to allow the user to provide input of any kind.  For
    example: when new STARS variables are created, often we want the
    user to be able to define the new name for thew variable.  You MUST
    use the User_Entry class in this instance.
    
    label:    serves as the label for the entry box.
    default:  you may provide a default value to be placed into the
              entry box.  Use this argument to do so.
    """
    def __init__(self, parent, label=None, default=''):
        n_col,n_row = parent.grid_size()
        l = Label(parent,text=label)
        l.grid(row=n_row, column=0)
        value = StringVar()
        userEntry = Entry(parent,textvariable=value)
        userEntry.insert(END,default)
        userEntry.grid(row=n_row,column=1)
        self.value = value
        
    def get(self):
        result = self.value.get()
        return result
        
class Combo_Entry:
    """Defines a SpinBox to be coupled with a Text widget to allow multiple
    items to be selected from a list. 

    Selections are made by Control-clicking on the currently displayed option
    in the SpinBox. The entry selected is then added to the selections text
    widget.
    """
    def __init__(self, parent, values, option_label="Options",
            selections_label="Selections"):
        """
        ARGUMENTS:
        
        parent: widget that contains this instance.
        values: list of values to be assigned to SpinBox.
        option_label: text label for the SpinBox
        selections_label: text label for selection text box
        """
        self.parent = parent
        spb = Spinbox(parent, values=values)
        spb_label = Label(parent, text=option_label)
        spb_label.grid(row=0,column=0,sticky=E)
        spb.grid(row=0,column=1,sticky=W)
        text = Text(parent, height=4, width=20)
        scroll = Scrollbar(parent, command=text.yview)
        text_label = Label(parent, text=selections_label)
        text.configure(yscrollcommand=scroll.set)
        text_label.grid(row=1, column=0, sticky=E)
        text.grid(row=1, column=1, sticky=W)
        scroll.grid(row=1, column=2, sticky=W)
        spb.bind("<Control-1>",self.add_selection)
        self.spb = spb
        self.entry = text
        self.retrieve()
        self.default = [values[0]]
    
    def add_selection(self,event):
        """
        handle selection of entry in SpinBox and update selections in text
        widget.
        """
        value = self.spb.get()
        self.entry.insert(END,value)
        self.entry.insert(END,"\n")
        self.entry.see(END)
        self.retrieve()

    def retrieve(self):
        """
        needed to update values before deletion of widget.
        """
        values = self.entry.get(1.0,END)
        values = [ value for value in values.split("\n") if value]
        self.values = values



    def get(self):
        """
        Return a list of selection values (as strings).
        """
        if not self.values:
            self.values = self.default
        return self.values


if __name__ == '__main__':
    
         
    root = Tk()
    d = Option_Dialogue("A Little Example Dialogue")
    fr = LabelFrame(d)
    se = Single_Entry(fr,values=('Income','Employment','Output'),label='Variable')
    fr.grid(sticky=W)
    lf = LabelFrame(d,text="Variables")
    vls = Combo_Entry(lf,("Income","Per Capita Income","Local I"))
    lf.grid(sticky=W)
    lf = LabelFrame(d,text="Graphs")
    cb = Check_Buttons(lf,("Scatter","Map","Box","Density"))
    lf.grid(sticky=W)
    lf = LabelFrame(d,text='ColorScheme')
    rb = Radio_Buttons(lf,('White','Gray'))
    lf.grid(sticky=W)
    lf = LabelFrame(d,text='Inference')
    perm = Single_Entry(lf,(0,999),'Permutations')
    variance = Single_Entry(lf,('Normality','Randomization'),'Variance')
    lf.grid(sticky=W)
    lf = LabelFrame(d,text='Graphs')
    d.show()

    # process the settings in the Option_Dialogue
    if d.status:
        print 'Called'
        print se.get()
        print vls.get()
        print cb.get()
        print rb.get()
        print perm.get()
        print variance.get()
    else:
        print 'Cancelled'

        
        
        
