from Tkinter import *      
#from getCor import *
#from convert import *
#lines = getCoor("Test Vector") # "Test Vector" is the line shapefile's name
                               # You can change it to other line shapefile

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master,width=900,height=600)
        self.width, self.height=500,500
        self.feature = 'lines'
        coords=[[20,20,70,70],[300,300,350,430]]
        self.coordinates=coords
        #self.coordinates = convert(self.feature,self.width,self.height)

        self.createWidgets(self.width,self.height)
        self.bind('<Configure>', self.canvas_conf)
        self.grid(sticky=N+S+E+W)
       
    def createWidgets(self,wid,high):
        top = self.winfo_toplevel()
        top.rowconfigure(0,weight=1)
        top.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        self.canvas = Canvas(self, bg="gray",width=wid,height=high)       
        self.width = self.canvas.winfo_reqwidth()
        self.height = self.canvas.winfo_reqheight()
        #self.drawLines(self.canvas,self.coordinates)
        self.drawObjects()
        self.canvas.grid(row=0,column=0,sticky=N+S+E+W)        

    def drawObjects(self):
        for i in range(10):
            x0=i*50
            x1=x0+50
            for j in range(10):
                y0=j*50
                y1=y0+50
                coords=(x0,y0,x1,y0,x1,y1,x0,y0)
                self.canvas.create_polygon(coords,fill='green')
                print x0,x1,y0,y1
        self.canvas.create_text(250,250,text='hi there')
    def drawLines(self,canvas,coordinates):
        lines = []
        """
        coordinates is from the convert function to get the coordinates
        of the features on the canvas
        """
        for line in coordinates:
            xo = line[0]
            yo = line[1]
            xd = line[2]
            yd = line[3]
            id = canvas.create_line(xo,yo,xd,yd,tags = "lines")
            lines.append(id)
       
        return lines

    def canvas_conf(self,event):
        x_scale = event.width*1.0/self.width
        y_scale = event.height*1.0/self.height
        self.width = event.width
        self.height = event.height
        self.canvas.scale(ALL,0,0,x_scale,y_scale)
       

app = Application()                   
app.master.title("Sample application")                                                    
app.mainloop()
