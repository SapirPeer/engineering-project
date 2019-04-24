import csv
import os
import sys

import gensim

# CSV_PATH = "/mnt/d/Naomi/Desktop/Naomi/Final_Project/finalproject/tools/patent_db/csv_db"
CSV_PATH = "/home/naomi/final_project/finalproject/tools/patent_db/csv_db"
maxInt = sys.maxsize
decrement = True

while decrement:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.
    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/10)
        decrement = True

class Word2Vec:

    def __init__(self, words_array):
        self.sg_model = self.run()
        self.words = self.most_similar_words_string(words_array) if words_array is not None else words_array


    def read_file(self, path):
        # Reads text file
        with open(path, encoding="utf8") as f:
            text = f.readlines()

        # Replaces escape character with space
        text = [line.replace("\n", "") for line in text]

        text = "".join(list(text))
        return text

    def read_csv(self, path):
        # Reads csv file
        with open(path, 'r', encoding='utf8', newline='') as fs:
            reader = csv.reader(x.replace('\0', '') for x in fs)
            rows = [r for r in reader]
        return rows

    def csvs_to_text_array(self, csvs_path):
        all_csvs_to_text_array = []

        all_csvs = [x for x in os.listdir(csvs_path) if x.endswith('csv')]
        for i, csv_file in enumerate(all_csvs, 1):

            print("\nProcessing CSV #{}".format(i), flush=True)
            patents = self.read_csv(csvs_path + "/" + csv_file)

            for j, patent in enumerate(patents, 1):
                text = ""
                pid, date, title, author, icn, org, acn, abstract, description, purpose, mechanics, uid = patent
                text += title + "\n" + abstract + "\n" + description + "\n" + purpose
                                                        # + "\n" + mechanics (because it will ruin the model)
                all_csvs_to_text_array.append(text)

        return all_csvs_to_text_array

    def word2vec_model(self, text_array):
        data = []
        i = 1
        for patent in text_array:
            print("start patent number " + str(i))
            patent_data = gensim.utils.simple_preprocess(patent, deacc=True, min_len=2, max_len=20)
            data.append(patent_data)
            print("finish patent number " + str(i))
            print("======")
            i += 1

        # Create Skip Gram model
        print("START TO CREATE MODEL")
        sg_model = gensim.models.Word2Vec(data, min_count=1, size=300, window=5, sg=1)
        print("FINISH TO CREATE MODEL")

        return sg_model

    def run(self):
        model = None
        try:
            model = gensim.models.Word2Vec.load("word2vec2.model")
        except:
            all_csvs_to_text_array = self.csvs_to_text_array(CSV_PATH)
            model = self.word2vec_model(all_csvs_to_text_array)
            model.save("word2vec2.model")

        if model is None:
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


if __name__ == '__main__':
    model = Word2Vec(None)