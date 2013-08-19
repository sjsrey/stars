
import Tkinter as tk

class CanvasFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("CanvasView")
        self.pack(fill=tk.BOTH, expand = 1)
        self.canvas = tk.Canvas(self, bg='white', width=300, height=100)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky='nesw')
        self.canvas.create_line(0, 0, 300, 100, width = 5.0)
        self.canvas.create_line(0, 100, 300, 0, width = 5.0)
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
        self.canvas.create_line(0, 0, self.width, self.height, width=5.0)
        self.canvas.create_line(0, self.height, self.width, 0, width=5.0)


if __name__ == '__main__':
    root = tk.Tk()
    view = CanvasFrame(root)
    root.mainloop()

