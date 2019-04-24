import csv
import os
import sys

import gensim

class Word2Vec:

    def __init__(self, words_array):
        self.sg_model = self.run()
        self.words = self.most_similar_words_string(words_array) if words_array is not None else words_array

    def run(self):
        model = None
        try:
            model = gensim.models.Word2Vec.load("../../tools/word2vec/word2vec2.model")
        except:
            print("ERROR: No model was found!")
            exit(-1)

        return model

    def most_similar_words_string(self, words):
        similar_words = []
        similar_words_str = ""

        for word in words:
            similar_words.extend(self.sg_model.most_similar(positive=word))

        for similar_word in similar_words:
            similar_words_str += similar_word[0] + " "

        return similar_words_str
