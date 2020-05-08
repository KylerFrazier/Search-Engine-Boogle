import pickle

def printNumTokens():
    with open("index.pickle", "rb") as index_file:
        hash_table = pickle.load(index_file)
        print("Number of tokens =", len(hash_table))

def printNumTokensQuickFix():
    total = set()
    for i in range(100):
        print(f"{i}%")
        with open(f"index-{i}.pickle", "rb") as index_file:
            hash_table = pickle.load(index_file)
            for token in hash_table:
                total.add(token)
            hash_table.clear()
    return len(total)

if __name__ == "__main__":
    print("Number of Tokens =", printNumTokensQuickFix())
