__author__ = 'lenovo'

import os
import sys
import re

import cx_Oracle
"""
oracle version; 11gR2
python version: 3.4.0
cx-Oracle: 1.5.2
功能:配置数据库链接，把数据直接加载到oracle数据库中。
:输入文件名，读取数据库表结构，编写load命令ctl文件，把数据导入到Oarcle数据库中。
"""

#获取环境变量
LOAD_PATH = os.getenv("LOAD_PATH")
#路径配置文件,文件夹路径filepath，load控制文件路径ctlpath，加载日志文件路径logpath
filepath= LOAD_PATH
datapath = os.path.join(filepath, "data")
if os.path.exists(datapath):os.mkdir(datapath)
ctlpath = os.path.join(filepath, "ctl")
if os.path.exists(ctlpath):os.mkdir(ctlpath)
logpath = os.path.join(filepath, "log")
if os.path.exists(logpath):os.mkdir(logpath)

#获取输入字段列表：目前规则为：tablename。txt
filename = ""

#由获取的字段衍生出来的字段,根据文件名获取表明
tablename = filename.split(".")[0]


#获取数据库字符串
def getddl(cursor, tablename):
    """
    根据数据库链接和表名字，获取数据表的元数据信息
    :param cursor:数据库链接字符串
    :param tablename: 表名字
    :return:dict : {col1:col_type,col2:col_type}
    """
    cursor.execute("""
    select a.table_name
       , a.COLUMN_NAME
       , a.DATA_TYPE
       , a.DATA_LENGTH
       , a.DATA_PRECISION
  from user_tab_cols a
       , user_tab_comments b
       , user_col_comments c
 where a.table_name = '%s'
   and a.TABLE_NAME = b.table_name
   and a.TABLE_NAME = c.table_name
   and a.COLUMN_NAME = c.column_name
 order by a.COLUMN_ID
    """ % tablename)
    res = cursor.fetchall()
    if res:
        return res
    else:
        return False

def mkctlfile(tablename, ddl_dict):
    """
    根据ddl_dict拼装出来load ctl语句
    :param tablename: 表名
    :param ddl_dict: 表字段元数据信息
    :return:
    """
    pass

#执行批量加载函数
def load(datapath, logpath, ctlpath, filename):
    """
    :param datapath: 文件路径
    :param logpath: 日志路径
    :param ctlpath: 控制文件路径
    :param filename: 数据文件名称
    :return:
    """
    #数据文件realpath
    datafile = os.path.join(datapath, filename)
    if os.path.isfile(datafile):
        pass
