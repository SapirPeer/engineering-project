
import os
import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher

DEF_TOPN = 10

class SearchIndex:


    def __init__(self, path, topn=DEF_TOPN):

        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        self.path = path
        self.topn = topn
        self._analyzer = StandardAnalyzer()
        self._store = SimpleFSDirectory(Paths.get(os.path.abspath(self.path)))
        self._searcher = IndexSearcher(DirectoryReader.open(self._store))


    def search(self, query, topn=None):

        topn = self.topn if topn is None else topn

        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()

        query = QueryParser('description', self._analyzer).parse(query)
        docs = self._searcher.search(query, topn).scoreDocs

        result = []
        for doc in docs:
            doc = self._searcher.doc(doc.doc)
            result.append({
                'id': doc.get('id'), 'date': doc.get('date'), 'title': doc.get('title'),
                'author': doc.get('author'), 'icn': doc.get('icn'), 'organization': doc.get('organization'),
                'acn': doc.get('acn'), 'abstract': doc.get('abstract'), 'description': doc.get('description'),
            })
        return result

