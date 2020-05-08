import os
import json
import pickle

from nltk.tokenize import word_tokenize
from nltk import FreqDist
from bs4 import BeautifulSoup
from collections import defaultdict

from Posting import Posting
from doc_id_handler import save_documents

class Indexer(object):

    def __init__(self, DEV: str) -> None:

        # If dir not found raise error
        if not os.path.exists(DEV):
            raise FileNotFoundError
            
        self.DEV = DEV
        self.corpus = [sub.path for sub in os.scandir(self.DEV) if sub.is_dir()]

        self.corpus = [os.path.join(sub, json_file) for sub in self.corpus \
                            for json_file in os.listdir(sub) if os.path.isfile(os.path.join(sub, json_file))]

    def get_batch(self, n_batch=3):
    
        n = int(len(self.corpus) / n_batch)
        for idx in range(0, n_batch - 1):
            yield self.corpus[idx * n : n * (idx + 1)]

        yield self.corpus[n * (n_batch - 1):]

    def index(self) -> None:
        
        docid = 0

        for i, batch in enumerate(self.get_batch()):

            print('###################################################################')
            print(f"######################### Batch - {i} ###############################")
            print('###################################################################')
            print(f"Batch-{i} has {len(batch)} documents")
            print()
            
            HashTable = defaultdict(list)
            docid_table = {}

            for json_file in batch:
                
                with open(json_file, 'r') as document:
                    data = json.load(document)

                    docid_table[docid] = data["url"]

                    tree = BeautifulSoup(data['content'], 'lxml')
                    tokens = [token.lower() for token in word_tokenize(tree.get_text()) if len(token) >= 2]
                    freq_dist = FreqDist(tokens)

                    for token, freq in freq_dist.items():
                        HashTable[token].append(Posting(docid, freq))

                    # I moved these into the "with" statement because I'm 
                    # assuming that we don't want to update docid unless
                    # the file was actually opened
                    del freq_dist
                    del data
                    docid += 1

            save_documents(docid_table)

            with open(f"index-{i}.pickle", 'wb') as pickle_file:
                pickle.dump(HashTable, pickle_file)

            del batch
            HashTable.clear()
            docid_table.clear()

            print(']\n')

        print()
        print(f"Number of documents = {docid}")
