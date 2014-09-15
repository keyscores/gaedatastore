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
def calculate(fact_name, fact_date=None, dim_level=None):
    sql = "select sum(%s) from BigTable;"%(fact_name)
    if fact_date != None :
        sql = 'select sum(%s) from BigTable where DownloadDate = "%s"'%(fact_name,fact_date);
    if dim_level != None:
        dim_name, level_name = dim_level.split(":")
        sql = 'select sum(%s) from BigTable where %s = "%s"'%(fact_name,dim_name, level_name);
    if (fact_date != None) & (dim_level != None):
        sql = 'select sum(%s) from BigTable where %s = "%s" and DownloadDate = "%s"'\
            %(fact_name,dim_name, level_name,fact_date);         
    cursor.execute(sql)    
    return cursor.fetchone()[0]    

#----------------------------------------    
def calculateGroupBy(fact_name, group_by, where_str):
    sql = "select sum(subtotal) from (select %s as subtotal from BigTable group by %s) as total;"\
        %(fact_name, group_by)
    if where_str != None:
        sub_sql = "select sum(subtotal) from (select %s as subtotal " +\
            "from BigTable where %s group by %s) as total;" 
        sql = sub_sql%(fact_name, where_str, group_by)
    print sql                 
    cursor.execute(sql)    
    return cursor.fetchone()[0]
    
#----------------------------------------    
def calculateSm2(left_hand_fact, op, right_hand_fact, fact_date=None, dim_level=None):
    sql = "select sum(%s) %s sum(%s) from BigTable;"%(left_hand_fact, op, right_hand_fact)
    if fact_date != None :
        sql = 'select sum(%s) %s sum(%s) from BigTable where DownloadDate = "%s"'\
        %(left_hand_fact, op, right_hand_fact,fact_date);
    if dim_level != None:
        dim_name, level_name = dim_level.split(":")
        sql = 'select sum(%s) %s sum(%s) from BigTable where %s = "%s"'\
            %(left_hand_fact, op, right_hand_fact,dim_name, level_name);
    if (fact_date != None) & (dim_level != None):
        sql = 'select sum(%s) %s sum(%s) from BigTable where %s = "%s" and DownloadDate = "%s"'\
            %(left_hand_fact, op, right_hand_fact,dim_name, level_name,fact_date);
    cursor.execute(sql)    
    return cursor.fetchone()[0]    

    
    
#data2BigTable(cursor)
#cleanUp(cursor)
#addFactUsingBinaryOp("NET_REVENUE", "Units", "RoyaltyPrice", "*") 
#addFactUsingBinaryOp("TAXES", "NET_REVENUE","TaxRate","*")
#addFactUsingBinaryOp("REVENUE_AFTER_TAX", "NET_REVENUE","TAXES","-")
print calculate("NET_REVENUE","6/1/14") 
print calculate("TAXES","6/1/14") 
print calculate("REVENUE_AFTER_TAX","6/1/14") 
print calculate("REVENUE_AFTER_TAX",None,"Region:World") 
print calculate("TAXES", "6/1/14","VendorId:0268_20140114_SOFA_ENGLIS") 
print calculate("NET_REVENUE", "6/1/14","VendorId:0268_20140114_SOFA_ENGLIS")
print calculate("TAXES", "6/1/14","Region:Latam")
print calculate("TAXES", "6/1/14","ProductType:D")
print calculateSm2("REVENUE_AFTER_TAX","/","NET_REVENUE", "6/1/14",None)
print calculateSm2("REVENUE_AFTER_TAX","/","NET_REVENUE", "6/1/14","VendorId:0268_20140114_SOFA_ENGLIS")

print "NEW TEST CASES"
print "(1)" + str(calculate("Units","6/1/14"))
print "-------*-----------"
print "(2)" + str(calculate("NET_REVENUE","6/1/14"))
print "(3)" + str(calculateGroupBy("sum(Units)* sum(RoyaltyPrice)",
                                   "VendorId, ProductType, DownloadDate"," id < 5 "))
print "(4)" + str(calculateGroupBy("sum(Units)* sum(RoyaltyPrice)",
                                   "DownloadDate"," id < 5 "))
print "-------+-----------"
print "(5)" + str(calculate("Units + RoyaltyPrice","6/1/14"))
print "(6)" + str(calculateGroupBy("sum(Units)+ sum(RoyaltyPrice)",
                                   "VendorId, ProductType, DownloadDate"," id < 5 "))
print "(7)" + str(calculateGroupBy("sum(Units)+ sum(RoyaltyPrice)",
                                   "DownloadDate"," id < 5 "))

print "INTERTABLE *"
print "(8 ???)" + str(calculate("RoyaltyPrice*TaxRate","6/1/14"))
print "(9)" + str(calculateGroupBy("sum(RoyaltyPrice) * sum(TaxRate)",
                                   "VendorId, ProductType, DownloadDate"," id < 5 "))
print "(10)" + str(calculateGroupBy("sum(RoyaltyPrice) * sum(TaxRate*RoyaltyPrice)",
                                   "DownloadDate"," id < 5 "))
print "INTERTABLE +"
print "(11)" + str(calculate("RoyaltyPrice+TaxRate","6/1/14"))
print "(12)" + str(calculateGroupBy("sum(RoyaltyPrice) + sum(TaxRate)",
                                   "VendorId, ProductType, DownloadDate"," id < 5 "))
print "(13)" + str(calculateGroupBy("sum(RoyaltyPrice) + sum(TaxRate)",
                                   "DownloadDate"," id < 5 "))
print "CHAINED +"
print "(14)" + str(calculate("REVENUE_AFTER_TAX","6/1/14"))
print calculateSm2("REVENUE_AFTER_TAX","/","NET_REVENUE", "6/1/14",None)
print "16 todo)" 

print "-------------FILTER--------------------"
print "(1)" + str(calculate("Units", "6/1/14","VendorId:0268_20140114_SOFA_ENGLIS"))
print "-------*-----------"
print "(2)" + str(calculate("NET_REVENUE","6/1/14","VendorId:0268_20140114_SOFA_ENGLIS"))
print "(3)" + str(calculateGroupBy("sum(Units)* sum(RoyaltyPrice)",
                                   "VendorId, ProductType, DownloadDate"," id < 5 and VendorId='0268_20140114_SOFA_ENGLIS' "))
print "(4)" + str(calculateGroupBy("sum(Units)* sum(RoyaltyPrice)",
                                   "DownloadDate"," id < 5 and VendorId='0268_20140114_SOFA_ENGLIS'"))
print "-------+-----------"
print "(5)" + str(calculate("Units + RoyaltyPrice","6/1/14","VendorId:0268_20140114_SOFA_ENGLIS"))
print "(6)" + str(calculateGroupBy("sum(Units)+ sum(RoyaltyPrice)",
                                   "VendorId, ProductType, DownloadDate"," id < 5 and VendorId='0268_20140114_SOFA_ENGLIS' "))
print "(7)" + str(calculateGroupBy("sum(Units)+ sum(RoyaltyPrice)",
                                   "DownloadDate"," id < 5 and VendorId='0268_20140114_SOFA_ENGLIS' "))

print "INTERTABLE *"
print "(8 ???)" + str(calculate("RoyaltyPrice*TaxRate","6/1/14","VendorId:0268_20140114_SOFA_ENGLIS"))
print "(9)" + str(calculateGroupBy("sum(RoyaltyPrice) * sum(TaxRate)",
                                   "VendorId, ProductType, DownloadDate"," id < 5 and VendorId='0268_20140114_SOFA_ENGLIS' "))
print "(9)" + str(calculateGroupBy("sum(RoyaltyPrice) * sum(TaxRate*RoyaltyPrice)",
                                   "DownloadDate"," id < 5 and VendorId='0268_20140114_SOFA_ENGLIS' "))
print "INTERTABLE +"
print "(11)" + str(calculate("RoyaltyPrice+TaxRate","6/1/14","VendorId:0268_20140114_SOFA_ENGLIS"))
print "(12)" + str(calculateGroupBy("sum(RoyaltyPrice) + sum(TaxRate)",
                                   "VendorId, ProductType, DownloadDate"," id < 5 and VendorId='0268_20140114_SOFA_ENGLIS' "))
print "(13)" + str(calculateGroupBy("sum(RoyaltyPrice) + sum(TaxRate)",
                                   "DownloadDate"," id < 5 and VendorId='0268_20140114_SOFA_ENGLIS' "))


print "CHAINED +"
print "(14)" + str(calculate("REVENUE_AFTER_TAX","6/1/14","VendorId:0268_20140114_SOFA_ENGLIS"))
print calculateSm2("REVENUE_AFTER_TAX","/","NET_REVENUE", "6/1/14","VendorId:0268_20140114_SOFA_ENGLIS")
print "16 todo)" 

db.commit()
