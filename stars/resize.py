from Tkinter import *      

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master,width=900,height=600)
        self.width, self.height=500,500
        self.feature = 'lines'
        coords=[[20,20,70,70],[300,300,350,430]]
        self.coordinates=coords

        self.createWidgets(self.width,self.height)
        # binding to Configure handles user resizing the window
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
        self.canvas.create_text(250,250,text='center here')

    def canvas_conf(self,event):
        x_scale = event.width*1.0/self.width
        y_scale = event.height*1.0/self.height
        self.width = event.width
        self.height = event.height
        #canvas.scale handles the rezie
        self.canvas.scale(ALL,0,0,x_scale,y_scale)
       

app = Application()                   
app.master.title("Resize Demo")                                                    
app.mainloop()
