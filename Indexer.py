import os
import json

from nltk.tokenize import word_tokenize
from nltk import FreqDist
from nltk.stem.snowball import SnowballStemmer # This is Porter2
from bs4 import BeautifulSoup
from collections import defaultdict
from warnings import filterwarnings

from Posting import Posting
from doc_id_handler import save_documents

class Indexer(object):

    def __init__(self, DEV: str) -> None:

        # If dir not found raise error
        if not os.path.exists(DEV):
            raise FileNotFoundError
            
        self.DEV = DEV
        self.corpus = [sub.path for sub in os.scandir(self.DEV) if sub.is_dir()]

        print("Creating corpus\n")
        self.corpus = [os.path.join(sub, json_file) for sub in self.corpus \
            for json_file in os.listdir(sub) \
            if os.path.isfile(os.path.join(sub, json_file))]

        print(f"Corpus size:{len(self.corpus)}\n")

    def get_batch(self, n_batch=3):
    
        n = int(len(self.corpus) / n_batch)
        for idx in range(0, n_batch - 1):
            yield self.corpus[idx * n : n * (idx + 1)]

        yield self.corpus[n * (n_batch - 1):]

    def index(self) -> None:
        
        filterwarnings("ignore", category=UserWarning, module='bs4')
        stemmer = SnowballStemmer("english") # NOTE: ASSUMING LANG IS ENGLISH
        docid = 0

        for i, batch in enumerate(self.get_batch(20)):

            print(f"==================== Batch - {i} ====================")
            print(f"Batch-{i} has {len(batch)} documents")
            print()
            
            HashTable = defaultdict(list)
            docid_table = {}

            for json_file in batch:
                
                with open(json_file, 'r') as document:
                    data = json.load(document)

                    docid_table[docid] = data["url"]

                    tree = BeautifulSoup(data['content'], 'lxml')
                    tokens = [stemmer.stem(token) for token in \
                        word_tokenize(tree.get_text())]
                    freq_dist = FreqDist(tokens)

                    for token, freq in freq_dist.items():
                        HashTable[token].append(Posting(docid, freq))

                    del freq_dist
                    del data
                    docid += 1

            save_documents(docid_table)

            self.writeIndexToFile(HashTable, i)

            del batch
            HashTable.clear()
            docid_table.clear()

        print(f"Number of documents = {docid}\n")

    def writeIndexToFile(self, HashTable, file_num):

        partial_indexes = os.path.join('.', "partial_indexes")
        
        if not os.path.exists(partial_indexes):
            os.mkdir(partial_indexes)

        with open(f"{partial_indexes}/index-{file_num}.txt", 'w', encoding="UTF-8") as text_file:
            for token in sorted(HashTable):
                posting_list = HashTable[token]
                posting_str = f"{token}:"
                for posting in posting_list:
                    posting_str += ",".join(posting.get_values()) + ";"
                text_file.write(posting_str)
                text_file.write("\n")
