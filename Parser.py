import os
import json

from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup

class Indexer(object):

    def __init__(self, DEV: str):

        # If dir not found raise error
        if not os.path.exists(DEV):
            raise FileNotFoundError
            
        self.DEV = DEV
        self.sub_dir = [sub.path for sub in os.scandir(self.DEV) if sub.is_dir()]

        #self.sub_dir = self.sub_dir[:1] # for testing

    def index(self) -> None:

        for sub in self.sub_dir:
            json_files = [os.path.join(sub, json_file) for json_file in os.listdir(sub)\
                            if os.path.isfile(os.path.join(sub, json_file))]

            for json_file in json_files:
                with open(json_file, 'r') as f:
                    data = json.load(f)     

                    #documentID = get_documentID(data['url']) # Need to define get_documentID
                    tree = BeautifulSoup(data['content'], 'lxml')

                    tokens = [token.lower() for token in word_tokenize(tree.get_text()) if len(token) >= 2]

                    #update_index(documentID, tokens)

                    

p = Indexer('DEV')
p.index()
