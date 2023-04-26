import sqlite3, os, copy

from globalvar import *




def dict_factory(cursor, row):
    # 将元组类型转换为字典类型
    # 主要用来将sqlite库查询的结果转换为dict类型

    d = {}  
    for idx, col in enumerate(cursor.description):  
        d[col[0]] = row[idx]  
    return d  


class DataBase:

    # 文献的全部字段
    FIELD_LIST = ["No",   "ReadOrNot",   "PublicationYear",  "Publisher",  
        "Author",   'PaperName',      "Tags",      "Notes",
        "Url",            "Path",               'LastReadDate',
        "Q0",     "Q1",     "Q2",     "Q3",     "Q4",
        "Q5",     "Q6",     "Q7",     "Q8",     "Q9"  
        ]
    
    SIMPLE_FIELD_LIST = ["ReadOrNot",   "PublicationYear", "Publisher",  
        "Author",   'PaperName',      "Tags",
        ]

    DB_REL_PATH = "database.db"

    def __init__(self):
        # 初始化函数，生成并连接数据库

        # 声明全部变量的名称
        self.m_con = None    # 数据库接口        
        
        # 测试用，每次删库跑路
        # try: 
        #     os.remove(rel_path) 
        # except:
        #     pass

        # 检查数据库文件是否存在
        if os.path.isfile(DataBase.DB_REL_PATH):
            self.m_con = sqlite3.connect(DataBase.DB_REL_PATH)
        else:
            # 若文件不存在，则初始化数据库
            # 数据库表名为paperlist
            self.m_con = sqlite3.connect(DataBase.DB_REL_PATH)
            self.m_con.execute('''create table paperlist(
                No INTEGER PRIMARY KEY AUTOINCREMENT,
                ReadOrNot       INT,
                PublicationYear INT,
                Publisher       TEXT,
                Author          TEXT,
                PaperName       TEXT,
                Tags            TEXT,
                Notes           TEXT,
                Url             TEXT,
                Path            TEXT,
                LastReadDate    TEXT,
                Q0              TEXT,
                Q1              TEXT,
                Q2              TEXT,
                Q3              TEXT,
                Q4              TEXT,
                Q5              TEXT,
                Q6              TEXT,
                Q7              TEXT,
                Q8              TEXT,
                Q9              TEXT
                );
                ''')
            self.m_con.commit()

        # 将查询结果返回为字典类型而非元组
        self.m_con.row_factory = dict_factory 

        return None



    def add_paper(self, info:dict):
        # 向数据库中插入paper条目,数据来自字典info{"字段":"值"}
        # PaperName字段不能为空
        # No字段自动生成，ReadOrNot默认记为0，
        # 没有的字段默认为空字符串
        
        fields = "ReadOrNot"  # 字段
        values = "0"  # 值

        if not info.get("PaperName"):
            return MY_ERROR_NO_PAPERNAME

        # 依次从info中读取字段
        add_fields = copy.deepcopy(DataBase.FIELD_LIST)
        add_fields.remove("No")
        add_fields.remove("ReadOrNot")
        add_fields.remove("PublicationYear")

        if info.get("PublicationYear"):
            fields += "," + "PublicationYear"
            values += "," + str(info.get("PublicationYear"))
        for item in add_fields:
            if info.get(item):
                fields += "," + item
                values += ",\"" + str(info.get(item)) + "\""
            else:
                fields += "," + item
                values += ",\"\""

        self.m_con.execute(f'''
            insert into paperlist ({fields}) values ({values});     
            ''')
        self.m_con.commit()
        
        return MY_SUCCESS



    def modi_paper(self, info:dict):
        # 修改指定No的paper条目，从info中提取信息

        # update的sql语句
        update = ""

        no = info.get("No")
        if not no:
            return MY_ERROR_NO_PAPERNO
        
        modi_fields = copy.deepcopy(DataBase.FIELD_LIST)
        modi_fields.remove("No")
        modi_fields.remove("ReadOrNot")
        modi_fields.remove("PublicationYear")

        # 依次读取待修改的属性
        if info.get("ReadOrNot"):
            update += "ReadOrNot=" + str(info.get("ReadOrNot")) + ","
        if info.get("PublicationYear"):
            update += "PublicationYear=" + str(info.get("PublicationYear")) + ","
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
        self.m_con.execute(f'''
            UPDATE paperlist
            SET {update}
            WHERE No = {no};
        ''')
        self.m_con.commit()

        return MY_SUCCESS

    def del_paper(self, info:dict):
        # 删除paper，删除info中No指定的文献
        # 只能删除一条

        no = info.get("No")
        if not no:
            return MY_ERROR_NO_PAPERNO

        self.m_con.execute(f'''
            DELETE FROM paperlist
            WHERE No = {no};
        ''')
        self.m_con.commit() 

        return MY_SUCCESS


    def show_all_paper(self):
        # 返回文献的字典的列表

        ret_list = list(self.m_con.execute('''
            select * from paperlist
            ORDER BY PublicationYear, Publisher, PaperName  DESC;
            '''))

        return ret_list


    def find_paper(self, info:dict):
        # 查找函数，按字典info信息查找特定的paper
        # pubyear_begin pubyear_end puber_list tag_list keyword
        # keyword_flag

        ret_list = []
        search_condition = ""

        if info.get("pubyear_begin"):
            if search_condition == "":
                search_condition += "PublicationYear >= "+str(info.get("pubyear_begin"))
            else:
                search_condition += " AND "+"PublicationYear >= "+str(info.get("pubyear_begin"))
        if info.get("pubyear_end"):
            if search_condition == "":
                search_condition += "PublicationYear <= "+str(info.get("pubyear_end"))
            else:
                search_condition += " AND " + "PublicationYear <= "+str(info.get("pubyear_end"))
        if info.get("puber_list"):
            if len(info.get("puber_list")) != 0:
                if search_condition != "":
                    search_condition += " AND "
                search_condition += "("
                i = 0
                for item in info.get("puber_list"):
                    if(i != 0):
                        search_condition += " OR "
                    search_condition += "Publisher LIKE "+'\''+str(item)+'\''
                    i += 1
                search_condition += ")"
        if info.get("tag_list"):
            if len(info.get("tag_list")) != 0:
                if search_condition != "":
                    search_condition += " AND "
                search_condition += "("
                i = 0
                for item in info.get("tag_list"):
                    if(i != 0):
                        search_condition += " OR "
                    search_condition += "Tags LIKE \'%"+str(item)+"%\'"
                    i += 1
                search_condition += ")"
        if info.get("keyword"):
            sear_key = info.get("keyword")
            if (info.get("keyword_flag") == 3):
                if search_condition != "":
                    search_condition += " AND "
                search_condition += f"(PaperName LIKE \'%{sear_key}%\' OR Notes LIKE \'%{sear_key}%\')"
            elif (info.get("keyword_flag") == 1):
                if search_condition != "":
                    search_condition += " AND "
                search_condition += f"PaperName LIKE \'%{sear_key}%\'"
            elif (info.get("keyword_flag") == 2):
                if search_condition != "":
                    search_condition += " AND "
                search_condition += f"Notes LIKE \'%{sear_key}%\'"

        # print(search_condition)

        if search_condition == "":
            return self.show_all_paper()
        
        ret_list = list(self.m_con.execute(f'''
            select * from paperlist
            WHERE {search_condition}
            ORDER BY PublicationYear, Publisher, PaperName  DESC;
            '''))
        # print(ret_list)

        return ret_list


    def get_all_pub(self): 
        # 查找数据库中全部的出版商
        # return list
        ret = []
        origin_info = list(self.m_con.execute('''
            select Publisher from paperlist;
            '''))
        pub_set = set()
        for item in origin_info:
            pub_set.add(item.get("Publisher"))
        pub_set.add("")
        ret = list(pub_set)
        ret.sort()

        return ret

    def get_all_tags(self): 
        # 查找数据库中全部的tag
        # return list
        ret = []
        origin_info = list(self.m_con.execute('''
            select Tags from paperlist;
            '''))
        tags_list = []
        for item in origin_info:
            tags_list.append(item.get("Tags"))
        tag_set = set()
        for item in tags_list:
            for j in item.split('$'):
                tag_set.add(j)
        tag_set.add("")
        ret = list(tag_set)
        ret.sort()
        
        return ret
    




