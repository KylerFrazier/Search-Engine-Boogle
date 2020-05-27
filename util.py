import hashlib
import os

def simhash(word_frequencies: list, n_bits=256) -> str: 
    
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

def find_similar(finger_print: str, n=6, threshold=0.93) -> bool:

    msb = finger_print[:n]

    if not os.path.exists(f'./finger_prints/fp-{msb}.txt'):
        with open(f'./finger_prints/fp-{msb}.txt', 'w') as f:
            f.write(finger_print + "\n")

    else:
        with open(f'./finger_prints/fp-{msb}.txt', 'r') as f:
            while True:
                fp = f.readline()
                if not fp:
                    break
                sim = sum(1 for bit in range(len(finger_print)) if finger_print[bit] == fp[bit])
                if sim / len(finger_print) > threshold:
                    return True

        # Similar finger print not found
        with open(f'./finger_prints/fp-{msb}.txt', 'a') as f:
            f.write(finger_print + '\n')

    return False
