import tkinter as tk
from tkinter import DISABLED, HORIZONTAL, VERTICAL, ttk, filedialog

from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import showerror, showinfo
from tkinter.scrolledtext import ScrolledText
import configparser, os, subprocess, copy
import sys
import crawl_API
from database import DataBase
from globalvar import *

SETTING_PATH = "setting.conf"

Q_TEXT = [
    "论文试图解决什么问题？",
    "这是否是一个新的问题？",
    "这篇文章要验证一个什么科学假设？",
    "有哪些相关研究？如何归类？谁是这一课题在领域内值得关注的研究员？",
    "论文中提到的解决方案之关键是什么？",
    "论文中的实验是如何设计的？",
    "用于定量评估的数据集是什么？代码有没有开源？",
    "论文中的实验及结果有没有很好地支持需要验证的科学假设？",
    "这篇论文到底有什么贡献？",
    "下一步呢？有什么工作可以继续深入？"
]

class TkUI:

    def __init__(self, 
        db:DataBase=None, 
        ):
        #  内部变量赋值
        # 数据库
        if (db != None):
            self.m_db = db      
        else:
            self.m_db = DataBase()
        self.m_conf = None  # 配置文件
        self.get_setting()  # m_conf赋值

        self.all_tag_list = self.m_db.get_all_tags() # 标签列表
        self.all_puber_list = self.m_db.get_all_pub() # 会议列表
        self.paper_list = []    # 当前展示的paper
        self.filter = {}    # 当前的筛选条件

        self.root = tk.Tk()     # 主窗口
        self.menu = tk.Menu(self.root)  # 菜单栏

        # 设置root的分割 允许填充
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.info_frame = tk.Frame(self.root)   # 底端显示信息的框
        self.info_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.body_frame = tk.Frame(self.root)   # 主体frame
        self.body_frame.grid(row=0, column=0, sticky=tk.NSEW)

        # 设置body_frame的分割 允许show_frame填充
        self.body_frame.grid_rowconfigure(0, weight=1)
        self.body_frame.grid_columnconfigure(1, weight=1)
        self.search_frame = tk.Frame(self.body_frame, )   # 搜索frame
        self.search_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.show_frame = tk.Frame(self.body_frame)     # 显示frame
        self.show_frame.grid(row=0, column=1, sticky=tk.NSEW)


        # 窗口基本设置
        self.root.geometry("1500x800+100+100")
        self.root.title("PaperFlow")
        self.root.protocol("WM_DELETE_WINDOW",self.root.destroy)

        # 设置菜单栏
        self.menu.add_command(label="手动添加", command=lambda:open_add_ui(self))
        self.menu.add_command(label="自动导入", command=lambda:do_nothing(self))
        self.menu.add_command(label="设置", command=lambda:open_setting_ui(self))
        self.menu.add_command(label="退出", command=self.root.destroy)

        # 放置菜单栏
        self.root.config(menu=self.menu)

        # 底端信息框
        self.info_frame.config(bg="#ffffdd", bd='1p')
        self.info_var = tk.StringVar()
        self.info_var.set("Info: No Info!")
        self.info = tk.Label(self.info_frame, bg='#ffffdd', textvariable=self.info_var)
        self.info.pack(side='left')

        
        # 搜索栏
        self.search_frame.config(bg='#f3f3f3', bd='1p')
        self.search_frame.grid_columnconfigure(1, weight=1)
        # 按发表年份搜索
        self.pubyear_frame = tk.Frame(self.search_frame)
        self.pubyear_frame.grid(row=1, column=0, sticky='we')
        tk.Label(self.pubyear_frame,text="发表时间").pack(side='left')
        tk.Label(self.pubyear_frame,text="从：").pack(side='left')
        self.pubyear_begin_entry = tk.Entry(self.pubyear_frame, width=5)
        self.pubyear_begin_entry.pack(side='left')
        tk.Label(self.pubyear_frame,text="到：").pack(side='left')
        self.pubyear_end_entry = tk.Entry(self.pubyear_frame, width=5)
        self.pubyear_end_entry.pack(side='left')
        # 按照标签搜索
        self.tag_frame = tk.Frame(self.search_frame)
        self.tag_frame.grid(row=2, column=0, sticky='we')
        tk.Label(self.tag_frame, text="包含标签").grid(row=0, column=0, columnspan=2)
        tk.Button(self.tag_frame, text="+", command=self.search_add_tag).grid(row=1,column=0)
        tk.Button(self.tag_frame, text='-', command=self.search_remove_tag).grid(row=1, column=1)
        # 标签输入
        self.search_tag_input_list = []
        self.search_tag_input_list.append( ttk.Combobox(self.tag_frame, values=self.all_tag_list) )
        self.search_tag_input_list[0].grid(row=0, column=2)
        # 按照期刊搜索
        self.puber_frame = tk.Frame(self.search_frame)
        self.puber_frame.grid(row=3, column=0, sticky='we')
        tk.Label(self.puber_frame, text="含出版商").grid(row=0, column=0, columnspan=2)
        tk.Button(self.puber_frame, text="+", command=self.search_add_puber).grid(row=1,column=0)
        tk.Button(self.puber_frame, text='-', command=self.search_remove_puber).grid(row=1, column=1)
        # 期刊输入
        self.search_puber_input_list = []
        self.search_puber_input_list.append( ttk.Combobox(self.puber_frame, values=self.all_puber_list) )
        self.search_puber_input_list[0].grid(row=0, column=2)
        # 按关键词搜索
        self.keyword_frame = tk.Frame(self.search_frame)
        self.keyword_frame.grid(row=4,column=0, sticky='we')
        tk.Label(self.keyword_frame, text='含关键词').grid(row=0, column=0)
        # 关键词搜索模式
        self.search_flag = tk.IntVar()    # 标记从论文标题中搜索
        self.search_flag.set(1)
        tk.Radiobutton(self.keyword_frame, text='仅标题',variable=self.search_flag, value=1).grid(row=1, column=0)
        tk.Radiobutton(self.keyword_frame, text='仅备注',variable=self.search_flag, value=2).grid(row=2, column=0)
        tk.Radiobutton(self.keyword_frame, text='标题+备注',variable=self.search_flag, value=3).grid(row=3, column=0)
        # 搜索内容
        self.search_keyword_input_entry = tk.Entry(self.keyword_frame)
        self.search_keyword_input_entry.grid(row=0, column=1)

        # 搜索按钮
        tk.Button(self.search_frame, text="筛选", width=20, height=4, command=self.search_paper).grid(row=5, column=0, sticky='we')
        tk.Button(self.search_frame,text="重置", width=20, height=2, command=self.resume_paper).grid(row=6, column=0, sticky='we') 
        tk.Button(self.search_frame,text="重置", width=20, height=2, command=self.resume_paper).grid(row=8, column=0, sticky='we') 

        # 文献列表显示主体
        self.show_frame.config(bd='1p')
        self.show_frame.grid_rowconfigure(0, weight=1)
        self.show_frame.grid_columnconfigure(0, weight=1)
        # 显示表
        self.show_table = ttk.Treeview(self.show_frame, columns=DataBase.SIMPLE_FIELD_LIST, selectmode='extended', show='headings')
        i = 0
        colunm_width_list = [100,120,130,150,700,400]
        for item in DataBase.SIMPLE_FIELD_LIST:
            self.show_table.column(item,anchor='w', stretch=0, width=colunm_width_list[i])
            i += 1
            self.show_table.heading(item,text=item)
        self.paper_list = search(self)
        i = 0
        for item in self.paper_list:
            val = []
            for tem in DataBase.SIMPLE_FIELD_LIST:
                val.append(item.get(tem))
            self.show_table.insert('', i, values=val, iid=str(item.get("No")) )
        self.show_table.bind("<Double-1>", lambda event:open_edit_ui(event, self, self.show_table.selection()[0]))
        self.show_table.grid(row=0, column=0, sticky='eswn')
        # 垂直滚动条
        self.show_table_ybar = ttk.Scrollbar(self.show_frame, orient=VERTICAL,command=self.show_table.yview)
        self.show_table.configure(yscrollcommand=self.show_table_ybar.set)
        self.show_table_ybar.grid(row=0, column=1, sticky='ns')
        # 水平滚动条
        self.show_table_xbar = ttk.Scrollbar(self.show_frame, orient=HORIZONTAL,command=self.show_table.xview)
        self.show_table.configure(xscrollcommand=self.show_table_xbar.set)
        self.show_table_xbar.grid(row=1, column=0, columnspan=2, sticky='ew')

        # 主循环
        self.root.mainloop()

        return None
    
    


    def search_add_tag(self):
        # 在搜索面板添加tag搜索条件输入框
        # 仅UI操作
        self.search_tag_input_list.append(ttk.Combobox(self.tag_frame, values=self.all_tag_list))
        self.search_tag_input_list[-1].grid(row=len(self.search_tag_input_list)-1, column=2)

        return None

    def search_remove_tag(self):
        # 在搜索面板去除tag搜索条件输入框
        # 仅UI操作
        if(len(self.search_tag_input_list) <= 0):
            return None
        else:
            self.search_tag_input_list[-1].grid_forget()
            self.search_tag_input_list.pop()
        
        return None

    def search_add_puber(self):
        # 在搜索面板添加puber搜索条件输入框
        # 仅UI操作
        self.search_puber_input_list.append(ttk.Combobox(self.puber_frame, values=self.all_puber_list))
        self.search_puber_input_list[-1].grid(row=len(self.search_puber_input_list)-1, column=2)

        return None

    def search_remove_puber(self):
        # 在搜索面板去除tag搜索条件输入框
        # 仅UI操作
        if(len(self.search_puber_input_list) <= 0):
            return None
        else:
            self.search_puber_input_list[-1].grid_forget()
            self.search_puber_input_list.pop()
        
        return None

    def table_renewer(self):
        # 使用现有查询条件更新table
        self.paper_list = search(self, self.filter)
        
        for item in self.show_table.get_children():
            self.show_table.delete(item)

        i = 0
        for item in self.paper_list:
            val = []
            for tem in DataBase.SIMPLE_FIELD_LIST:
                val.append(item.get(tem))
            self.show_table.insert('', i, values=val, iid=str(item.get("No")) )
        return

    def search_renewer(self):
        # 更新查找词条
        self.all_tag_list = self.m_db.get_all_tags()
        self.all_puber_list = self.m_db.get_all_pub()
        for item in self.search_tag_input_list:
            item.configure(values = self.all_tag_list)
        for item in self.search_puber_input_list:
            item.configure(values = self.all_puber_list)
        return MY_SUCCESS

    def search_paper(self):
        # 更新筛选器，更新筛选结果
        # pubyear_begin pubyear_end puber_list tag_list keyword
        # keyword_flag

        # self.paper_list = []    # 当前展示的paper
        # self.filter # 筛选条件
        loc_filter = {}

        # 更新发表年份筛选条件
        if self.pubyear_begin_entry.get() != "":
            try:
                pubyear_begin = int(self.pubyear_begin_entry.get())
                print(self.pubyear_begin_entry.get())
                loc_filter["pubyear_begin"] = pubyear_begin
            except:
                showerror("Failed", "发表起始年份错误：请输入自然数")
                return
            
        if self.pubyear_end_entry.get() != "":
            try:
                pubyear_end = int(self.pubyear_end_entry.get())
                loc_filter["pubyear_end"] = pubyear_end
            except:
                showerror("Failed", "发表结束年份错误：请输入自然数")
                return
        # 更新标签筛选条件
        loc_tag_list = []
        for item in self.search_tag_input_list:
            if item.get() != "":
                loc_tag_list.append(item.get())
        if loc_tag_list != []:
            loc_filter['tag_list'] = loc_tag_list
        # 更新出版商筛选条件
        loc_puber_list = []
        for item in self.search_puber_input_list:
            if item.get() != "":
                loc_puber_list.append(item.get())
        if loc_puber_list != "":
            loc_filter['puber_list'] = loc_puber_list
        # 更新关键词筛选条件
        if self.search_keyword_input_entry.get() != "":
            loc_filter["keyword"] = self.search_keyword_input_entry.get()
        
            if self.search_flag.get() == 1 or self.search_flag.get() == 2 or self.search_flag.get() == 3:
                loc_filter["keyword_flag"] = self.search_flag.get()
        # 更新self.filter
        if loc_filter!={}:
            self.filter = copy.deepcopy(loc_filter)
            self.table_renewer()

    def resume_paper(self):
        # 重置筛选条件，重置搜索结果
        self.pubyear_begin_entry.delete(0,"end")
        self.pubyear_end_entry.delete(0,'end')
        while(len(self.search_tag_input_list)>0):
            self.search_remove_tag()
        self.search_add_tag()
        while(len(self.search_puber_input_list)>0):
            self.search_remove_puber()
        self.search_add_puber()
        self.search_flag.set(1)
        self.search_keyword_input_entry.delete(0, "end")

        self.filter = {}
        self.table_renewer()
        pass
            
    def get_setting(self):
        # 获取设置文件
        conf = configparser.ConfigParser()
        if not os.path.isfile(SETTING_PATH):
            conf.add_section("default")
            conf.set("default","pdf_reader", "D:\\tools\\Foxit\\FoxitPhantomPDF.exe")
            conf.write(open(SETTING_PATH, "w"))
        else:
            conf.read(SETTING_PATH, encoding="utf-8")
        self.m_conf = copy.deepcopy(conf)
        return




def search(ui:TkUI, info:dict={}):
    # 使用ui.m_db搜索条目
    if (info == {}):
        # 返回全部paper
        return ui.m_db.show_all_paper()
    else:
        return ui.m_db.find_paper(info)




def do_nothing(ui:TkUI):
    def add_paper():
        # 添加按钮的功能函数
        # 获取文献信息并将文献添加到数据库
        paper_dict = {}
        if publication_year_text.get(1.0,'end').rstrip() != "":
            try:
                paper_dict['PublicationYear'] = int(publication_year_text.get(1.0,'end').rstrip())
            except:
                showerror("Failed", "文献发表年份必须为整数")
                return
        paper_dict['Publisher'] = publisher_text.get(1.0,'end').rstrip()
        if publisher_text.get(1.0,'end').rstrip() == "":
            showerror("Failed", "会议名不能为空")
            return 
        
        # 更新显示信息
        # print(paper_dict)
        ui.m_db.add_paper(paper_dict)
        ui.table_renewer()
        ui.search_renewer()
        
        add_root.destroy()
        return

    # 添加文献界面主窗口
    add_root = tk.Toplevel(ui.root)
    add_root.geometry('600x200')
    add_root.resizable(True, True)
    add_root.title("爬取paper")
    add_root.protocol("WM_DELETE_WINDOW",add_root.destroy)
    add_root.wm_attributes('-topmost',1)
    # 主窗口划分
    add_root.grid_rowconfigure(1, weight=1)
    add_root.grid_columnconfigure(0, weight=1)
    button_frame = tk.Frame(add_root) # 按钮区
    button_frame.grid(row=0, column=0, columnspan=2 ,sticky='new')
    add_canvas = tk.Canvas(add_root) # 添加区
    add_canvas.bind('<Configure>', lambda event: add_canvas.config(scrollregion=add_canvas.bbox('all')))
    add_canvas.grid(row=1, column=0, sticky='ewns')
    # 添加区主体
    add_frame = tk.Frame(add_canvas) 
    add_canvas.create_window((0,0), window=add_frame, anchor='n')
    # 修改区滚动条
    ybar = ttk.Scrollbar(add_root,orient=VERTICAL,command=add_canvas.yview)
    ybar.configure(command=add_canvas.yview)
    add_canvas.configure(yscrollcommand=ybar.set)
    ybar.grid(row=1, column = 1, sticky='ns')

    # 在按钮区添加按钮
    add_button = tk.Button(button_frame)
    add_button.config(text='爬取', command=lambda:call_API(), state='normal')
    add_button.grid(row=0, column=0)


    # 添加区
    # PublicationYear
    publication_year_label = tk.Label(add_frame, text="发表年份：")
    publication_year_label.grid(row=3,column=0)
    publication_year_text = tk.Text(add_frame, height=1,width=10)
    publication_year_text.config(state='normal', bg='#ffffff')
    publication_year_text.grid(row=4,column=0)
    # Publisher
    publisher_label = tk.Label(add_frame, text="会议：")
    publisher_label.grid(row=5,column=0)
    publisher_text = tk.Text(add_frame, height=1)
    publisher_text.config(state='normal', bg='#ffffff')
    publisher_text.grid(row=6,column=0)

 
    
    def call_API():
        year_num = int(publication_year_text.get(1.0,'end').rstrip())
        publication_year_start = str(year_num)
        publication_year__end = str(year_num+1)
        publisher = (publisher_text.get(1.0,'end').rstrip())
 
        os.system('cd crawl_API && python run.py -c {0} -s {1} -e {2}'.format(publisher,publication_year_start,publication_year__end))
        #print('cd crawl_API && python run.py -c {0} -s {1} -e {2}'.format(publisher,publication_year_start,publication_year__end))
        








def open_add_ui(ui:TkUI):
    # 添加文献界面的实现函数

    def add_paper():
        # 添加按钮的功能函数
        # 获取文献信息并将文献添加到数据库
        paper_dict = {}
        if publication_year_text.get(1.0,'end').rstrip() != "":
            try:
                paper_dict['PublicationYear'] = int(publication_year_text.get(1.0,'end').rstrip())
            except:
                showerror("Failed", "文献发表年份必须为整数")
                return
        paper_dict['Publisher'] = publisher_text.get(1.0,'end').rstrip()
        paper_dict['Author'] = author_text.get(1.0,'end').rstrip()
        if paper_name_text.get(1.0,'end').rstrip() == "":
            showerror("Failed", "文献名不能为空")
            return 
        paper_dict['PaperName'] = paper_name_text.get(1.0,'end').rstrip()
        paper_dict['Url'] = url_text.get(1.0,'end').rstrip()
        paper_dict['Path'] = path_text.get(1.0,'end').rstrip() 
        
        # 更新显示信息
        # print(paper_dict)
        ui.m_db.add_paper(paper_dict)
        ui.table_renewer()
        ui.search_renewer()
        
        add_root.destroy()
        return

    # 添加文献界面主窗口
    add_root = tk.Toplevel(ui.root)
    add_root.geometry('750x400')
    add_root.resizable(True, True)
    add_root.title("Add Paper")
    add_root.protocol("WM_DELETE_WINDOW",add_root.destroy)
    add_root.wm_attributes('-topmost',1)
    # 主窗口划分
    add_root.grid_rowconfigure(1, weight=1)
    add_root.grid_columnconfigure(0, weight=1)
    button_frame = tk.Frame(add_root) # 按钮区
    button_frame.grid(row=0, column=0, columnspan=2 ,sticky='new')
    add_canvas = tk.Canvas(add_root) # 添加区
    add_canvas.bind('<Configure>', lambda event: add_canvas.config(scrollregion=add_canvas.bbox('all')))
    add_canvas.grid(row=1, column=0, sticky='ewns')
    # 添加区主体
    add_frame = tk.Frame(add_canvas) 
    add_canvas.create_window((0,0), window=add_frame, anchor='n')
    # 修改区滚动条
    ybar = ttk.Scrollbar(add_root,orient=VERTICAL,command=add_canvas.yview)
    ybar.configure(command=add_canvas.yview)
    add_canvas.configure(yscrollcommand=ybar.set)
    ybar.grid(row=1, column = 1, sticky='ns')

    # 在按钮区添加按钮
    add_button = tk.Button(button_frame)
    add_button.config(text='Add', command=add_paper, state='normal')
    add_button.grid(row=0, column=0)

    # 添加区
    # PublicationYear
    publication_year_label = tk.Label(add_frame, text="发表年份：")
    publication_year_label.grid(row=3,column=0)
    publication_year_text = tk.Text(add_frame, height=1)
    publication_year_text.config(state='normal', bg='#ffffff')
    publication_year_text.grid(row=4,column=0)
    # Publisher
    publisher_label = tk.Label(add_frame, text="出版商：")
    publisher_label.grid(row=5,column=0)
    publisher_text = tk.Text(add_frame, height=1)
    publisher_text.config(state='normal', bg='#ffffff')
    publisher_text.grid(row=6,column=0)
    # Author
    author_label = tk.Label(add_frame, text="作者：")
    author_label.grid(row=7,column=0)
    author_text = tk.Text(add_frame, height=1)
    author_text.config( state='normal', bg='#ffffff')
    author_text.grid(row=8,column=0)
    # PaperName
    paper_name_label = tk.Label(add_frame, text="论文名：")
    paper_name_label.grid(row=9,column=0)
    paper_name_text = tk.Text(add_frame, height=3)
    paper_name_text.config( state='normal', bg='#ffffff')
    paper_name_text.grid(row=10,column=0)
    # Url
    url_label = tk.Label(add_frame, text="网页链接：")
    url_label.grid(row=15,column=0)
    url_text = tk.Text(add_frame, height=1)
    url_text.config(state='normal', bg='#ffffff')
    url_text.grid(row=16,column=0)
    # Path
    def path_button_func():
        add_root.wm_attributes('-topmost',0)
        path_info = filedialog.askopenfilename(
            title = "选择本地pdf文件",
            initialdir='.',
            filetypes = [('PDF','*.pdf')]
        ).replace('/','\\')
        path_text.delete(1.0,tk.END)
        path_text.insert('end', str(path_info))
        add_root.wm_attributes('-topmost',1)
        return
    path_frame = tk.Frame(add_frame)
    path_frame.grid(row=17, column=0)
    path_label = tk.Label(path_frame, text="本地目录：",height=2)
    path_label.grid(row=0,column=0, sticky="we")
    path_button = tk.Button(path_frame, text="Select", command=path_button_func)
    path_button.grid(row=0, column=1)
    path_text = tk.Text(add_frame, height=1)
    path_text.config(state='normal', bg='#ffffff')
    path_text.grid(row=18,column=0)

    add_root.mainloop()


def open_edit_ui(event, ui:TkUI, paper_no:str):

    # 函数定义：
    def begin_edit_paper():
        # edit 按钮的响应函数，修改按钮状态
        edit_button.config(state='disable')
        save_button.config(state='normal')
        del_button.config(state='normal')

        read_or_not_button.config(state='normal', bg='#e8f0fe')
        publication_year_text.config(state='normal', bg='#e8f0fe')
        publisher_text.config(state='normal', bg='#e8f0fe')
        author_text.config(state='normal', bg='#e8f0fe')
        paper_name_text.config(state='normal', bg='#e8f0fe')
        tags_text.config(state='normal', bg='#e8f0fe')
        notes_text.config(state='normal', bg='#e8f0fe')
        url_text.config(state='normal', bg='#e8f0fe')
        path_button.config(state='normal')
        path_text.config(state='normal', bg='#e8f0fe')
        last_read_date_text.config(state='normal', bg='#e8f0fe')
        for i in range(10):
            q_text_list[i].config(state='normal', bg='#e8f0fe')

    def edit_paper():
        # save 按钮的响应函数
        # 读取并保存文献信息
        edit_button.config(state='normal')
        save_button.config(state='disable')
        del_button.config(state='disable')

        read_or_not_button.config(state='disable', bg='#ffffff')
        publication_year_text.config(state='disable', bg='#ffffff')
        publisher_text.config(state='disable', bg='#ffffff')
        author_text.config(state='disable', bg='#ffffff')
        paper_name_text.config(state='disable', bg='#ffffff')
        tags_text.config(state='disable', bg='#ffffff')
        notes_text.config(state='disable', bg='#ffffff')
        url_text.config(state='disable', bg='#ffffff')
        path_button.config(state='disable')
        path_text.config(state='disable', bg='#ffffff')
        last_read_date_text.config(state='disable', bg='#ffffff')
        for i in range(10):
            q_text_list[i].config(state='disable', bg='#ffffff')

        paper_dict['ReadOrNot'] = read_or_not_button_val.get()
        if publication_year_text.get(1.0,'end').rstrip() != "":
            try:
                paper_dict['PublicationYear'] = int(publication_year_text.get(1.0,'end').rstrip())
            except:
                showerror("Failed", "文献发表年份必须为整数")
        paper_dict['Publisher'] = publisher_text.get(1.0,'end').rstrip()
        paper_dict['Author'] = author_text.get(1.0,'end').rstrip()
        if paper_name_text.get(1.0,'end').rstrip() == "":
            showerror("Failed","文献名不能为空")
            return
        paper_dict['PaperName'] = paper_name_text.get(1.0,'end').rstrip()
        paper_dict['Tags'] = tags_text.get(1.0,'end').rstrip()
        paper_dict['Notes'] = notes_text.get(1.0,'end').rstrip()
        paper_dict['Url'] = url_text.get(1.0,'end').rstrip()
        paper_dict['Path'] = path_text.get(1.0,'end').rstrip()
        for i in range(10):
            paper_dict['Q'+str(i)] = q_text_list[i].get(1.0,'end').rstrip()

        # 更新显示        
        ui.m_db.modi_paper(paper_dict)
        ui.search_renewer()
        ui.table_renewer()

        return

    def del_paper():
        # delete 按钮的响应函数
        # 删除文献
        dic = {"No":paper_no}
        ui.m_db.del_paper(dic)
        ui.search_renewer()
        ui.table_renewer()

        edit_root.destroy()
        pass

    def open_paper():
        # 通过路径使用pdf阅读器打开文件
        pdf_reader = ui.m_conf.get('default', "pdf_reader")
        if not os.path.isfile(pdf_reader):
            showerror("failed", "pdf阅读器目录错误")
        file_path = path_text.get(1.0,'end').rstrip()
        if not os.path.isfile(file_path):
            showerror("failed", "目标文件pdf目录错误")
            return
        
        pdf_temp = copy.deepcopy(pdf_reader)
        pdf_exe = pdf_temp.split('\\')[-1]
        pdf_path = pdf_reader.rstrip(pdf_exe)
        print(f"{pdf_reader} \"{file_path}\"\n{pdf_exe} {pdf_path}\n" )
        subprocess.Popen([f"{pdf_exe}",f"\"{file_path}\""], shell=True, cwd = pdf_path)
        return
        

    # 正式开始
    paper_dict = {}
    # 查找对应文献
    for item in ui.paper_list:
        if (str(item.get("No"))==paper_no):
            # paper_dict = copy.deepcopy(item)
            paper_dict = item
            break

    # 修改窗口主窗口
    edit_root = tk.Toplevel(ui.root)
    edit_root.geometry('770x800')
    edit_root.resizable(True, True)
    edit_root.title("Paper: "+str(paper_dict.get("PaperName")))
    edit_root.protocol("WM_DELETE_WINDOW",edit_root.destroy)
    edit_root.grid_rowconfigure(1, weight=1)
    edit_root.grid_columnconfigure(0, weight=1)
    button_frame = tk.Frame(edit_root) # 按钮区
    button_frame.grid(row=0, column=0, columnspan=2 ,sticky='new')

    # 修改区
    edit_canvas = tk.Canvas(edit_root)
    edit_canvas.bind('<Configure>', lambda event: edit_canvas.config(scrollregion=edit_canvas.bbox('all')))
    edit_canvas.grid(row=1, column=0, sticky='ewns')
    # 修改区主体
    edit_frame = tk.Frame(edit_canvas) 
    edit_canvas.create_window((0,0), window=edit_frame, anchor='n')
    # 修改区滚动条
    ybar = ttk.Scrollbar(edit_root,orient=VERTICAL,command=edit_canvas.yview)
    ybar.configure(command=edit_canvas.yview)
    edit_canvas.configure(yscrollcommand=ybar.set)
    ybar.grid(row=1, column = 1, sticky='ns')

    # 在按钮区添加按钮
    open_button = tk.Button(button_frame)
    open_button.config(text='open', command=open_paper, state = 'normal')
    open_button.pack(side='right')
    save_button = tk.Button(button_frame)
    save_button.config(text='save', command=edit_paper, state = 'disable')
    save_button.pack(side='right')
    edit_button = tk.Button(button_frame)
    edit_button.config(text='edit', command=begin_edit_paper, state='normal')
    edit_button.pack(side='right')
    del_button = tk.Button(button_frame)
    del_button.config(text='delete', command=del_paper, state = 'disable')
    del_button.pack(side='left')

    # 在修改区添加
    # No 序号
    no_label = tk.Label(edit_frame, text="Paper Local No: "+paper_no)
    no_label.grid(row=0,column=0)
    # ReadOrNot 标识
    read_or_not_button_val = tk.IntVar()
    read_or_not_button_val.set(int(paper_dict.get("ReadOrNot")))
    read_or_not_button = tk.Checkbutton(edit_frame,variable=read_or_not_button_val, text="阅读标记：",height=1, onvalue=1, offvalue=0)
    read_or_not_button.config(state='disable', bg='#ffffff')
    read_or_not_button.grid(row=2,column=0)
    # PublicationYear
    publication_year_label = tk.Label(edit_frame, text="发表年份：")
    publication_year_label.grid(row=3,column=0)
    publication_year_text = tk.Text(edit_frame, height=1)
    publication_year_text.insert('end',str(paper_dict.get("PublicationYear")))
    publication_year_text.config(state='disable', bg='#ffffff')
    publication_year_text.grid(row=4,column=0)
    # Publisher
    publisher_label = tk.Label(edit_frame, text="出版商：")
    publisher_label.grid(row=5,column=0)
    publisher_text = tk.Text(edit_frame, height=1)
    publisher_text.insert('end',str(paper_dict.get("Publisher")))
    publisher_text.config(state='disable', bg='#ffffff')
    publisher_text.grid(row=6,column=0)
    # Author
    author_label = tk.Label(edit_frame, text="作者：")
    author_label.grid(row=7,column=0)
    author_text = tk.Text(edit_frame, height=1)
    author_text.insert('end',str(paper_dict.get("Author")))
    author_text.config( state='disable', bg='#ffffff')
    author_text.grid(row=8,column=0)
    # PaperName
    paper_name_label = tk.Label(edit_frame, text="论文名：")
    paper_name_label.grid(row=9,column=0)
    paper_name_text = tk.Text(edit_frame, height=3)
    paper_name_text.insert('end',str(paper_dict.get("PaperName")))
    paper_name_text.config( state='disable', bg='#ffffff')
    paper_name_text.grid(row=10,column=0)
    # Tages
    tags_label = tk.Label(edit_frame, text="标签：")
    tags_label.grid(row=11,column=0)
    tags_text = tk.Text(edit_frame, height=1)
    tags_text.insert('end',str(paper_dict.get("Tags")))
    tags_text.config(state='disable', bg='#ffffff')
    tags_text.grid(row=12,column=0)
    # Notes
    notes_label = tk.Label(edit_frame, text="备注：")
    notes_label.grid(row=13,column=0)
    notes_text = tk.Text(edit_frame, height=1)
    notes_text.insert('end',str(paper_dict.get("Notes")))
    notes_text.config(state='disable', bg='#ffffff')
    notes_text.grid(row=14,column=0)
    # Url
    url_label = tk.Label(edit_frame, text="网页链接：")
    url_label.grid(row=15,column=0)
    url_text = tk.Text(edit_frame, height=1)
    url_text.insert('end',str(paper_dict.get("Url")))
    url_text.config(state='disable', bg='#ffffff')
    url_text.grid(row=16,column=0)
    # Path
    def path_button_func():
        path_info = filedialog.askopenfilename(
            title = "选择本地pdf文件",
            initialdir='.',
            filetypes = [('PDF','*.pdf')]
        ).replace('/','\\')
        path_text.delete(1.0,tk.END)
        path_text.insert('end', str(path_info))
        edit_root.wm_attributes('-topmost',1)
        edit_root.wm_attributes('-topmost',0)
        return
    path_frame = tk.Frame(edit_frame)
    path_frame.grid(row=17, column=0)
    path_label = tk.Label(path_frame, text="本地目录：",height=2)
    path_label.grid(row=0,column=0, sticky="we")
    path_button = tk.Button(path_frame, text="Select", command=path_button_func, state='disable')
    path_button.grid(row=0, column=1)
    path_text = tk.Text(edit_frame, height=1)
    path_text.insert('end',str(paper_dict.get("Path")))
    path_text.config(state='disable', bg='#ffffff')
    path_text.grid(row=18,column=0)
    # LastReadDate
    last_read_date_label = tk.Label(edit_frame, text="上次阅读的时间：")
    last_read_date_label.grid(row=19,column=0)
    last_read_date_text = tk.Text(edit_frame, height=1)
    last_read_date_text.insert('end',str(paper_dict.get("LastReadDate")))
    last_read_date_text.config(state='disable', bg='#ffffff')
    last_read_date_text.grid(row=20,column=0)
    # 10Q
    q_label_list = []
    q_text_list = []
    for i in range(10):
        q_label_list.append(tk.Label(edit_frame, text='Q'+str(i)+Q_TEXT[i]))
        q_label_list[-1].grid(row=21+2*i, column=0)
        q_text_list.append(ScrolledText(edit_frame, height=10))
        q_text_list[-1].insert('end',str(paper_dict.get("Q"+str(i))))
        q_text_list[-1].configure(state='disable', bg='#ffffff')
        q_text_list[-1].grid(row=21+2*i+1, column=0)
    
    edit_root.mainloop()

    
    
def open_setting_ui(ui:TkUI):
    # 主窗口菜单栏设置按钮响应函数

    def begin_edit_setting():
        # edit 按钮响应函数
        pdf_path_entry.configure(state='normal', bg='#e8f0fe')
        edit_button.configure(state='disable')
        save_button.configure(state='normal')
        resume_button.configure(state='normal')
        pdf_path_button.configure(state='normal')
        pass

    def edit_setting():
        # save 按钮响应函数
        # 保存设置信息
        pdf_path = pdf_path_entry.get()
        print(pdf_path)
        ui.m_conf.set("default", "pdf_reader", pdf_path)
        ui.m_conf.write(open(SETTING_PATH, "w", encoding='utf-8'))

        pdf_path_entry.configure(state='disable', bg='#ffffff')
        edit_button.configure(state='normal')
        save_button.configure(state='disable')
        resume_button.configure(state='disable')
        pdf_path_button.configure(state='disable')
        pass

    def resume_setting():
        # resume按钮响应函数
        # 删除原有设置，恢复默认设置
        try: 
            os.remove(SETTING_PATH) 
        except:
            pass
        ui.get_setting()

        pdf_path_entry.delete(0,'end')
        pdf_path_entry.insert('end',ui.m_conf.get("default","pdf_reader"))
        pdf_path_entry.configure(state='disable', bg='#ffffff')
        edit_button.configure(state='normal')
        save_button.configure(state='disable')
        resume_button.configure(state='disable')
        pdf_path_button.configure(state='disable')
        pass

    def backup():
        # print(["copy", os.path.join(os.getcwd(),DataBase.DB_REL_PATH),os.path.join(os.getcwd(),DataBase.DB_REL_PATH+".backup")])
        try:
            subprocess.Popen(["copy", DataBase.DB_REL_PATH, DataBase.DB_REL_PATH+".backup" ], shell=True)
        except:
            return
        showinfo("Succeed","备份成功")
        return MY_SUCCESS

    # 设置窗口主函数
    setting_root = tk.Toplevel(ui.root)
    setting_root.geometry('770x400')
    setting_root.resizable(True, True)
    setting_root.title("Setting")
    setting_root.protocol("WM_DELETE_WINDOW",setting_root.destroy)
    setting_root.wm_attributes('-topmost',1)

    setting_root.grid_rowconfigure(1, weight=1)
    setting_root.grid_columnconfigure(0, weight=1)
    button_frame = tk.Frame(setting_root) # 按钮区
    button_frame.grid(row=0, column=0, columnspan=2 ,sticky='new')

    # 修改区
    edit_canvas = tk.Canvas(setting_root)
    edit_canvas.bind('<Configure>', lambda event: edit_canvas.config(scrollregion=edit_canvas.bbox('all')))
    edit_canvas.grid(row=1, column=0, sticky='ewns')
    # 修改区主体
    edit_frame = tk.Frame(edit_canvas) 
    edit_canvas.create_window((0,0), window=edit_frame, anchor='n')
    # 修改区滚动条
    ybar = ttk.Scrollbar(setting_root,orient=VERTICAL,command=edit_canvas.yview)
    ybar.configure(command=edit_canvas.yview)
    edit_canvas.configure(yscrollcommand=ybar.set)
    ybar.grid(row=1, column = 1, sticky='ns')

    # 在按钮区添加按钮
    edit_button = tk.Button(button_frame)
    edit_button.config(text='edit', command=begin_edit_setting, state='normal')
    edit_button.pack(side='left')
    save_button = tk.Button(button_frame)
    save_button.config(text='save', command=edit_setting, state = 'disable')
    save_button.pack(side='left')
    resume_button = tk.Button(button_frame)
    resume_button.config(text='default', command=resume_setting, state = 'disable')
    resume_button.pack(side='left')

    # 添加修改的设置内容
    def pdf_path_button_func():
        setting_root.wm_attributes('-topmost',0)
        filepath = filedialog.askopenfilename(
            title = "选择pdf阅读器",
            initialdir='.',
            filetypes = [('Exe','*.exe')]
        ).replace('/','\\')
        if filepath != "":
            pdf_path_entry.delete(0,"end")
            pdf_path_entry.insert('end',filepath)
        setting_root.wm_attributes('-topmost',1)
        pass

    tk.Label(edit_canvas, text="pdf阅读器位置（推荐福昕pdf阅读器）：").pack()
    pdf_path_button = tk.Button(edit_canvas, text="Select", command=pdf_path_button_func, state='disable')
    pdf_path_button.pack(pady=0.5)
    pdf_path_entry = tk.Entry(edit_canvas, width= 80)
    pdf_path_entry.insert('end',ui.m_conf.get("default","pdf_reader"))
    pdf_path_entry.configure(state='disable')
    pdf_path_entry.pack()
    # print(ui.m_conf.get("default","pdf_reader"))
    tk.Label(edit_canvas, text="备份数据库文件").pack()
    back_button = tk.Button(edit_canvas, text="Backup", command=backup)
    back_button.pack()

    setting_root.mainloop()

    return None

