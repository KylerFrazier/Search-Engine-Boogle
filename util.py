import hashlib
import os

def simhash(word_frequencies: list, n_bits=16) -> str: 
    
    hash_list = []
    simhash = []

    for token in word_frequencies.keys():
        
        hasher = hashlib.shake_128(token.encode())
        hashed = hasher.hexdigest(int(n_bits / 8))
        binary = bin(int(hashed, 16))[2:]
        
        if len(binary) != n_bits:
            binary = "0" * (n_bits - len(binary)) + binary
            
        hash_list.append(binary)
    
    for i in range(n_bits):
        value = 0

        for frequency, h in zip(word_frequencies.values(), hash_list):
            if h[i] == "1": 
                value = value + frequency
                
            else: 
                value = value - frequency

        simhash.append(value)

    for i in range(n_bits):
        if simhash[i] <= 0: 
            simhash[i] = "0"

        else: 
            simhash[i] = "1"
    
    simhash = ''.join(simhash)

    return simhash

def find_similar(finger_print: str, n=4, threshold=0.9) -> bool:

   msb = finger_print[:n]

   if not os.path.exists(f'./finger_prints/fp-{msb}'):
      with open(f'./finger_prints/fp-{mbs}.txt', 'w') as f:
         f.write(finger_print + "\n")
   

   with open(f'./finger_prints/fp-{msb}.txt', 'r') as f:
      while True:
         fp = f.readline()
         if not fp:
            break
         sim = sum([1 for bit in range(len(finger_print)) if finger_print[bit] == fp[bit]])
         if sim / len(finger_print) > threshold:
            return True

   # new finger_print not found so add
   with open(f'./finter_prints/fp-{msb}.txt', 'a') as f:
      f.write(finger_print + '\n')

   return False

from os import path
from json import dump, load

def initJSON():
    with open('document-id-convert.json', 'w') as json_file:
        dump({}, json_file)

def save_documents(docid_table: {int : str}) -> None:
        # docid: int, url: str
        if not path.exists('document-id-convert.json'):
            with open('document-id-convert.json', 'w') as json_file:
                dump(docid_table, json_file, indent=4)

        else:

            with open('document-id-convert.json', 'r') as json_file:
                convert = load(json_file)

            for docid, url in docid_table.items():
                
                if docid in convert.keys():
                    print("Duplicate docid found")

                # This one takes a LOT of time. It would be ideal if we could remove it.
                if url in convert.values():
                    print("Duplicate url found")
                    print(url)
                    for docid, url in convert.items():
                        print("\t", docid, ": " ,url ,sep="")

            convert.update(docid_table)

            with open('document-id-convert.json', 'w') as json_file:
                dump(convert, json_file, indent=4)