import Tkinter as tk
import numpy as np


m1 = tk.PanedWindow()
m1.pack(fill=tk.BOTH, expand='yes')

left = tk.Label(m1, text="legend",relief=tk.SUNKEN)
m1.add(left)

m2 = tk.PanedWindow(m1, orient=tk.VERTICAL)
m1.add(m2)

top = tk.Label(m2, text="view")
m2.add(top)


tk.mainloop()
