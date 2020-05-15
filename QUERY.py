from time import time
from sys import argv
from nltk.stem.snowball import SnowballStemmer # This is Porter2
from string import printable

first_letters = sorted(printable)
first_letters = {key:value for value, key in enumerate(first_letters)}

def search(argv):
    start_time = time()

    if len(argv) == 0:
        print("Please provide a query.")
        exit(0)
    query = argv

    stemmer = SnowballStemmer("english") # NOTE: ASSUMING QUERY IS IN ENGLISH
    tokens = {stemmer.stem(token) for token in query}
    hash_map = {}

    with open("index.txt", 'r', encoding="UTF-8") as index:
        for line in index:
            token = line[:line.rfind(":")]
            if token in tokens:
                tokens.remove(token)
                hash_map[token] = [entry.split(',')[0] for entry in \
                    line[line.rfind(":")+1:].rstrip(';\n').split(';')]
                if len(tokens) == 0:
                    break
    
    end_time = time()

    docid = list(hash_map.values())
    result = set(docid[0]).intersection(*docid)
    print(result)
    result = list(result)
    
    if len(tokens) > 0:
        print("Query found no matches.")
        return []

    else:
        print(result[:5])
    
    print(f"\nQuery time = {round(end_time - start_time, 4)} sec\n")

    return result[:5]

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
