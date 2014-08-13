from google.appengine.ext import ndb
import logging

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
        
    def __str__(self):
        name_str = "\n"
        for name in self.names:
            name_str = name_str + " | " + name
        value_str = "\n"
        for key in self.facts:
            fact = key.get()
            value_str = value_str + " | " + fact.value
        return name_str + value_str   

