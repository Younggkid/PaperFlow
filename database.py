import sqlite3,os



# 定义本地文献数据库类
class DataBase:
    # 定义表格属性
    FIELD_LIST = ["Num", "PaperTitle", "Author", "YearofPublish", "Conference", "Tags",
                   "LastReadDate", "URL", "Q1", "Q2", "Q3", "Q4", "Q5",
                  ]
    # 定义数据库位置（相对）
    DB_REL_PATH = "database.db"
    # 构造函数生成空数据库并提供连接
    def __init__(self) -> None:
        self.con = None
        # 如果已有数据库则连接已有数据库，没有则创建新的数据库

        if os.path.isfile(DataBase.DB_REL_PATH):
            self.con = sqlite3.connect(DataBase.DB_REL_PATH)
        else:
            self.con = sqlite3.connect(DataBase.DB_REL_PATH)
            init_text = '''CREATE TABLE PAPERS(
            Num INT PRIMARY KEY AUTOINCREMENT,
            PaperTitle TEXT,
            Author TEXT,
            YearofPublish INT,
            Conference TEXT,
            Tags TEXT,
            LastReadDate TEXT,
            URL TEXT,
            Q1  TEXT,
            Q2  TEXT,
            Q3  TEXT,
            Q4  TEXT,
            Q5  TEXT,
            );'''
            self.con.execute(init_text)
            self.con.commit()
        
        self.con.close()
        return None
# TODO:接受字典，插入数据
def add_data(self, info:dict):
    pass
    
# TODO:接受字典，更改数据
def modi_data(self, info:dict):
    pass

#TODO:接受字典，删除数据
def modi_data(self, info:dict):
    pass

#TODO : 或根据主键删除
def modi_data_num(self, num:int):
    pass

# TODO:展示所有paper
def show_all_paper(self):
    pass

#TODO: 查找某个paper
def search_paper(self, info:dict):
    pass

#TODO: 批量加入大量paper，调用爬虫API
def batch_add_data(self):
    pass
