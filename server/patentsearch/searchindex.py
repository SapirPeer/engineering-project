
import os
import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader, Term
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause, TermQuery

import sys
import gensim

DEF_TOPN = 10

class Word2Vec:

    def __init__(self, words_array):
        self.sg_model = self.run()
        self.words = self.most_similar_words_string(words_array) if words_array is not None else words_array

    def run(self):
        model = None
        try:
            model = gensim.models.Word2Vec.load("/home/naomi/final_project/finalproject/tools/word2vec/word2vec2.model")
        except Exception as e:
            print("ERROR: No model was found!")
            print(e)
            exit(-1)

        return model

    def most_similar_words_string(self, words):
        similar_words = []
        similar_words_str = ""

        words = words.split(" ")
        for word in words:
            similar_words.extend(self.sg_model.most_similar(positive=word))

        for similar_word in similar_words:
            similar_words_str += similar_word[0] + " "

        return similar_words_str

class SearchIndex:


    def __init__(self, path, topn=DEF_TOPN):

        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        self.path = path
        self.topn = topn
        self._analyzer = StandardAnalyzer()
        self._store = SimpleFSDirectory(Paths.get(os.path.abspath(self.path)))
        self._searcher = IndexSearcher(DirectoryReader.open(self._store))
        self.purpose_is_w2v = None
        self.purpose_is_not_w2v = None
        self.mechanics_is_w2v = None
        self.mechanics_is_not_w2v = None


    def search(self, query, topn=None):

        general_query = query['general_query']
        purpose_is = query['purpose_is']
        purpose_is_not = query['purpose_is_not']
        mechanics_is = query['mechanics_is']
        mechanics_is_not = query['mechanics_is_not']

        self.purpose_is_w2v = Word2Vec(purpose_is).words
        self.purpose_is_not_w2v = Word2Vec(purpose_is_not).words
        self.mechanics_is_w2v = Word2Vec(mechanics_is).words
        self.mechanics_is_not_w2v = Word2Vec(mechanics_is_not).words

        topn = self.topn if topn is None else topn

        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()

        bool_query = BooleanQuery.Builder()

        if general_query:
            query_description = QueryParser('description', self._analyzer).parse(general_query)
            query_title = QueryParser('title', self._analyzer).parse(general_query)
            # query_id = QueryParser('uid', self._analyzer).parse(query)
            query_id = TermQuery(Term('uid', general_query))

            bool_query.add(query_description, BooleanClause.Occur.SHOULD)
            bool_query.add(query_title, BooleanClause.Occur.SHOULD)
            bool_query.add(query_id, BooleanClause.Occur.SHOULD)

        if purpose_is:
            query_purpose_is_w2v = QueryParser('purpose', self._analyzer).parse(purpose_is + self.purpose_is_w2v)
            bool_query.add(query_purpose_is_w2v, BooleanClause.Occur.SHOULD)

        if purpose_is_not:
            query_purpose_is_not_w2v = QueryParser('purpose', self._analyzer).parse(purpose_is_not + self.purpose_is_not_w2v)
            bool_query.add(query_purpose_is_not_w2v, BooleanClause.Occur.MUST_NOT)  # MAYBE NEED TO BE BooleanClause.Occur.SHOULD

        if mechanics_is:
            query_mechanics_is_w2v = QueryParser('mechanics', self._analyzer).parse(mechanics_is + self.mechanics_is_w2v)
            bool_query.add(query_mechanics_is_w2v, BooleanClause.Occur.SHOULD)

        if mechanics_is_not:
            query_mechanics_is_not_w2v = QueryParser('mechanics', self._analyzer).parse(mechanics_is_not + self.mechanics_is_not_w2v)
            bool_query.add(query_mechanics_is_not_w2v, BooleanClause.Occur.MUST_NOT)


        # bool_query = BooleanQuery.Builder()
        # bool_query.add(query_description, BooleanClause.Occur.SHOULD)
        # bool_query.add(query_title, BooleanClause.Occur.SHOULD)
        # bool_query.add(query_id, BooleanClause.Occur.SHOULD)
        #
        # bool_query.add(query_purpose_is_w2v, BooleanClause.Occur.SHOULD)
        # bool_query.add(query_purpose_is_not_w2v, BooleanClause.Occur.MUST_NOT) # MAYBE NEED TO BE BooleanClause.Occur.SHOULD
        # bool_query.add(query_mechanics_is_w2v, BooleanClause.Occur.SHOULD)
        # bool_query.add(query_mechanics_is_not_w2v, BooleanClause.Occur.MUST_NOT)

        docs = self._searcher.search(bool_query.build(), topn).scoreDocs

        result = []
        for doc in docs:
            doc = self._searcher.doc(doc.doc)
            result.append({
                'id': doc.get('id'), 'date': doc.get('date'), 'title': doc.get('title'),
                'author': doc.get('author'), 'icn': doc.get('icn'), 'organization': doc.get('organization'),
                'acn': doc.get('acn'), 'abstract': doc.get('abstract'), 'description': doc.get('description'),
                'purpose': doc.get('patent purpose'), 'mechanics': doc.get('patent mechanics'),
                'uid': doc.get('uid')
            })
        return result
