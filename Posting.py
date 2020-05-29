
class Posting(object):

    def __init__(self, docid, tfidf):

        self.docid = docid
        self.tfidf = tfidf

    def __str__(self):
        
        return str(self.docid)

    def _get_docid(self) -> int:

        return self.docid

    def _get_tfidf(self) -> int:
        
        return self.tfidf

    # returns a list of strings of the values in the Posting sorted by item name
    def get_values(self) -> list:
        
        return [str(self.__dict__[key]) for key in sorted(self.__dict__.keys())]

