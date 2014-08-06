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
    header = reader.next()
        

    for row in reader:
        col_counter = 0
        corresponding_facts = CorrespondingFacts()
        corresponding_facts.put()
        fact_keys = []
        date_str = row[4]
        for col in row:
            logging.info(col + "/n")
            fact = Fact(value = col, 
                        name = header[col_counter],
                        corresponding_facts = corresponding_facts.key,
                        date = datetime.datetime.strptime(date_str, '%m/%d/%y').date())

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
   
        # summary of all facts
        self.response.write("facts:")
        facts = Fact.query()
        for fact in facts:
            self.response.write(str(fact) + "\n")


        self.response.write("****************\n")        
        self.response.write("*   TESTS      *\n")
        self.response.write("****************\n") 

        # Net Revenue
        self.response.write("-------------\n")
        self.response.write("Net Revenue 6/1/14:\n")
        Fact.AddFactByMultiplication('Units', 'Royalty Price','Net Revenue')
        date_060114 = datetime.datetime.strptime('6/1/14', '%m/%d/%y').date()
        net_revenues = Fact.query(Fact.name=="Net Revenue", Fact.date == date_060114)
        net_revenue_sum = 0
        for fact in net_revenues:
            self.response.write(str(fact) + "\n")
            net_revenue_sum += int(fact.value)
        self.response.write("Net Revenue sum:" + str(net_revenue_sum))    

         # Filter
        self.response.write("-------------\n")
        self.response.write("Units filter by \
                             Vendor Identifier:0268_20140114_SOFA_ENGLISHTEACHER):\n")
        filtered_facts = Fact.FilterByDimLevel('Units', 
                                               'Vendor Identifier',
                                               '0268_20140114_SOFA_ENGLISHTEACHER')
        for fact in filtered_facts:
            self.response.write(str(fact) + "\n")




class CorrespondingFacts(ndb.Model):
    names = ndb.StringProperty(repeated = True)
    facts = ndb.KeyProperty(repeated = True)

    def getFact(self, name):
        logging.info("-----------" +name)
        indices = [i for i, elem in enumerate(self.names) if name in elem]
        return self.facts[indices[0]].get()


class Fact(ndb.Model):
    value = ndb.StringProperty()
    name = ndb.StringProperty()
    date = ndb.DateProperty()
    corresponding_facts = ndb.KeyProperty()

    @staticmethod
    def AddFactByMultiplication(first_fact_name, 
                 second_fact_name,
                 measure_name):
         facts = Fact.query(Fact.name==first_fact_name)
         for fact in facts:
             corresponding_facts = fact.corresponding_facts.get()
             second_fact = corresponding_facts.getFact(second_fact_name)
             result = int(fact.value) * int (second_fact.value)
             new_fact = Fact(value = str(result), 
                        name = measure_name,
                        corresponding_facts = fact.corresponding_facts,
                        date = fact.date)
             new_fact.put()
             
    @staticmethod
    def FilterByDimLevel(fact_name, 
                         dim_name,
                         level_name):
        facts = Fact.query(Fact.name == dim_name)
        filtered_facts = []
        for fact in facts:
            if (fact.value == level_name):
                corresponding_facts = fact.corresponding_facts.get()
                target_fact = corresponding_facts.getFact(fact_name)
                filtered_facts.append(target_fact)
        return filtered_facts     

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
