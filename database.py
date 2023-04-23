import sqlite3,os,copy
MY_SUCCESS = 1
MY_ERROR_NO_PAPERNO = 0


# 定义本地文献数据库类
class DataBase:
    # 定义表格属性
    FIELD_LIST = ["No", "ReadOrNot", "YearofPublish", "PaperTitle", "Author",  "Conference", "Tags",
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
            No INTEGER PRIMARY KEY AUTOINCREMENT,
            ReadOrNot INT,
            YearofPublish INT,
            PaperTitle TEXT,
            Author TEXT,
            Conference TEXT,
            Tags TEXT,
            LastReadDate TEXT,
            URL TEXT,
            Q1  TEXT,
            Q2  TEXT,
            Q3  TEXT,
            Q4  TEXT,
            Q5  TEXT
            );'''
            self.con.execute(init_text)
            self.con.commit()
        
       # self.con.close()
        return None
    

# TODO:接受字典，插入数据
    def add_data(self, info:dict):
        fields = "ReadOrNot"  # 字段
        values = "0"  # 值

        add_fields = copy.deepcopy(DataBase.FIELD_LIST)
        add_fields.remove("No")
        add_fields.remove("ReadOrNot")
        add_fields.remove("YearofPublish")

        if info.get("YearofPublish"):
            fields += "," + "YearofPublish"
            values += "," + str(info.get("YearofPublish"))
        for item in add_fields:
            if info.get(item):
                fields += "," + item
                values += ",\"" + str(info.get(item)) + "\""
            else:
                fields += "," + item
                values += ",\"\""

        self.con.execute(f'''
            insert into PAPERS ({fields}) values ({values});     
            ''')
        self.con.commit()
        
        return MY_SUCCESS
        
    # TODO:接受字典，更改数据
    def modi_data(self, info:dict):
        update = ""

        no = info.get("No")
        
        if not no:
            return MY_ERROR_NO_PAPERNO
            
        
        modi_fields = copy.deepcopy(DataBase.FIELD_LIST)
        modi_fields.remove("No")
        modi_fields.remove("ReadOrNot")
        modi_fields.remove("YearofPublish")
        print(update,no)
        # 依次读取待修改的属性
        if info.get("ReadOrNot"):
            update += "ReadOrNot=" + str(info.get("ReadOrNot")) + ","
        if info.get("YearofPublish"):
            update += "YearofPublish=" + str(info.get("YearofPublish")) + ","
        for item in modi_fields:
            if info.get(item):
                update += item + "=\"" + info.get(item) + "\","
        # 删除最后多余的 ,
        try:
            if update[-1] == ",":
                update = update[:-1]
        except:
            pass
            
        print(update,no)
        self.con.execute(f'''
            UPDATE PAPERS
            SET {update}
            WHERE No = {no};
        ''')
        self.con.commit()

        return MY_SUCCESS

    #TODO:接受字典，删除数据
    def del_data(self, info:dict):
        pass

    #TODO : 或根据主键删除
    def modi_data_no(self, no:int):
        pass

    # TODO:展示所有paper
    def show_all_paper(self):
        ret_list = list(self.con.execute('''
                select * from PAPERS
                ORDER BY YearofPublish, PaperTitle  DESC;
                '''))
 
        print("下面是所有论文")
        print(ret_list)
        return ret_list
    

    #TODO: 查找某个paper
    def search_paper(self, info:dict):
        pass

    #TODO: 批量加入大量paper，调用爬虫API
    def batch_add_data(self):
        pass
