select a.TABLE_NAME AS 表名字,
         a.COMMENTS as 表注释,
         b.COLUMN_NAME as 字段名,
         case when c.DATA_TYPE = 'NUMBER'
              then 'NUMBER' || '(' || nvl(c.DATA_PRECISION,0) || ',' || c.DATA_SCALE || ')'
              when c.DATA_TYPE = 'VARCHAR2'
              then 'VARCHAR2' || '(' || c.CHAR_LENGTH || ')'
              else c.DATA_TYPE
          end as 字段类型,
         c.NULLABLE as 可否为空,
         b.COMMENTS as 字段注释
    from USER_TAB_COMMENTS a, USER_COL_COMMENTS b, USER_TAB_COLUMNS c
   where a.TABLE_NAME = b.TABLE_NAME(+)
     and b.COLUMN_NAME = c.COLUMN_NAME(+)
     and b.TABLE_NAME = c.TABLE_NAME