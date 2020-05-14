from Indexer import Indexer
from merger import merge
from num_tokens import getNumTokens
from doc_id_handler import initJSON

if __name__ == '__main__':

    print()
    initJSON()

    print("<<< INDEXING >>>\n")
    indexer = Indexer('DEV')
    indexer.index()

    print("<<< MERGING >>>\n")
    merge()
    print("\nNumber of Tokens =", getNumTokens())
