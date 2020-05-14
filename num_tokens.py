import pickle

def getNumTokens():
    num_tokens = 0
    with open("index.txt", "r", encoding="UTF-8") as index_file:
        for _ in index_file:
            num_tokens += 1
    return num_tokens

if __name__ == "__main__":
    print("Number of Tokens =", getNumTokens())
