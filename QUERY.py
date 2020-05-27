# RUNNING AS A WEBAPP:
#   On most devices, create a virtual environment with: python3 -m venv env
#   Set up the environment with: env/Scripts/activate
#   Begin flask with: Flask run
#   Open a web-browser, and go to "localhost:5000"
# INSTALLATION REQUIREMENTS through pip3:
#   nltk
#   bs4
#   flask
#   python-dotenv
# RUN IN TERMINAL:
#   Simply run: python3 Query.py <your query>

from collections import defaultdict
from time import time
from sys import argv
from queue import Queue
import json

from nltk.stem.snowball import SnowballStemmer # This is Porter2
from nltk.tokenize import word_tokenize

meta_index = [] # [(token, file)]
with open("meta_index.txt", 'r', encoding="UTF-8") as meta_index_file:
    for line in meta_index_file:
        line = line.rstrip()
        if line != "":
            sep = line.rfind('*')
            meta_index.append( ( line[:sep] , line[sep+1:] ) )

with open('./document-id-convert.json', 'r') as json_file:
    docID_to_URL = json.load(json_file)

def intersectAndRank(hash_map: { str : [ [int] ] } ) -> [int]:
    i = {token:0 for token in hash_map}
    ranked = defaultdict(float)
    done = False
    while not done:
        first_token = next(iter(hash_map))
        max_id = hash_map[first_token][i[first_token]][0]
        in_all = True
        for token, postings in hash_map.items():
            docID = postings[i[token]][0]
            if docID != max_id:
                if docID > max_id: max_id = docID
                in_all = False
        if in_all:
            for token, postings in hash_map.items():
                posting = postings[i[token]]
                ranked[posting[0]] += posting[1]
                i[token] += 1
                if i[token] >= len(postings): done = True
        else:
            for token, postings in hash_map.items():
                docID = postings[i[token]][0]
                if docID < max_id:
                    i[token] += 1
                    if i[token] >= len(postings): done = True
    return sorted(ranked, key = lambda x : -ranked[x])

def lookUp(file_name: str, tokens: set, idfs: dict) -> { str : [ [int] ] } :
    with open(file_name, 'r', encoding="UTF-8") as index:
        hashMap = {}
        for line in index:
            sep = line.rfind(":")
            sep2 = line.rfind("*")
            token = line[:sep]
            if token in tokens:
                tokens.remove(token)
                hashMap[token] = [[int(i) for i in entry.split(',')] \
                    for entry in line[sep+1:sep2].rstrip(';').split(';')]
                idfs[token] = float(line[sep2+1:].rstrip())
                if not tokens:
                    return hashMap
    return {}

def search(query: str, number_of_results=10) -> dict:

    start_time = time()
    hash_map = {}       # { token : [docIDs] }
    idfs = {}           # { token : idf }

    # Process Query
    query_tokens = word_tokenize(query)
    if len(query_tokens) == 0: return {'result' : '', 'time': 0.0}
    stemmer = SnowballStemmer("english") # NOTE: ASSUMING QUERY IS IN ENGLISH
    tokens = {stemmer.stem(token) for token in query_tokens}

    # Make a dict of sub_indexes and the query tokens that would be in them
    search_files = defaultdict(set)
    for meta_token, file_name in meta_index:
        found = False
        for token in tokens:
            if token <= meta_token:
                search_files[file_name].add(token)
                found = True
        if found:
            for token in search_files[file_name]:
                tokens.remove(token)
    if tokens:
        return {"result":[], "time":time()-start_time}
    
    # Look for the postings in the sub_indexes and update the hash_map
    for file_name, file_tokens in search_files.items():
        docIDs = lookUp(file_name, file_tokens, idfs)
        if docIDs == {}:
            return {"result":[], "time":time()-start_time}
        hash_map.update(docIDs)

    # Process postings to get final result
    return_dict = {'result' : []}   # { "result" : [URLs] , "time" : time }
    result = intersectAndRank(hash_map) # Get intersection of ranked IDs
    return_dict['n_documents'] = len(result)
    
    for docid in result[:number_of_results]:
        url = docID_to_URL[str(docid)]
        return_dict['result'].append(url)
    return_dict['time'] = round(time() - start_time, 4)
    
    return return_dict

if __name__ == "__main__":    
    start_time = time()

    if len(argv) == 1:
        print("Please provide a query.")
        exit(0)
    
    print()
    print("#==================================================#")
    print("|                                                  |")
    print("|                      Boogle                      |")
    print("|                                                  |")
    print("#==================================================#")

    query = " ".join(argv[1:])

    results = search(query)
    
    print(f"\n                  ({results['time']} seconds)\n")
    if len(results['result']) == 0:
        print(f"No results were found for \"{query}\".\n")
    else:
        print("Search Results:")
        for result in results['result']:
            print(f" > {result}")
        print()
