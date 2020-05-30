import os
import shutil
import json
from math import ceil, log10

from nltk.tokenize import word_tokenize
from nltk import FreqDist
from nltk.stem.snowball import SnowballStemmer # This is Porter2
from bs4 import BeautifulSoup
from collections import defaultdict
from warnings import filterwarnings

from Posting import Posting
from doc_id_handler import save_documents

from util import simhash, find_similar

MAX_DOCS = 1000
special_tag_weights = {'title': 3, 'h1': 2, 'h2': 1, 'h3': 1, 'b': 1, 'strong': 1}
URL_WEIGHT = 3
special_tags = [key for key in special_tag_weights]

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

        print(f"Corpus size: {len(self.corpus)}\n")

        # Create directory for finger_prints
        if os.path.exists('./finger_prints'):
            shutil.rmtree('./finger_prints')
        os.mkdir('./finger_prints')

    def get_batch(self, n_batch=3):
    
        n = int(len(self.corpus) / n_batch)
        for idx in range(0, n_batch - 1):
            yield self.corpus[idx * n : n * (idx + 1)]

        yield self.corpus[n * (n_batch - 1):]

    def index(self) -> None:
        
        filterwarnings("ignore", category=UserWarning, module='bs4')
        stemmer = SnowballStemmer("english") # NOTE: ASSUMING LANG IS ENGLISH
        docid = 0
        
        for i, batch in enumerate(self.get_batch(ceil(len(self.corpus)/MAX_DOCS))):

            print(f"==================== Batch - {i} ====================")
            print(f"Batch-{i} has {len(batch)} documents")
            starting_docID = docid

            HashTable = defaultdict(list)
            docid_table = {}

            for json_file in batch:
                
                with open(json_file, 'r') as document:
                    data = json.load(document)

                    docid_table[docid] = data["url"]

                    tree = BeautifulSoup(data['content'], 'lxml')
                    
                    freq_dist = defaultdict(int)
                    previous = ""

                    for token in word_tokenize(tree.get_text()):
                        token = stemmer.stem(token)
                        freq_dist[token] += 1
                        if previous:
                            freq_dist[previous + " " + token] += 1
                        previous = token

                    finger_print = simhash(freq_dist)
                    if find_similar(finger_print):
                        continue

                    # Add more weights to special tags
                    for special in tree.findAll(special_tags):
                        previous = ""

                        # Update single token
                        for token in word_tokenize(str(special.string)):
                            token = stemmer.stem(token)
                            weight = special_tag_weights[special.name]
                            freq_dist[token] += weight
                            if previous:
                                freq_dist[previous + " " + token] += weight
                            previous = token

                    # Add URLs
                    for token in word_tokenize(data["url"]):
                        freq_dist[stemmer.stem(token)] += URL_WEIGHT
                    for anchor in tree.findAll('a', href=True):
                        for token in word_tokenize(anchor['href']):
                            freq_dist[stemmer.stem(token)] += 1

                    for token, freq in freq_dist.items():
                        HashTable[token].append(Posting(docid, round(1+log10(freq), 5)))

                    del freq_dist
                    del data
                    docid += 1

            save_documents(docid_table)

            self.writeIndexToFile(HashTable, i)

            del batch
            HashTable.clear()
            docid_table.clear()

            print(f"Batch-{i} added {docid - starting_docID} documents")
            print()

        print(f"Number of documents = {docid}\n")
        with open("index_info.json", "w") as index_info:
            json.dump({"NUM_DOCS" : docid}, index_info, indent=4)

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
