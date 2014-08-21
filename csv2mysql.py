import csv
import MySQLdb

def getInsert(table, header):
    field_names = ', '.join(header)
    field_markers = ', '.join('%s' for col in header)
    return 'INSERT INTO %s (%s) VALUES (%s);' % \
        (table, field_names, field_markers)
        
def getSchema(table, header, col_types):
    schema_sql = """CREATE TABLE IF NOT EXISTS %s (id int NOT NULL AUTO_INCREMENT,""" % table 
    for col_name, col_type in zip(header, col_types):
        schema_sql += '%s %s,' % (col_name, col_type)
    schema_sql += """PRIMARY KEY (id)) DEFAULT CHARSET=utf8;"""
    return schema_sql     
     
def getDB(host, user, password):
    db = MySQLdb.connect(host=host, user=user, passwd=password)
    return db

def csv2DB(csv_name, host, user, password,db_name):
    db = getDB(host, user, password)
    cursor = db.cursor()
    cursor.execute("use " + db_name + ";")
    input_file = csv_name
    table_name, postfix = csv_name.split(".") 
    row_counter = 0
    sql_insert = ""
    for row in csv.reader(open(input_file)):
        if row_counter == 0:
            header = row
            print header
            col_types = []
            for col in row:
                col_types.append("VARCHAR(50)")
            sql_insert = getInsert(table_name,  header)
            cursor.execute(getSchema(table_name, header, col_types))
        else:    
            print sql_insert
            print row     
            cursor.execute(sql_insert%tuple(map(repr,row)))
        row_counter += 1    
    db.commit()     

# connect to mysql
with open('mysql_setting.txt', 'r') as f:
  mysql_config = f.readline()

mysql_params = mysql_config.split(",")  
host = mysql_params[0]
user = mysql_params[1]
password = mysql_params[2]
db_name = mysql_params[3]


csv2DB("Sales.csv",host, user,password,db_name)
csv2DB("CountryRegion.csv",host, user,password, db_name)
csv2DB("ComissionTax.csv",host, user,password, db_name)        