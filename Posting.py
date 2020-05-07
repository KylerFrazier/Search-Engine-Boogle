
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

