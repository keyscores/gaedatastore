from google.appengine.ext import ndb 
import logging

from correspondingfacts import CorrespondingFacts

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
            logging.info(last_fact_name + "=>" + step)
            [last_table, last_col] = last_fact_name.split(".") 
            [next_table, next_col] = step.split(".")
            if last_table == next_table:
                logging.info("INTRA")
                logging.info(last_table + next_table)
                old_facts = facts
                facts = []
                for fact in old_facts:
                    logging.info("STEP:" + step)
                    logging.info("FACT:" + str(fact))
                    new_fact =  fact.getCorrespondingIntraFact(step)
                    logging.info(str(new_fact))
                    facts.append(new_fact)
            else:
                 logging.info("INTER")
                 old_facts = facts
                 facts = []
                 for fact in old_facts:
                     logging.info("STEP:" + step)
                     logging.info("FACT:" + str(fact))
                     new_facts =  fact.getCorrespondingInterFact(step)
                     for new_fact in new_facts:
                         logging.info("Add new fact" + str(new_fact))
                         facts.append(new_fact)
            last_fact_name = step    
        return facts    

    @staticmethod
    def calculate(old_table_name, date_str=None, dimlevel_str=None):
        [old_table, old_fact] = old_table_name.split(".")
        date_name = old_table + "." + "Date (PST)"
        logging.info(date_name)
        
        using_filter = False
        if not(date_str == None):
            using_filter = True
            date_facts = Fact.query(Fact.name == date_name, Fact.value == date_str)
            date_keys = []
            for date_key in date_facts.iter(keys_only=True):
                logging.info(date_key.get().value)
                cfacts = date_key.get().corresponding_facts.get()
                date_keys.append(cfacts.getFact(old_table_name).key)
        
        facts = Fact.query(Fact.name == old_table_name)
        total_sum = 0
        for fact in facts:
            if using_filter:
                if fact.key in date_keys:
                    total_sum = total_sum + float(fact.value)
            else:
                total_sum = total_sum + float(fact.value)

        return total_sum    
            

    @staticmethod
    def binaryOperation(first_fact_name, 
                        dim_links,
                        operation,
                        new_table_name):
         facts = Fact.query(Fact.name==first_fact_name)
         new_rows = []
         header = []
         header.append(new_table_name + "." + new_table_name)
         target_header = []
         fact_counter = 0
         for fact in facts:
             # handle header source table
             if fact_counter == 0:
                 header = header + \
                     fact.corresponding_facts.get().getCols(new_table_name)
                 header_cols_source = \
                     fact.corresponding_facts.get().getCols("")
             counter = 0
             for link in dim_links:
                 cfacts = fact.getCorrespondingChainFact(link)
                 if counter > 0:
                     cfacts_ids = []
                     for cfact in cfacts:
                          cfacts_ids.append(cfact.key.id())
                     oldfacts_ids = []
                     for oldfact in old_facts:
                         oldfacts_ids.append(oldfact.key.id())
                     resulting_ids = \
                         list((set(oldfacts_ids).intersection(set(cfacts_ids))))    
                     old_facts = []
                     for resulting_id in resulting_ids:
                         old_facts.append(ndb.Key(Fact,resulting_id).get())
                 else:
                     old_facts = cfacts
                 counter += 1
             results = []     
             target_fact = old_facts[0]
             result = "error"
             if operation == "*":
                 result = str(float(fact.value) * float(target_fact.value.replace("%","")))
                 logging.info("******************BINARY OP:(result)" + result)
                 # FIXXXXXXXXXXMEEEEEEEEEE % HACK
                 if "%" in target_fact.value:
                     result = str(float(result) / 100)
             if operation == "-":        
                 result = str(float(fact.value) - float(target_fact.value.replace("%","")))
             results.append(result)

             # handle header target table
             if fact_counter == 0:
                 header_cols_target = \
                     target_fact.corresponding_facts.get().getCols("")
                 header_target = \
                      target_fact.corresponding_facts.get().getCols(new_table_name)
                 col_counter = 0
                 for col in header_cols_target:
                     if not(col in header_cols_source):
                         header.append(header_target[col_counter])
                         target_header.append(header_target[col_counter])
                     col_counter += 1    
                 
             logging.info(fact)
             # handle source values
             cfacts = fact.corresponding_facts.get()
             logging.info(cfacts)
             for fact_key in cfacts.facts:
                 results.append(fact_key.get().value)
                 logging.info("-------------" + str(fact.key.id()))

             # handle target values
             cfacts = target_fact.corresponding_facts.get()    
             for fact_key in cfacts.facts:
                 [current_table, current_col] = fact_key.get().name.split(".")
                 current_col_name = new_table_name + "." + current_col
                 if current_col_name in target_header:
                     results.append(fact_key.get().value)
             
             new_rows.append(results)   
             fact_counter +=1
         return [new_rows, header]

    @staticmethod
    def fact2Table(fact_name, web):
        web.response.write("\n" + fact_name)
        facts = Fact.query(Fact.name==fact_name)
        counter = 0
        for fact in facts:
            counter += 1
            if counter == 1:
                web.response.write("\n" + str(fact.corresponding_facts.get().names))
            web.response.write("\n")
            corresponding_facts = fact.corresponding_facts
            cfacts = corresponding_facts.get().facts
            for cfact in cfacts:
                web.response.write("|" + cfact.get().value)

    @staticmethod
    def facts2Table(facts, web):
        counter = 0
        for fact in facts:
            counter += 1
            corresponding_facts = fact.corresponding_facts
            if (counter == 1):
                web.response.write("\n")
                web.response.write(corresponding_facts.get().names)
                web.response.write("\n")
            web.response.write("\n" + fact.value)
            cfacts = corresponding_facts.get().facts
            for cfact in cfacts:
                web.response.write(" | " + cfact.get().value)

    @staticmethod
    def storeFacts(results, table_name):
        [rows, header] = results
        for row in rows:
            col_counter = 0
            corresponding_facts = CorrespondingFacts()
            corresponding_facts.put()
            fact_keys = []
            for col in row:
                fact = Fact(value = col,
                        name = header[col_counter],
                        corresponding_facts = corresponding_facts.key)
                fact.put()
                fact_keys.append(fact.key)
                col_counter += 1
            corresponding_facts.facts = fact_keys
            corresponding_facts.names = header
            corresponding_facts.put()


    def __str__(self):
        return "FACT: name:" + self.name + \
            ", value: " + self.value + \
            ", date: " + str(self.date) + \
            ", facts: " + str(self.corresponding_facts)
