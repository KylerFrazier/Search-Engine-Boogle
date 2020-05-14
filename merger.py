import os
import pickle

from collections import deque

def merge() -> None:

    partial_index = deque([index for index in os.listdir('.') if index.endswith('.pickle')])

    if 'index.pickle' in partial_index:
        partial_index.remove('index.pickle')

    if not os.path.exists('index.pickle'):
        with open('index.pickle', 'w') as _:
            pass
    

    while len(partial_index) != 1:

        index1 = partial_index.popleft()
        index2 = partial_index.popleft()

        with open(index1, 'rb') as file1:
            index1_dict = pickle.load(file1)

        with open(index2, 'rb') as file2:
            index2_dict = pickle.load(file2)

        for token, posting in index2_dict.items():
            if token in index1_dict.keys():
                index1_dict[token].extend(posting)

            else:
                index1_dict.update({token:posting})

        with open('index.pickle', 'wb') as index:
            pickle.dump(index1_dict, index)

        index1_dict.clear()
        index2_dict.clear()
        partial_index.appendleft('index.pickle')


