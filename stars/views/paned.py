import Tkinter as tk
import numpy as np

from view import CanvasFrame, LegendFrame

top = tk.Toplevel()
top.title('New Title')
m1 = tk.PanedWindow(top)
m1.pack(fill=tk.BOTH, expand='yes')

#left = tk.Label(m1, text="legend",relief=tk.SUNKEN)
legend = LegendFrame(m1)
legend.pack()
m1.add(legend)

m2 = tk.PanedWindow(m1, orient=tk.VERTICAL)
view = CanvasFrame(m2)
view.pack()
m1.add(m2)

#m1.sash_place(0,0,1)



#tk.mainloop()
