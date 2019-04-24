
import os
import sys
import csv
import threading
import time
import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory


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


class Ticker:
    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            print('.', end='', flush=True)
            time.sleep(1.0)


class IndexFiles:

    def __init__(self, path, analyzer):
        self.path = path
        self._analyzer = analyzer
        self.errors = []
        self._initialize()

    def index(self, csvs_path):

        all_csvs = [x for x in os.listdir(csvs_path) if x.endswith('csv')]

        for i, csv_file in enumerate(all_csvs, 1):
            print("\nProcessing CSV #{}".format(i), flush=True)

            patents = self._read_csv(csvs_path + "/" + csv_file)
            print("\rProcessed {}/{} patents in file".format(0, len(patents)), end='', flush=True)
            for j, patent in enumerate(patents, 1):

                pid, date, title, author, icn, org, acn, abstract, description, purpose, mechanics, uid = patent

                try:
                    doc = Document()
                    doc.add(Field('id', pid, self._ft1))
                    doc.add(Field('date', date, self._ft1))
                    doc.add(Field('title', title, self._ft1))
                    doc.add(Field('author', author, self._ft1))
                    doc.add(Field('icn', icn, self._ft1))
                    doc.add(Field('organization', org, self._ft1))
                    doc.add(Field('acn', acn, self._ft1))
                    doc.add(Field('abstract', abstract, self._ft2))
                    doc.add(Field('description', description, self._ft2))
                    doc.add(Field('purpose', description, self._ft2))
                    doc.add(Field('mechanics', description, self._ft2))
                    doc.add(Field('uid', uid, self._ft1))

                    self._writer.addDocument(doc)

                except Exception as e:
                    print("\nFailed to index '{}': {}\n".format(path, e))
                print("\rProcessed {}/{} patents in file".format(j, len(patents)), end='', flush=True)
            print()
        self._commit()
        return self

    def _read_csv(self, path):

        with open(path, 'rU', newline='') as fs:
            reader = csv.reader(x.replace('\0', '') for x in fs)
            rows = [r for r in reader]

        return rows

    def _commit(self):

        ticker = Ticker()
        print("Commiting index", end='', flush=True)
        threading.Thread(target=ticker.run).start()
        self._writer.commit()
        self._writer.close()
        ticker.tick = False
        print("Done!")

    def _initialize(self):

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self._analyzer = LimitTokenCountAnalyzer(self._analyzer, 1048576)
        self._store = SimpleFSDirectory(Paths.get(self.path))
        self._config = IndexWriterConfig(self._analyzer)
        self._config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        self._writer = IndexWriter(self._store, self._config)
        self._set_fieldtypes()

    def _set_fieldtypes(self):

        self._ft1 = FieldType()
        self._ft1.setStored(True)
        self._ft1.setTokenized(False)
        self._ft1.setIndexOptions(IndexOptions.DOCS_AND_FREQS)
        self._ft2 = FieldType()
        self._ft2.setStored(True)
        self._ft2.setTokenized(True)
        self._ft2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)


if __name__ == '__main__':

    INDEX_DIR = "patent.index"
    CSV_DIR = "patent_db/csv_db"

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print('lucene {}'.format(lucene.VERSION))
    start = time.time()

    try:
        index = IndexFiles(INDEX_DIR, StandardAnalyzer())
        index.index(CSV_DIR)
        print(time.time() - start)

    except Exception as e:
        print("Failed: {}".format(e))
        raise e
