from tkinter import *
import os
from database import DataBase
window = Tk()
window.title("First Window")
window.mainloop()
a=os.system("ping 192.168.1.101")
new = DataBase()