import os
import json
from queue import Queue
from math import ceil, log10
from collections import defaultdict

from buffer import ReadBufferWithPosting

SIZE_CAP = 2500
NUM_DOCS = 0

def mergePostings(postings: set) -> str:
    merged = next(iter(postings)).token + ":"
    all_ids = {}
    for posting in postings:
        all_ids.update(posting.ids)
    for key in sorted(all_ids):
        merged += str(key) + all_ids[key] + ';'
    return merged + "\n"

def dump_to_files(output, big_file_name, sub_file_name):
    sub_path = os.path.join('.', "sub_indexes")
    
    if not os.path.exists(sub_path):
        os.mkdir(sub_path)

    with open(big_file_name, 'a', encoding="UTF-8") as big_file, \
         open(sub_path+"/"+sub_file_name, 'w', encoding="UTF-8") as sub_file, \
         open("meta_index.txt", 'a', encoding="UTF-8") as meta_file:
        
        while not output.empty():
            line = output.get()
            sep = line.rfind(':')+1
            line = line.rstrip() + "*" + str( round( log10(
                NUM_DOCS / line[sep:].count(";") ), 4 ) ) + "\n"
            big_file.write(line)
            sub_file.write(line)
        meta_file.write(line[:line.rfind(':')] +"*"+ sub_path+"/"+sub_file_name +"\n")

def merge() -> None:
    global NUM_DOCS

    with open("index_info.json", "r") as index_info_file:
        index_info = json.load(index_info_file)
        NUM_DOCS = index_info["NUM_DOCS"]

    # Get's a list of all file names that are partial indexes
    partial_index_names = {index for index in os.listdir('./partial_indexes') \
        if index.endswith('.txt') and index[:5] == "index"}

    if 'index.txt' in partial_index_names:
        partial_index_names.remove('index.txt')

    # Make new file which is the final index
    with open('index.txt', 'w', encoding="UTF-8") as _, \
         open("meta_index.txt", 'w', encoding="UTF-8") as _:
        pass

    buffer_size = ceil( SIZE_CAP / len(partial_index_names) )
    partial_indexes = set()

    for index in partial_index_names:
        try:
            opened_index = ReadBufferWithPosting("partial_indexes/"+index, buffer_size)
            partial_indexes.add(opened_index)
        except:
            print(f"{index} could not be opened for merging")

    output = Queue(SIZE_CAP)
    file_num = 0

    while partial_indexes:
        
        # Get a set of indexes that are on the lowest ordered string
        lowest = next(iter(partial_indexes)).token
        lowest_set = set()
        for index in partial_indexes:
            if index.token < lowest:
                lowest = index.token
                lowest_set.clear()
                lowest_set.add(index)
            elif index.token == lowest:
                lowest_set.add(index)

        # Merge postings and add to output buffer
        output.put(mergePostings(lowest_set))
        for index in lowest_set:
            index.readline()

        # Remove indexes that fully read
        done = {index for index in partial_indexes if index.line == ""}
        for index in done: partial_indexes.remove(index)

        # Once the queue is full, dump to file
        if output.full():
            dump_to_files(output, "index.txt", f"index-{file_num}.txt")
            file_num += 1
    
    dump_to_files(output, "index.txt", f"index-{file_num}.txt")

if __name__ == "__main__":
    merge()
