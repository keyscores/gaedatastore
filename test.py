import csv
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import db
from google.appengine.ext import ndb 
import logging
import datetime
 
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
        self.response.write("summary:")

        filtered_facts = Fact.query(Fact.name == 'Sales.Vendor Identifier',
                                    Fact.value ==  '0268_20140114_SOFA_ENGLISHTEACHER')
        for fact in filtered_facts:
            self.response.write(str(fact) + "\n")

        # Test Corresponding Intra Fact
        facts = Fact.query(Fact.name == "Sales.Units")
        for fact in facts:
            self.response.write(str(fact.getCorrespondingIntraFact("Sales.Royalty Price")) + "\n")

        # Test Corresponding Inter Fact
        fact_assault = Fact.query(Fact.name == "Sales.Vendor Identifier",
                                  Fact.value == "0273_20140114_SOFA_ASSAULTONWALLSTREET")
        for fact in fact_assault:
            self.response.write(str(fact) + "\n")
            corr_facts = fact.getCorrespondingInterFact("ComissionTax.Vendor Identifier")
            for corr_fact in corr_facts:
                self.response.write(str(corr_fact) + "\n")

        # Test Chain
        # Test Corresponding Inter Fact
        self.response.write("CHAIN: \n")
        fact_assaults = Fact.query(Fact.name == "Sales.Vendor Identifier",
                                   Fact.value == "0273_20140114_SOFA_ASSAULTONWALLSTREET")
        fact_assault = fact_assaults.get()
        self.response.write(fact_assaults.get())

        facts = fact_assault.getCorrespondingChainFact(["Sales.Country Code",
                                                        "CountryRegion.Country Code",
                                                        "CountryRegion.Region",
                                                        "ComissionTax.Region",
                                                        "ComissionTax.Tax Rate"])

        
        facts2 = fact_assault.getCorrespondingChainFact(["Sales.Units",
                                                        "Sales.Vendor Identifier",
                                                        "ComissionTax.Vendor Identifier",
                                                         "ComissionTax.Tax Rate"])    


class CorrespondingFacts(ndb.Model):
    names = ndb.StringProperty(repeated = True)
    facts = ndb.KeyProperty(repeated = True)

    def getFact(self, name):
        logging.info("-----------" +name)
        indices = [i for i, elem in enumerate(self.names) if name in elem]
        return self.facts[indices[0]].get()

    def getCols(self,new_table):
        cols = []
        for name in self.names:
            [table, col] = name.split(".")
            col = new_table + "." + col
            cols.append(col)
        return cols


class Fact(ndb.Model):
    value = ndb.StringProperty()
    name = ndb.StringProperty()
    date = ndb.DateProperty()
    corresponding_facts = ndb.KeyProperty()

    def getCorrespondingIntraFact(self, corresponding_fact_name):
        corresponding_facts = self.corresponding_facts.get()
        corresponding_fact = corresponding_facts.getFact(corresponding_fact_name)
        return corresponding_fact
       
    def getCorrespondingInterFact(self, corresponding_fact_name):
        return  Fact.query(Fact.name == corresponding_fact_name, 
                           Fact.value == self.value) 
        
    def getCorrespondingChainFact(self, chain):
        facts = []
        facts.append(self)
        last_fact_name = self.name;
        for step in chain:
            [last_table, last_col] = last_fact_name.split(".") 
            [next_table, next_col] = step.split(".")
            if last_table == next_table:
                old_facts = facts
                facts = []
                for fact in old_facts:
                    new_fact =  fact.getCorrespondingIntraFact(step)
                    facts.append(new_fact)
            else:
                 old_facts = facts
                 facts = []
                 for fact in old_facts:
                     new_facts =  fact.getCorrespondingInterFact(step)
                     for new_fact in new_facts:
                         facts.append(new_fact)
            last_fact_name = step    
        return facts    

    def __str__(self):
        return "FACT: name:" + self.name + \
            ", value: " + self.value + \
            ", date: " + str(self.date) + \
            ", facts: " + str(self.corresponding_facts)

 
application = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/upload', UploadHandler),
    ('/tests', Tests)
], debug=True)
