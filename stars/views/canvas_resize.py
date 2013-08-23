

import Tkinter as tk

class CanvasFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("CanvasView")
        self.pack(fill=tk.BOTH, expand = 1)
        height = self.parent.winfo_screenheight() / 2.
        width = self.parent.winfo_screenwidth() /2.
        length = height
        if width < height:
            length = width
        self.canvas = tk.Canvas(self, bg='white', width=length, height=length)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky='nesw')
        self.canvas.create_line(0, 0, width, height, width = 5.0)
        self.canvas.create_line(0, height, width, 0, width = 5.0)
        self.config_events = 0

        # Event bindings
        self.canvas.bind('<Configure>', self.onConfigure)

    def onConfigure(self, event):
        print '(%d, %d)' %(event.width, event.height)
        print 'config_events: ', self.config_events
        #self.canvas.delete(tk.ALL)
        #self.canvas.create_line(0,0, event.width, event.height, width=5.0)
        self.width = event.width
        self.height = event.height
        self.redraw()
        self.config_events += 1

    def redraw(self):
        self.canvas.delete(tk.ALL)
        # buffer so we have some space between edge of parent window and our drawing
        # bounding box
        buff = (1 - 0.025)
        if self.width < self.height:
            length = self.width
        else:
            length = self.height

        length *= buff
        self.x0 = self.width - length
        self.x0 /= 2
        self.x1 = self.x0 + length
        self.y0 = self.height - length
        self.y0 /= 2
        self.y1 = self.y0 + length

        # world coords for line
        wc_line = [ (100,100), (2000,2000) ]
        wc_line1 = [ (100,2000), (2000, 100) ]

        min_x = 100
        min_y = 100
        max_x = 2000
        max_y = 2000

        width_world = max_x - min_x
        height_world = max_y - min_y
        sy = length * 1. / height_world
        sx = length * 1. / width_world

        x0 = (100 - min_x) * sx + self.x0
        y0 = self.y0 + (max_y - 100) * sy 
        x1 = (2000 - min_x) * sx + self.x0
        y1 = self.y0 + (max_y - 2000) * sy
        self.canvas.create_line(x0, y0, x1, y1, width=1.0)

        # second line
        x0 = (100 - min_x) * sx + self.x0
        y0 = self.y0 + (max_y - 2000) * sy 
        x1 = (2000 - min_x) * sx + self.x0
        y1 = self.y0 + (max_y - 100) * sy
        self.canvas.create_line(x0, y0, x1, y1, width=1.0)


        # left
        self.canvas.create_line(x0, y0, x0, y1, width=1.0)
        # right
        self.canvas.create_line(x1, y0, x1, y1, width=1.0)
        # top
        self.canvas.create_line(x0, y1, x1, y1, width=1.0)
        # bottom
        self.canvas.create_line(x0, y0, x1, y0, width=1.0)





if __name__ == '__main__':
    root = tk.Tk()
    view = CanvasFrame(root)
    root.mainloop()


