from time import time
from sys import argv
from nltk.stem.snowball import SnowballStemmer # This is Porter2
from string import printable

import json

first_letters = sorted(printable)
first_letters = {key:value for value, key in enumerate(first_letters)}

def search(query: list, k=5) -> dict:

    start_time = time()

    obj = {}

    if len(query) == 0:
        obj['result'] = ''  
        obj['time'] = 0
        
    else:

        stemmer = SnowballStemmer("english") # NOTE: ASSUMING QUERY IS IN ENGLISH
        tokens = {stemmer.stem(token) for token in query}
        hash_map = {}

        for letter in {token[0] for token in tokens}:
            i = first_letters[letter]
            with open(f"char_indexes/index-{i}.txt", 'r', encoding="UTF-8") as index:
                for line in index:
                    token = line[:line.rfind(":")]
                    if token in tokens:
                        tokens.remove(token)
                        hash_map[token] = [entry.split(',')[0] for entry in \
                            line[line.rfind(":")+1:].rstrip(';\n').split(';')]
                        if len(tokens) == 0:
                            break
        
        end_time = time()

        obj['result'] = []

        docid = list(hash_map.values())

        if docid != []:
            result = list(set(docid[0]).intersection(*docid))

            if len(tokens) == 0:
                obj['n_documents'] = len(result) 

                with open('./document-id-convert.json', 'r') as json_file:

                    data = json.load(json_file)
                    
                    for docid in result[:k]:
                        url = data[docid]
                        obj['result'].append(url)

            obj['time'] = round(end_time - start_time, 4)

    return obj

if __name__ == "__main__":
    start_time = time()

    if len(argv) == 1:
        print("Please provide a query.")
        exit(0)
    query = argv[1:]

    stemmer = SnowballStemmer("english") # NOTE: ASSUMING QUERY IS IN ENGLISH
    tokens = {stemmer.stem(token) for token in query}
    hash_map = {}

    for letter in {token[0] for token in tokens}:
        i = first_letters[letter]
        print(i)
        with open(f"char_indexes/index-{i}.txt", 'r', encoding="UTF-8") as index:
            for line in index:
                token = line[:line.rfind(":")]
                if token in tokens:
                    tokens.remove(token)
                    hash_map[token] = [entry.split(',')[0] for entry in \
                        line[line.rfind(":")+1:].rstrip(';\n').split(';')]
                    if len(tokens) == 0:
                        break

    # with open("index.txt", 'r', encoding="UTF-8") as index:
    #     for line in index:
    #         token = line[:line.rfind(":")]
    #         if token in tokens:
    #             tokens.remove(token)
    #             hash_map[token] = [entry.split(',')[0] for entry in \
    #                 line[line.rfind(":")+1:].rstrip(';\n').split(';')]
    #             if len(tokens) == 0:
    #                 break

    end_time = time()

    if len(tokens) > 0:
        print("Query found no matches.")
    else:
        docid = list(hash_map.values())
        result = set(docid[0]).intersection(*docid)
        result = list(result)
        print(result[:5])
    
    print(f"\nQuery time = {round(end_time - start_time, 4)} sec\n")
