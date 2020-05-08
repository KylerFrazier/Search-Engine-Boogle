from Indexer import Indexer
from merger import merge
from num_tokens import printNumTokens
from doc_id_handler import initJSON

if __name__ == '__main__':

    print('kek')
    initJSON()
    indexer = Indexer('DEV')
    indexer.index()

    merge()
    printNumTokens()
