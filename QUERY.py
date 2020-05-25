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
from nltk.stem.snowball import SnowballStemmer # This is Porter2
from string import printable

import json
from rank import tfidf

first_letters = sorted(printable)
first_letters = {key:value for value, key in enumerate(first_letters)}

def search(query: list, number_of_results=5) -> dict:

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

                        posting_list = [entry.split(',') for entry in line[line.rfind(':')+1:].rstrip(';\n').split(';')]
                        posting_list = list(map(lambda posting: (posting[0], posting[1]), posting_list))

                        hash_map[token] = {
                                'docid': [posting[0] for posting in posting_list], 
                                'tf': [posting[1] for posting in posting_list]
                        }

                        if len(tokens) == 0:
                            break
        
        obj['result'] = []

        docid = [posting['docid'] for posting in hash_map.values()]

        if docid != []:
            result = list(set(docid[0]).intersection(*docid))

            if len(tokens) == 0:
                obj['n_documents'] = len(result) 

                score = tfidf(hash_map, result) 
                print(score)

                with open('./document-id-convert.json', 'r') as json_file:

                    data = json.load(json_file)
                    
                    for i, docid in enumerate(sorted(score.items(), key=lambda docid: docid[1], reverse=True)):
                        if i >= number_of_results:
                            break

                        url = data[docid[0]]
                        obj['result'].append(url)

            end_time = time()
            obj['time'] = round(end_time - start_time, 4)
    
    return obj

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

    query = (argv[1:])

    results = search(query)
    
    print(f"\n                  ({results['time']} seconds)\n")
    print("Results:")
    for result in results['result']:
        print(f" > {result}")
    print()
