import os
import json
import pickle

from nltk.tokenize import word_tokenize
from nltk import FreqDist
from bs4 import BeautifulSoup
from collections import defaultdict

from Posting import Posting

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
        HashTable = defaultdict(list)

        for i, batch in enumerate(self.get_batch()):

            print('###################################################################')
            print(f"######################### Batch - {i} ###############################")
            print('###################################################################')
            print(f"Batch-{i} has {len(batch)} documents")
            print()


            for json_file in batch:
                docid = docid + 1

                with open(json_file, 'r') as document:
                    data = json.load(document)

                    self.save_document(docid, data['url'])

                    tree = BeautifulSoup(data['content'], 'lxml')
                    tokens = [token.lower() for token in word_tokenize(tree.get_text()) if len(token) >= 2]
                    freq_dist = FreqDist(tokens)

                    tokens = set(tokens) # Remove duplicates

                    for token in tokens:
                        HashTable[token].append(Posting(docid, freq_dist[token]))

                del freq_dist
                del data

            with open(f"index-{i}.pickle", 'wb') as pickle_file:
                pickle.dump(HashTable, pickle_file)

            HashTable.clear()
            del batch

        print()
        print(f"Number of documents = {docid}")

    def save_document(self, docid: int, url: str) -> None:
        
        if not os.path.exists('document-id-convert.json'):
            with open('document-id-convert.json', 'w') as json_file:
                json.dump({docid: url}, json_file)

        else:

            with open('document-id-convert.json', 'r') as json_file:
                convert = json.load(json_file)

            if docid in convert.keys() or url in convert.values():
                return

            convert.update({docid: url})

            with open('document-id-convert.json', 'w') as json_file:
                json.dump(convert, json_file)

