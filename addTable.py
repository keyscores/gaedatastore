import MySQLdb
import sys
import types;

# connect to mysql
with open('mysql_setting.txt', 'r') as f:
  mysql_config = f.readline()

mysql_params = mysql_config.split(",")  
localhost = mysql_params[0]
user = mysql_params[1]
password = mysql_params[2]
db_name = mysql_params[3]
db = MySQLdb.connect(localhost, user, password, db_name)

#----------------------------------------
def getHeader(cursor, table_name):
    cursor.execute("SELECT `COLUMN_NAME`  FROM `INFORMATION_SCHEMA`." \
                   "`COLUMNS`  WHERE `TABLE_SCHEMA`='source' AND " \
                   "`TABLE_NAME`='"+ table_name+"';")
    numrows = cursor.rowcount
    header = ""
    for x in xrange(0,numrows):
        row = cursor.fetchone()
        header += row[0] + ","
    
    header = header[3:-1]
    return header

#----------------------------------------
def insertMeta(cursor, header, table_name, facts_str, date_pos):
    sql_insert = "insert into table_meta (name, header, facts, date)" +\
        " values ('%s','%s','%s',%s);" 
    sql = sql_insert%(table_name,header,facts_str,str(date_pos))
    cursor.execute(sql)

#----------------------------------------
def addRows(cursor, table_name, table_id, max_link_id):
    sql_select = "select id +%s as link_id,%s as table_id from source.%s;"\
        %(max_link_id, table_id, table_name)
    sql_insert =  "insert into table2link(link_id, table_id)"
    sql = sql_insert + " " + sql_select
    print sql
    cursor.execute(sql)

#----------------------------------------
def addFactCol(cursor, fact_name, table_name, max_link_id):
    print "add fact col: %s.%s"%(table_name, fact_name)
    # add fact_name
    sql_insert = "insert into fact_names(name) values ('%s');"%(fact_name)
    cursor.execute(sql_insert)
    print sql_insert
    # get fact_id
    sql_select = "select id from fact_names where name = '%s';"%(fact_name)
    print sql_select
    cursor.execute(sql_select)
    fact_id = cursor.fetchone()[0]
    print "FACT_ID: %s"%(fact_id)
    # add fact col
    sql_select = "select id +%s as link_id,%s as value, %s as fact_id from source.%s;"\
        %(max_link_id, fact_name, fact_id,table_name)
    sql_insert =  "insert into fact2link(link_id, value,fact_id)"
    sql = sql_insert + " " + sql_select
    print sql
    cursor.execute(sql)

#----------------------------------------    
def addDimCol(cursor, dim_name, table_name, max_link_id):
    print "add dim col: %s.%s"%(table_name, dim_name)
    sql_select = "select id +%s as link_id,concat('%s:',%s) as dim_level from source.%s;"\
        %(max_link_id, dim_name,dim_name, table_name)
    sql_insert =  "insert into dim_level2link(link_id, dim_level)"
    sql = sql_insert + " " + sql_select
    print sql
    cursor.execute(sql)
    
#----------------------------------------    
def addDateCol(cursor, date_name, table_name,max_link_id):
    print "add date col: %s.%s"%(table_name, date_name)
    sql_select = "select id +%s as link_id,%s as date from source.%s;"\
        %(max_link_id, date_name, table_name)
    sql_insert =  "insert into date2link(link_id, date)"
    sql = sql_insert + " " + sql_select
    print sql        
    cursor.execute(sql)

#----------------------------------------    
def addTable(table_name, facts_str, date_pos, db):
    cursor = db.cursor()
        
    header = getHeader(cursor, table_name)
    insertMeta(cursor, header, table_name, facts_str, date_pos)
   
    # get max link _id
    sql = "select max(link_id) from table2link;"
    cursor.execute(sql)
    max_link_id = cursor.fetchone()[0]
    if isinstance(max_link_id, types.NoneType):
                max_link_id = 0
            
    
    
    # get table_id
    sql = "select id from table_meta where name = '%s';"%(table_name)
    cursor.execute(sql)
    table_id = cursor.fetchone()[0]
    
    addRows(cursor,table_name, table_id, max_link_id)
   
    facts_flag = facts_str.split(",")
    cols = header.split(",")
    col_counter = 0
    addCol = {"fact":addFactCol,"dim":addDimCol,"date":addDateCol}
    for col in cols:
        type = "fact"
        if facts_flag[col_counter] == "0":
            type = "dim"
        if col_counter == date_pos:
            type = "date"
        print "---------------"
        addCol[type](cursor, col, table_name, max_link_id)    
        col_counter += 1
 
    
addTable("Sales","0,0,1,1,0,0,0",4,db)
addTable("ComissionTax","0,0,0,1,1",-1,db)
addTable("CountryRegion","0,0",-1,db)

db.commit()
    