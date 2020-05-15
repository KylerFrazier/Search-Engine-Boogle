import os

from collections import defaultdict
from string import printable

def mergePostings(p1, p2):
    if int(p1[:p1.index(',')]) < int(p2[:p2.index(',')]):
        return p1.rstrip('\n') + p2
    return p2.rstrip('\n') + p1

def merge() -> None:

    # Get's a list of all file names that are partial indexes
    partial_index_names = {index for index in os.listdir('./partial_indexes') \
        if index.endswith('.txt') and index[:5] == "index"}

    if 'index.txt' in partial_index_names:
        partial_index_names.remove('index.txt')

    # Make new file which is the final index
    with open('index.txt', 'w', encoding="UTF-8") as _:
        pass
    
    first_letters = sorted(printable)   # Sorted ASCII characters
    partial_indexes = set()             # Set of all files
    next_set = set()                    # Stores files that are done per letter
    last_line = {}                      # Stores the last read line per file
    
    # Open all files and put them into partial_indexes
    for index in partial_index_names:
        try:
            opened_index = open("partial_indexes/"+index, "r", encoding="UTF-8")
            last_line[opened_index] = ""
            partial_indexes.add(opened_index)
        except:
            print(f"{index} could not be opened for merging")
    
    # For each character, merge into a buffer then dump the buffer to the file

    for i, first_letter in enumerate(first_letters):
        if i%2 == 0: print(f"Progress: {int(100*i/len(first_letters))}%")
        print(first_letter)
        buffer = {}
        while len(partial_indexes) != 0:
            remove_set = set()
            finished_set = set()
            for index in partial_indexes:
                # Read a line if the last line was used
                if last_line[index] == "":
                    line = index.readline()
                    last_line[index] = line
                else:
                    line = last_line[index]
                
                # Stop this file if EOF or the first char is doesn't match
                if line == "":
                    finished_set.add(index)
                elif line[0] != first_letter:
                    remove_set.add(index)
                else:
                    last_line[index] = ""
                    colon_i = line.rfind(":")
                    token, posting = line[:colon_i], line[colon_i+1:]
                    if token in buffer:
                        buffer[token] = mergePostings(buffer[token], posting)
                    else:
                        buffer[token] = posting
            
            # Clean up finished files
            for index in finished_set:
                partial_indexes.remove(index)
                index.close()
            for index in remove_set:
                partial_indexes.remove(index)
                next_set.add(index)
        
        # Reset for the next letter and dump content to index.txt
        partial_indexes = next_set
        next_set = set()
        with open("index.txt", 'a', encoding="UTF-8") as index_file:
            for token, posting in sorted(buffer.items()):
                index_file.write(f"{token}:{posting}")
        
        char_indexes = os.path.join('.', "char_indexes")
        if not os.path.exists(char_indexes):
            os.mkdir(char_indexes)
        with open(f"{char_indexes}/index-{i}.txt", 'w', encoding="UTF-8") as index_file:
            for token, posting in sorted(buffer.items()):
                index_file.write(f"{token}:{posting}")
    print("Progress: 100%")
        
if __name__ == "__main__":
    merge()
