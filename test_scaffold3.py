###############Test Class, Test that we can load only the most current version when there are multiple versions of files uploaded (Multiversion) 


##Case Aggregate	
1 Measure: Units	:	Date
			 120.00 	:	6/1/14
######### Binary Ops

#multiply
2 Case Multiplication, without groupby, per record
Measure: Gross Sales=(Units*Royalty_Price)	:	Date
										  2,400.00 	:	6/1/14
						
#######Intertable
#multiply
8 Case Intertable Multiplication, without groupby, per record
Measure: Individual Tax =(Royalty_Price*Tax Rate)	:	Date
										    56.00  	:	6/1/14

###############Test Class, Tests that we can aggregate data from multiple companies (Crosscompany)

##Case Benchmarks	
1 Measure: Units	Total "Units" sold by all customers:	Date
			 315.00 	:	6/1/14
	
2 Measure: Units	AVERAGE "Units" sold by all customers:	Date
			 157.50 	:	6/1/14
