
import Tkinter as tk

class CanvasFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH, expand = 1)
        self.canvas = tk.Canvas(self, bg='white', width=300, height=100)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky='nesw')


if __name__ == '__main__':
    root = tk.Tk()
    view = CanvasFrame(root)
    root.mainloop()

