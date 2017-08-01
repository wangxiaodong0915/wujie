__author__ = 'lenovo'

import  os
import sys

import xlwt
import cx_Oracle

#定义一个函数，用来获取oracle用户下的表明清单，可以做排除
def get_tables(cursor):
    """get table list
        return: list of tablename
    """
    sql = """
select table_name
  from user_tables
    """
    cursor.execute(sql)
    res = cursor.fetchall()
    result = []
    for i in res:
        result.append(i[0])
    print("查询到%d个表" % len(result))
    return result

#获取数据库字符串
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
  from user_tab_cols a
       , user_tab_comments b
       , user_col_comments c
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

def mkoraddl(cursor, table_comment):
    """
    把读到的表元数据编写成ddl文档
    :param cursor: 数据库链接
    :param table_comment: dict of table metadata
    :return:（ddl&True） or False
    """
    pass

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

f_oracle = xlwt.Workbook()
conn = cx_Oracle.connect("poc/poc@218db")
cursor = conn.cursor()
tablelist = get_tables(cursor)
if tablelist:
    for tablename in tablelist:
        try:
            ora_comment = get_comment(cursor, tablename)
            wttoExcel(f_oracle, tablename, ora_comment)
            #编写ddl文件
            mkoraddl(cursor, ora_comment)
        except Exception:
            print(" is Error %e")
print("make excel of PLM")
f_oracle.save("d:\HiveDDL\Oracle_PLM.xls")
