import math

def tfidf(hash_map: dict, result: list, N=55393):

    tfidf_dict = {}

    for docid in result:
        score = 0

        for token, posting in hash_map.items():
            for tup in zip(posting['docid'], posting['tf']):

                if docid in tup[0]:
                    tf = 1.0 + math.log(int(tup[1]))
                    idf = math.log(N / len(hash_map[token]))

                    score += tf * idf

        tfidf_dict[docid] = score

    return tfidf_dict
