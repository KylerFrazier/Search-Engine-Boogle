import pickle

def printNumTokens():
    with open("index.pickle", "rb") as index_file:
        hash_table = pickle.load(index_file)
        print("Number of tokens =", len(hash_table))

if __name__ == "__main__":
    printNumTokens()
