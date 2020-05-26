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

from time import time
from sys import argv
from string import printable
import json
import dbm

from nltk.stem.snowball import SnowballStemmer # This is Porter2
from nltk.tokenize import word_tokenize

first_letters = sorted(printable)
first_letters = {key:value for value, key in enumerate(first_letters)}

with dbm.open("meta_index", 'c') as meta_index_file:
    meta_index = [(key.decode("UTF-8"),meta_index_file[key].decode("UTF-8")) \
        for key in sorted(meta_index_file)]

def lookUp(query_token):
    for key, value in meta_index:
        if query_token <= key:
            with open(value, 'r', encoding="UTF-8") as index:
                for line in index:
                    sep = line.rfind(":")
                    token = line[:sep]
                    if token == query_token:
                        return [entry.split(',')[0] for entry in \
                            line[line.rfind(":")+1:].rstrip(';\n').split(';')]
            return []

def search(query: str, number_of_results=5) -> dict:

    start_time = time()
    return_dict = {}
    query_tokens = word_tokenize(query)

    if len(query_tokens) == 0:
        return {'result' : '', 'time': 0.0}
    
    stemmer = SnowballStemmer("english") # NOTE: ASSUMING QUERY IS IN ENGLISH
    tokens = {stemmer.stem(token) for token in query_tokens}
    hash_map = {}
    for token in tokens:
        docIDs = lookUp(token)
        print(docIDs)
        if docIDs == []:
            return {"result":"", "time":time()-start_time}
        hash_map[token] = docIDs
        
    # for letter in {token[0] for token in tokens}:
    #     i = first_letters[letter]
    #     with open(f"char_indexes/index-{i}.txt", 'r', encoding="UTF-8") as index:
    #         for line in index:
    #             token = line[:line.rfind(":")]
    #             if token in tokens:
    #                 tokens.remove(token)
    #                 hash_map[token] = [entry.split(',')[0] for entry in \
    #                     line[line.rfind(":")+1:].rstrip(';\n').split(';')]
    #                 if len(tokens) == 0:
    #                     break
    
    return_dict['result'] = []

    docid = list(hash_map.values())

    if docid != []:
        result = list(set(docid[0]).intersection(*docid))

        if len(tokens) == 0:
            return_dict['n_documents'] = len(result) 

            with open('./document-id-convert.json', 'r') as json_file:

                data = json.load(json_file)
                
                for docid in result[:number_of_results]:
                    url = data[docid]
                    return_dict['result'].append(url)
        end_time = time()
        return_dict['time'] = round(end_time - start_time, 4)
    else:
        end_time = time()
        return_dict['time'] = round(end_time - start_time, 4)
    
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
