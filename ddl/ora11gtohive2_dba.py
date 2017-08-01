__author__ = 'lenovo'
"""
python version ; 3.5.2
cx_Oracle verison : 5.2.1
Oracle version : 11gR2
Hive version : HIVE HUIWEI 1.3.0

us:read oracle metadata transform to Hive HUAWEI 1.3.0 metadata.
"""

import os
import re
import os.path

import cx_Oracle
import xlwt

#定义一个函数，用来获取oracle用户下的表明清单，可以做排除
def get_tables(cursor):
    """get table list
        return: list of tablename
    """
    sql = """
select user,table_name
  from dba_tables
where table_name not like '%$%'
    """
    cursor.execute(sql)
    res = cursor.fetchall()
    result = []
    result2 = []
    for i in res:
        result.append(i[1])
        result2.append([i[0],i[1]])
    print("查询到%d个表" % len(result2))
    return result,result2

def get_comment(cursor, tablename):
    """
    get table comment from tablename
    :param cursor: where you want get meta
    :param tablename:string is a table in this user
    :return:this table metadata with list , 表名，表注释，类型，列名，列注释，数据类型，字段长度，字段精度，是否可空，字段序号
    """
    sql = """
    select a.table_name
       , b.comments
       , b.table_type
       , a.COLUMN_NAME
       , c.comments
       , a.DATA_TYPE
       , a.DATA_LENGTH
       , a.DATA_PRECISION
       , a.NULLABLE
       , a.COLUMN_ID
  from dba_tab_cols a
       , dba_tab_comments b
       , dba_col_comments c
 where a.table_name = '%s'
   and a.TABLE_NAME = b.table_name
   and a.TABLE_NAME = c.table_name
   and a.COLUMN_NAME = c.column_name
 order by a.COLUMN_ID
 """ % tablename
    cursor.execute(sql)
    res = cursor.fetchall()
    if res:
        print("查询到表 %s 的列信息" % tablename)
        return res
    else:
        print("未查询到表 %s 的列信息" % tablename)
        return False



def transform_hive(tablename, table_comment, filepath,user):
    """
    :param table_comment:接收从get_comment函数 返回的值，进行处理
    :return:string about HIVE create ddl
    """
    mapping = {
    "DATE":"DATE",
    "NUMBER":"DECIMAL",
    "LONG":"DECIMAL",
    "VARCHAR2":"VARCHAR",
    "CHAR":"VARCHAR",
    "BLOB":"STRING",
    "TIMESTAMP(9)":"TIMESTAMP",
    "NVARCHAR2":"VARCHAR",
    "CLOB":"TEXT"
}
    hive_comment = []
    if table_comment:
        table_name = table_comment[0][0].lower()
        table_name_comment = table_comment[0][1]
        table_type = table_comment[0][2]
        table_info = (table_name,table_name_comment,table_type)
        for i in table_comment:
            #用来接收表的字段信息并完成字段类型的转换
            a = ()
            col_name = i[3].upper()
            col_comment = i[4]
            try:
                col_type = mapping[str(i[5])]
            except KeyError:
                print("find new Data type: %s,please deal it!" % i[5])
                exit(110)
            col_length = i[6]
            col_percision = i[7]
            nullable = i[8]
            id = i[9]
            a = (col_name, col_comment, col_type, col_length, col_percision, nullable, id)
            hive_comment.append(a)
        #开始拼装HIVE sql
        sql_head = """
CREATE TABLE %s
(   """ % table_name.upper()
        sql_body = ""
        for i in hive_comment:
            if i[1]:
                if i[2] in ("DATA","TIMESTAMP","STRING","TEXT"):
                    sql_body += "%s %s COMMENT '%s',\n" % (i[0], i[2], i[1])
                if i[2] in ("VARCHAR",):
                    sql_body += "%s %s(%s) COMMENT '%s',\n" % (i[0], i[2], i[3], i[1])
                if i[2] in ("DECIMAL",):
                    if i[4]:
                        sql_body += "%s %s(%s,%s) COMMENT '%s',\n" % (i[0], i[2], i[3], i[4], i[1])
                    else:
                        sql_body += "%s %s(%s) COMMENT '%s',\n" % (i[0], i[2], i[3], i[1])
            else:
                if i[2] in ("DATA","TIMESTAMP","STRING","TEXT"):
                    sql_body += "%s %s,\n" % (i[0], i[2])
                if i[2] in ("VARCHAR",):
                    sql_body += "%s %s(%s),\n" % (i[0], i[2], i[3])
                if i[2] in ("DECIMAL",):
                    if i[4]:
                        sql_body += "%s %s(%s,%s),\n" % (i[0], i[2], i[3], i[4])
                    else:
                        sql_body += "%s %s(%s),\n" % (i[0], i[2], i[3])
        sql_body = sql_body[:-2] #截取最后一个，\n
        if table_name_comment:
            sql_botten = """
)
COMMENT '%s'
PARTITIONED BY (ETL_DATE String COMMENT '数据日期')
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '$#'
STORED AS TEXTFILE
;
""" % table_name_comment
        else:
            sql_botten = """
)
PARTITIONED BY (ETL_DATE String COMMENT '数据日期')
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '$#'
STORED AS TEXTFILE
;
"""
        sql = sql_head + sql_body + sql_botten
        #开始写文件
        file = open(os.path.join(filepath,user+'.'+table_name+'.ddl'), 'w')
        try:
            file.write(sql.lower())
            print("表结构已经写入 %s" % user+'.'+table_name+'.ddl')
        finally:
            file.close()
        result = []
        for i in hive_comment:
            b = (table_info[0], table_info[1], table_info[2], i[0], i[1], i[2], i[3], i[4], i[5], i[6])
            result.append(b)
        return result

def set_style(name,height,bold=False):
    style = xlwt.XFStyle() # 初始化样式
    font = xlwt.Font() # 为样式创建字体
    font.name = name # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height

    # borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6

    style.font = font
    # style.borders = borders

    return style


def wttoExcel(f_excel,table_name ,table_comment):
    """
    :param table_comment: 从get_comment 函数获取信息，解析之后准备写入到excel中
    :return:True
    """

    sheet1 = f_excel.add_sheet(u'%s' % table_name, cell_overwrite_ok=True) #创建sheet
    column0 = [u'表名',u'表中文名',u'类型',u'字段名',u'字段中文名',u'字段类型',u'字段长度',u'字段精度',u'是否可为空',u'字段序号']
    #第一行信息写入
    for i in range(0,len(column0)):
        sheet1.write(0, i, column0[i])
    #写入数据部分
    for r in range(0,len(table_comment)):
        for c in range(0, len(table_comment[r])):
            if not table_comment[r][c]:
                value = ''
            else:
                value = table_comment[r][c]
            sheet1.write(r+1, c, value)




#定义oracle链接
#conn = cx_Oracle.connect("poc/poc@218db")
conn = cx_Oracle.connect("apps/apps@Glodwind_apps")
cursor = conn.cursor()
#定义输出路径
filepath = 'D:\HiveDDL'
#获取表清单
table_list,user_table_list = get_tables(cursor)
count = 0
#异常列表
err_list = []
f_oracle = xlwt.Workbook() #创建工作簿
f_hive = xlwt.Workbook()
print(str(user_table_list))
for i in user_table_list:
    try:
        print('1')
        ora_table_com = get_comment(cursor, i[1])
        print('2')
        wttoExcel(f_oracle, i[0]+'.'+i[1], ora_table_com)
        print('3')
        hive_table_com = transform_hive(i[1], ora_table_com, filepath,i[0])
        print('4')
        wttoExcel(f_hive, i[0]+'.'+i[1], hive_table_com)
        print('index : %d' % count )
    except Exception:
        print(Exception)
        err_list.append(i)
        continue
    count += 1
print("一共编写ddl语句 %d 个" % count)
print(str(err_list))
f_oracle.save('d:\HiveDDL\Oracle_PLM.xls') #保存文件
print("Oracle_PLM is write")
f_hive.save('d:\HiveDDL\HIVE_PLM.xls')
print("Hive_PLM is write")
cursor.close()
conn.close()