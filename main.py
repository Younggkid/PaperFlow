from tkinter import *
import os
from database import DataBase
#window = Tk()
#window.title("First Window")
#window.mainloop()
#a=os.system("ping 192.168.1.101")
new = DataBase()
info = {'No' : 2,'ReadOrNot' : 1,'YearofPublish': 2019,'PaperTitle' :'find bug in real world','Author' :'dod',
            'Conference': 'CCS',
            'Tags' :'fucker',
            'Location' : 'haah',
            'LastReadDate': '20-9',
            'URL' :'why',
            'Q1'  :'why',
            'Q2'  :'why',
            'Q3'  :'why',
            'Q4'  :'why',
            'Q5'  :'why'}
new.add_data(info)
info2 = {'No' : 2,'ReadOrNot' : 1,'YearofPublish': 2023,'PaperTitle' :'software develo','Author' :'alice',
            'Conference': 'usenix',
            'Tags' :'fucker',
            'LastReadDate': '20-9',
            'Location' : 'haah',
            'URL' :'why',
            'Q1'  :'why',
            'Q2'  :'why',
            'Q3'  :'why',
            'Q4'  :'why',
            'Q5'  :'why'}
new.modi_data(info2)
new.show_all_paper()

