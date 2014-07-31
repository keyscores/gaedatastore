#### Measure definitions
# Sales.Unit refers to "Sales.csv" and column header "Unit"

# the first three only produce the expected business results if the dimensions are matching the multiplication.
NET_REVENUE = Sales.Units*Sales.Royalty Price
TAXES = NET_REVENUE * ComissionTax.Tax
REVENUE_AFTER_TAX = NET_REVENUE - TAXES
# this last one, will only produce expected results if it will groupby on date only (what we used to call SM2)
KPI_MARGIN = REVENUE_AFTER_TAX / NET_REVENUE

#### API
#for now a simple API like this returns a series.

def analytics(measure, start_date, end_date,filter_by_dimension_level_tuples)
# filter_by_dimension_level_tuples would allow two drill scenarios of: filtering and also breaking-down.


#### Tests
def test_chain()
	assert calculate(NET_REVENUE, 6/1/14,6/1/14) == 24
	assert calculate(TAXES, 6/1/14,6/1/14) == 1.2576
	assert calculate(REVENUE_AFTER_TAX, 6/1/14,6/1/14) == 22.7424
	assert calculate(KPI_MARGIN, 6/1/14,6/1/14) == 0.9226

def test_filter()
# test that filtering down a measure can produce correct results on SUM and SM2 situations (with and without a chain)
	# simple aggregation SUM, and no Chain
	assert calculate(NET_REVENUE, 6/1/14,6/1/14,"Vendor Identifier":"0268_20140114_SOFA_ENGLISHTEACHER") == 12
	
	# simple aggregation SUM, with Chain
	assert calculate(TAXES, 6/1/14,6/1/14, "Vendor Identifier":"0268_20140114_SOFA_ENGLISHTEACHER") == 0.6288
	
	# now test with the SM2 situation and Chain
	assert calculate(KPI_MARGIN, 6/1/14,6/1/14,"Vendor Identifier":"0268_20140114_SOFA_ENGLISHTEACHER") == 0.9476

def test_broadcasting()
# test where filter dimension is on a different table than fact (we solved this with broadcasting in pandas)

	assert calculate(TAXES, 6/1/14,6/1/14, "Region":"Latam") == 1.2
	assert calculate(TAXES, 6/1/14,6/1/14, "Product Type Identifier":"D") == 0.6288
	
	
