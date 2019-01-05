import os
import threading
from time import time

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader, DocValues
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.pylucene.search.similarities import PythonSimilarity


DEF_TOPN = 10

class SearchFiles:

    def __init__(self, path, analyzer, topn=DEF_TOPN):

        self.path = path
        self._analyzer = analyzer
        self.topn = topn
        self._store = SimpleFSDirectory(Paths.get(os.path.abspath(self.path)))
        self._searcher = IndexSearcher(DirectoryReader.open(self._store))

    def search(self, query):

        query = QueryParser('content', self._analyzer).parse(query)
        docs = self._searcher.search(query, self.topn).scoreDocs

        return docs

if __name__ == '__main__':

    INDEX_DIR = "test.index"

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print('lucene {}'.format(lucene.VERSION))

    searcher = SearchFiles(INDEX_DIR, StandardAnalyzer())

    while True:

        print("=" * 100)
        query = input("Enter query: ")
        if not query:
            break

        print('-' * 100)
        print('BM25')
        docs = searcher.search(query)
        for doc in docs:
            doc = searcher._searcher.doc(doc.doc)
            print('path: {}\nfilename: {}'.format(doc.get("path"), doc.get("filename")))




