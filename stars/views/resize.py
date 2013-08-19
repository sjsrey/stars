import Tkinter as tk

root = tk.Tk()
scrollbar = tk.Scrollbar(root, orient="vertical")
lb = tk.Listbox(root, width=50, height=20, yscrollcommand=scrollbar.set)
scrollbar.config(command=lb.yview)

scrollbar.pack(side="right", fill="y")
lb.pack(side="left",fill="both", expand=True)
for i in range(0,100):
    lb.insert("end", "item #%s" % i)

root.mainloop()
