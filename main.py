from Indexer import Indexer
from merger import merge
from num_tokens import printNumTokensQuickFix
from doc_id_handler import initJSON

if __name__ == '__main__':

    print('kek')
    initJSON()
    indexer = Indexer('DEV')
    indexer.index()

    # merge()
    # print("Number of Tokens =", printNumTokensQuickFix())
