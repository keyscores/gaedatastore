#### Measure definitions
# Sales.Unit refers to "Sales.csv" and column header "Unit"

# the first three only produce the expected business results if the dimensions are matching the multiplication.
NET_REVENUE = Sales.Units*Sales.Royalty Price
TAXES = NET_REVENUE * ComissionTax.Tax
REVENUE_AFTER_TAX = NET_REVENUE - TAXES
# this last one, will only produce expected results if it will groupby on date only (what we used to call SM2)
KPI_MARGIN = REVENUE_AFTER_TAX / NET_REVENUE
	
###############
###############Test Class, Totals,  original periodicity	

##Case Aggregate	
1 Measure: Units	:	Date
			12	:	6/1/14
######### Binary Ops

#multiply
2 Case Multiplication, without groupby, per record
Measure: Gross Sales=(Units*Royalty_Price)	:	Date
										24	:	6/1/14

3 Case Multiplication, with groupby (Vendor Identifier, Product Type Idenfier,Date)
Measure: Gross Sales=(Units*Royalty_Price)      	:	Date
									        	36	:	6/1/14

4 Case Multiplication, with groupby (none/Date)
Measure: Gross Sales=(Units*Royalty_Price)	        :	Date
						                		96	:	6/1/14
										
##Add (This is a simple case, but these are here for 'completeness' of regression tests, and as documentation)					
5 Case Addition without groupby, per record	
Measure: Plus=(Units+Royalty_Price)             	:	Date
								              20	:	6/1/14
								              
6 Case Addition with groupby (Vendor Identifier, Product Type Idenfier,Date)	
Measure: Gross Plus=(Units+Royalty_Price)       	:	Date
										      20	:	6/1/14
7 Case Addition with groupby (Date)	
Measure: Gross Sales=(Units+Royalty_Price)	        :	Date
									        	20	:	6/1/14
										
#######Intertable
#multiply
8 Case Intertable Multiplication, without groupby, per record
Measure: Individual Tax =(Royalty_Price*Tax Rate)	:	Date
										   0.62 	:	6/1/14

9 Case Intertable Multiplication, with groupby (Vendor Identifier, Product Type Idenfier,Date)
Measure: Individual Tax =(Royalty_Price*Tax Rate)	:	Date
										    2.82 	:	6/1/14
											
10 Case Intertable Multiplication, with groupby (Date)	
Measure: Individual Tax =(Royalty_Price*Tax Rate)	:	Date
										   4.95 	:	6/1/14
										
#add	
11 Case Intertable Addition without groupby, per record	
Measure: Nonsense Add=(Royalty_Price+Tax Rate)	    :	Date
									       8.31 	:	6/1/14
									
12 Case Intertable Addition with groupby (Vendor Identifier, Product Type Idenfier,Date)
Measure: Nonsense Add=(Royalty_Price+Tax Rate)	:	Date
										 8.31 	:	6/1/14

13 Case In	tertable Addition with groupby (Date)	
Measure: Nonsense Add=(Royalty_Price+Tax Rate)	        :	Date
												 8.31 	:	6/1/14
#### Chained

14 Chain Calculation Intertable
	Measure: REVENUE_AFTER_TAX (see above) 	           :	Date
											     22.1424 :	6/1/14
	
15 Chain Calculation Intertable ending with SM2
	Measure: KPI_MARGIN(see above) 	                   :	Date
										    	  0.9226 :	6/1/14

16 Chain Calculation Intertable with sandwich SM2
	Measure: Unit_Margin=(KPI_MARGIN*Royalty_Price)	    :	Date
										    	  29.5232 :	6/1/14
###############
###############Test Class, Totals, with filter

##Case Aggregate	
1 Measure: Units	:	Date
			6	:	6/1/14
######### Binary Ops

#multiply
2 Case Multiplication, without groupby, per record
Measure: Gross Sales=(Units*Royalty_Price)	:	Date
										12	:	6/1/14

3 Case Multiplication, with groupby (Vendor Identifier, Product Type Idenfier,Date)
Measure: Gross Sales=(Units*Royalty_Price)      	:	Date
									        	24	:	6/1/14

4 Case Multiplication, with groupby (none/Date)
Measure: Gross Sales=(Units*Royalty_Price)	        :	Date
						                		24	:	6/1/14
										
##Add (This is a simple case, but these are here for 'completeness' of regression tests, and as documentation)					
5 Case Addition without groupby, per record	
Measure: Plus=(Units+Royalty_Price)             	:	Date
								              10	:	6/1/14
								              
6 Case Addition with groupby (Vendor Identifier, Product Type Idenfier,Date)	
Measure: Gross Plus=(Units+Royalty_Price)       	:	Date
										      10	:	6/1/14
7 Case Addition with groupby (Date)	
Measure: Gross Sales=(Units+Royalty_Price)	        :	Date
									        	10	:	6/1/14
										
#######Intertable
#multiply
8 Case Intertable Multiplication, without groupby, per record
Measure: Individual Tax =(Royalty_Price*Tax Rate)	:	Date
										   0.21 	:	6/1/14

9 Case Intertable Multiplication, with groupby (Vendor Identifier, Product Type Idenfier,Date)
Measure: Individual Tax =(Royalty_Price*Tax Rate)	:	Date
										    0.42 	:	6/1/14
											
10 Case Intertable Multiplication, with groupby (Date)	
Measure: Individual Tax =(Royalty_Price*Tax Rate)	:	Date
										   0.84 	:	6/1/14
										
#add	
11 Case Intertable Addition without groupby, per record	
Measure: Nonsense Add=(Royalty_Price+Tax Rate)	    :	Date
									       4.10 	:	6/1/14
									
12 Case Intertable Addition with groupby (Vendor Identifier, Product Type Idenfier,Date)
Measure: Nonsense Add=(Royalty_Price+Tax Rate)	    :	Date
										    4.10 	:	6/1/14

13 Case Intertable Addition with groupby (Date)	
Measure: Nonsense Add=(Royalty_Price+Tax Rate)	       :	Date
											   4.10    :	6/1/14
#### Chained

14 Chain Calculation Intertable
	Measure: REVENUE_AFTER_TAX (see above) 	           :	Date
											     11.37 :	6/1/14
	
15 Chain Calculation Intertable ending with SM2
	Measure: KPI_MARGIN(see above) 	                   :	Date
										    	  0.95 :	6/1/14

16 Chain Calculation Intertable with sandwich SM2
	Measure: Unit_Margin=(KPI_MARGIN*Royalty_Price)	    :	Date
										    	 7.58	:	6/1/14


##### TO DO	
Test class, breakdown by "vendor id"	
Test Class, Totals, aggregate periods to quarter or year
Test class, Totals with rolling sum	
Test class, Totals with sum positive	
Test class, Totals with previous period	
	
