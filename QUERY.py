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
from math import log10, sqrt
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

# Returns the a dictionary of docIDs and their respective token vectors
#   after intersecting for all unary tokens, and 2grams when possible
def intersectAndMakeVector(hash_map: { str : [ [int] ] } ) -> dict:
    i = {token:0 for token in hash_map}
    is_2gram = {token:True if " " in token else False for token in hash_map}
    vectors = defaultdict(dict)
    normalize = defaultdict(float)
    done = False
    while not done:
        first_token = next(iter(hash_map))
        max_id = hash_map[first_token][i[first_token]][0]
        in_all = True
        for token, postings in hash_map.items():
            docID = postings[i[token]][0]
            if docID < max_id:
                in_all = False
            if docID > max_id and not is_2gram[token]:
                max_id = docID
                in_all = False
        if in_all:
            for token, postings in hash_map.items():
                posting = postings[i[token]]
                docID = posting[0]
                tf = posting[1] if docID == max_id else 0
                vectors[max_id][token] = tf
                normalize[max_id] += tf**2
                i[token] += 1
                if i[token] >= len(postings): done = True
        else:
            done_2grams = []
            for token, postings in hash_map.items():
                while postings[i[token]][0] < max_id:
                    i[token] += 1
                    if i[token] >= len(postings): 
                        if is_2gram[token]:
                            done_2grams.append(token)
                        else:
                            done = True
                        break
            for token in done_2grams:
                hash_map.pop(token)
    for docID, vector in vectors.items():
        norm = sqrt(normalize[docID])
        for token in vector:
            vector[token] /= norm
    return vectors

# Go through a sub-index and check for the tokens that might be in it
#   If there are missing 2grams, still allow the query to continue
def lookUp(file_name: str, tokens: set, idfs: dict) -> { str : [ [int] ] } :
    hashMap = {}
    with open(file_name, 'r', encoding="UTF-8") as index:
        for line in index:
            sep = line.rfind(":")
            sep2 = line.rfind("*")
            token = line[:sep]
            if token in tokens:
                tokens.remove(token)
                hashMap[token] = [[float(i) for i in entry.split(',')] \
                    for entry in line[sep+1:sep2].rstrip(';').split(';')]
                idfs[token] = float(line[sep2+1:].rstrip())
                if not tokens:
                    return hashMap
    for token in tokens:
        if " " not in token:
            return {}
        idfs[token] = 0
        hashMap[token] = [[-1,0]]
    return hashMap

def search(query: str, number_of_results=10) -> dict:

    start_time = time()
    hash_map = {}       # { token : [docIDs] }
    idfs = {}           # { token : idf }

    # Process Query
    query_tokens = word_tokenize(query)
    if len(query_tokens) == 0: return {'result' : '', 'time': 0.0}
    stemmer = SnowballStemmer("english") # NOTE: ASSUMING QUERY IS IN ENGLISH
    tokens = set()
    query_vector = defaultdict(float)
    previous = ""
    for token in query_tokens:
        t = stemmer.stem(token)
        tokens.add(t)
        query_vector[t] += 1
        if previous:
            twoGram = previous + " " + t
            tokens.add(twoGram)
            query_vector[twoGram] += 10
        previous = t

    


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

    # Get the tfidf for the query and normalize
    normalize_query = 0
    for token, freq in query_vector.items():
        tfidf = (1 + log10(freq)) * idfs[token]
        query_vector[token] = tfidf
        normalize_query += tfidf**2
    normalize_query = sqrt(normalize_query)
    for token in query_vector:
        query_vector[token] /= normalize_query
    # print("Query vector:")
    # print(query_vector)

    # Process all vectors to get final result
    return_dict = {'result' : []}   # { "result" : [URLs] , "time" : time }
    vectors = intersectAndMakeVector(hash_map) # Intersect of IDs and vectorize
    scores = defaultdict(float)
    for docID, vector in vectors.items():
        for token, tf in vector.items():
            scores[docID] += tf*query_vector[token]
    result = sorted(scores, key = lambda x : -scores[x])
            
    return_dict['n_documents'] = len(result)
    
    for docid in result[:number_of_results]:
        url = docID_to_URL[str(int(docid))]
        return_dict['result'].append(url) # +"\n\tScore: "+str(scores[docid])
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
