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