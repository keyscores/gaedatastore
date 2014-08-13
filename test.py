import csv
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb 
import datetime
import logging

from fact import Fact
from correspondingfacts import CorrespondingFacts
 
class MainHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
 
        html_string = """
         <form action="%s" method="POST" enctype="multipart/form-data">
        Upload File:
        <input type="file" name="file"> <br>
        <input type="submit" name="submit" value="Submit">
        </form>""" % upload_url
 
        self.response.write(html_string)
 
 
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        process_csv(blob_info)
 
        blobstore.delete(blob_info.key())  # optional: delete file after import
        self.redirect("/")
 
 
def process_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter=',')
    # get file name
    csv_file_name =  blob_info.filename
    # get csv header
    [prefix, postfix] = csv_file_name.split(".")
    header = reader.next()
    temp_header = header
    header = []
    for col in temp_header:
        header.append(prefix + "." + col)
        

    for row in reader:
        col_counter = 0
        corresponding_facts = CorrespondingFacts()
        corresponding_facts.put()
        fact_keys = []
        if csv_file_name == "Sales.csv":
            date_str = row[4]
        for col in row:
            date =  datetime.datetime.strptime("1/1/14", '%m/%d/%y').date()
            if csv_file_name == "Sales.csv":
                 date = datetime.datetime.strptime(date_str, '%m/%d/%y').date()
            logging.info(col + "/n")
            fact = Fact(value = col,
                        name = header[col_counter],
                        corresponding_facts = corresponding_facts.key,
                        date = date)
            fact.put()
            fact_keys.append(fact.key)
            col_counter += 1
            corresponding_facts.facts = fact_keys
            corresponding_facts.names = header
            corresponding_facts.put()


class Tests(webapp2.RequestHandler):
    def get(self):
        logging.info("test")
        self.response.headers['Content-Type'] = 'text/plain'

        #-----------------
        # Test Net revenue
        #-----------------
        # NET_REVENUE = Sales.Units*Sales.Royalty Price
        #result = Fact.binaryOperation("Sales.Units",
        #                                    [["Sales.Royalty Price"]],
        #                                    "*",
        #                                    "NET_REVENUE")
        
        #result2table(result, self)
        #Fact.storeFacts(result, "NET_REVENUE")
        #Fact.fact2Table("NET_REVENUE.NET_REVENUE", self)


        #-----------------
        # Test Taxes
        #-----------------
        # TAXES = NET_REVENUE * ComissionTax.Tax
        link1 = ["NET_REVENUE.Country Code",
                 "CountryRegion.Country Code",
                 "CountryRegion.Region",
                 "ComissionTax.Region",
                 "ComissionTax.Tax Rate"]    

        link2 = ["NET_REVENUE.Units",
                 "NET_REVENUE.Vendor Identifier",
                 "ComissionTax.Vendor Identifier",
                 "ComissionTax.Tax Rate"]  

        #taxes = Fact.binaryOperation("NET_REVENUE.NET_REVENUE",[link1,link2],"*","TAXES")
        #result2table(taxes, self)
        #Fact.storeFacts(taxes, "TAXES")
        #Fact.fact2Table("TAXES.TAXES", self)    
        
        #------------------
        # Revenue After Tax
        #------------------
        # REVENUE_AFTER_TAX = NET_REVENUE - TAXES
        link1 = ["NET_REVENUE.Vendor Identifier",
                 "TAXES.Vendor Identifier",
                 "TAXES.TAXES"]

        link2 = ["NET_REVENUE.Country Code",
                 "TAXES.Country Code",
                 "TAXES.TAXES"]


        #revenues = Fact.binaryOperation("NET_REVENUE.NET_REVENUE",
        #                                [link1, link2],"-","REVENUE_AFTER_TAX")
        #result2table(revenues, self)
        #Fact.storeFacts(revenues, "REVENUE_AFTER_TAX")
        #Fact.fact2Table("REVENUE_AFTER_TAX.REVENUE_AFTER_TAX", self)    

        #------------------
        # Test sm2
        #------------------
        
        result = Fact.calculate("NET_REVENUE.NET_REVENUE","6/1/14")
        self.response.write("\n NET_REVENUE:" + str(result) + "\n")

        result = Fact.calculate("TAXES.TAXES","6/1/14")
        self.response.write("\n TAXES:" + str(result)+ "\n")

        result = Fact.calculate("REVENUE_AFTER_TAX.REVENUE_AFTER_TAX", "6/1/14")
        self.response.write("\n REVENUE_AFTER_TAX:" + str(result)+ "\n")

        #------------------
        # KPI_Margin
        #------------------
        # KPI_MARGIN = REVENUE_AFTER_TAX / NET_REVENUE


def result2table(result, web):
    web.response.write("\n-----------TABLE------------\n")
    [rows, header] = result
    for col in header:
        web.response.write(col + " | ")
    web.response.write("\n-----------------------------------------------------------------")
    for row in rows:
        web.response.write("\n|")
        for col in row:
            web.response.write(str(col)+ " | ")
    web.response.write("\n-----------------------------------------------------------------")
    
 
application = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/upload', UploadHandler),
    ('/tests', Tests),
], debug=True)
