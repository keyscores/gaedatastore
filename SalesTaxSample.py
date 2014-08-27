import MySQLdb

# connect to mysql
with open('mysql_setting.txt', 'r') as f:
    mysql_config = f.readline()

mysql_params = mysql_config.split(",")  
localhost = mysql_params[0]
user = mysql_params[1]
password = mysql_params[2]
db_name = mysql_params[3]
db = MySQLdb.connect(localhost, user, password, db_name)

cursor = db.cursor()

#----------------------------------------
def data2BigTable(cursor):
    sql = "insert into BigTable select S.id,S.VendorId,S.ProductType, "\
        "S.Units, S.RoyaltyPrice, S.DownloadDate, S.CustomerCurrency, "\
        "S.CountryCode, C.Region, T.RightsHolder, T.ComissionRate, "\
        "T.TaxRate from Sales S Inner Join CountryRegion C on "\
        "S.CountryCode=C.CountryCode Inner join ComissionTax T on " \
        "S.VendorId = T.VendorIdentifier and C.Region = T.Region;"

    print sql
    cursor.execute(sql)

#----------------------------------------
def cleanUp(cursor):
    sql = "ALTER TABLE BigTable change ComissionRate ComissionRate FLOAT;"
    cursor.execute(sql)
    sql = "ALTER TABLE BigTable change TaxRate TaxRate FLOAT;"
    cursor.execute(sql)
    sql ="update BigTable set TaxRate = TaxRate/100;"
    cursor.execute(sql)

#----------------------------------------    
def addFactUsingBinaryOp(new_fact_name, 
                         left_hand_fact, 
                         right_hand_fact,
                         op):
    
    sql =  "alter table BigTable add column %s FLOAT;"%(new_fact_name)
    print sql
    cursor.execute(sql)
    sql = "update BigTable set %s = %s%s%s;"%(new_fact_name,
                                              left_hand_fact,
                                              op,
                                              right_hand_fact)
    cursor.execute(sql)
    print sql

#----------------------------------------    
def calculate(fact_name, fact_date=None):
    sql = "select sum(%s) from BigTable;"%(fact_name)
    if fact_date != None :
        sql = 'select sum(%s) from BigTable where DownloadDate = "%s"'%(fact_name,fact_date);
    cursor.execute(sql)    
    print sql
    return cursor.fetchone()[0]    
    
    
data2BigTable(cursor)
cleanUp(cursor)
addFactUsingBinaryOp("NET_REVENUE", "Units", "RoyaltyPrice", "*") 
addFactUsingBinaryOp("TAXES", "NET_REVENUE","TaxRate","*")
addFactUsingBinaryOp("REVENUE_AFTER_TAX", "NET_REVENUE","TAXES","-")
assert(calculate("NET_REVENUE","6/1/14") == 24)
assert(calculate("TAXES","6/1/14") == 1.2576)
assert(calculate("REVENUE_AFTER_TAX","6/1/14") == 22.7424)

db.commit()
