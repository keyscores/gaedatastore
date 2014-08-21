import MySQLdb
import sys

# connect to mysql
with open('mysql_setting.txt', 'r') as f:
  mysql_config = f.readline()

mysql_params = mysql_config.split(",")  
localhost = mysql_params[0]
user = mysql_params[1]
password = mysql_params[2]
db_name = mysql_params[3]


con = MySQLdb.connect(localhost, user, password, db_name)



try:
    with con:
        cur = con.cursor()
        
        # ---------------------------------------
        #                 names
        # ---------------------------------------
        cur.execute("CREATE TABLE table_meta(id INT PRIMARY KEY AUTO_INCREMENT, \
                 name VARCHAR(25) NOT NULL UNIQUE,header VARCHAR(200), \
                 facts VARCHAR(50), date INT)")
        
        cur.execute("CREATE TABLE fact_names(Id INT PRIMARY KEY AUTO_INCREMENT, \
                 Name VARCHAR(50) NOT NULL UNIQUE)")
        
        cur.execute("CREATE TABLE fact2link(link_id INT, \
                    value INT, fact_id INT)")
        
        cur.execute("CREATE TABLE dim_level2link(dim_level VARCHAR(25), link_id INT)")
        
        cur.execute("CREATE TABLE date2link(date VARCHAR(25), link_id INT)")
        
        cur.execute("CREATE TABLE table2link(table_id INT, link_id INT)")

        cur.execute("CREATE TABLE level_names(Id INT PRIMARY KEY AUTO_INCREMENT, \
                  Name VARCHAR(25) NOT NULL UNIQUE)")
        
        cur.execute("CREATE TABLE date_values(Id INT PRIMARY KEY AUTO_INCREMENT, \
                  Value DATE NOT NULL UNIQUE)")
        
        
except MySQLdb.Error, e:
  
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)