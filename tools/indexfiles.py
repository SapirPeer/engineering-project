import os
import csv
from glob import glob
import threading
import time
import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory

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

    def index(self, csv_path):
        patents = self._read_csv(csv_path)
        print("\rProcessed {}/{} patents".format(0, len(patents)), end='', flush=True)
        
        for i, patent in enumerate(patents, 1):

            pid, date, title, author, icn, org, acn, abstract, description = patent[1:]

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

                self._writer.addDocument(doc)

            except Exception as e:
                print("Failed to index '{}': {}".format(path, e))
            print("\rProcessed {}/{} patents".format(i, len(patents)), end='', flush=True)
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
    CSV_FILE = "output.csv"

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print('lucene {}'.format(lucene.VERSION))
    start = time.time()

    try:
        index = IndexFiles(INDEX_DIR, StandardAnalyzer())
        index.index(CSV_FILE)
        print(time.time() - start)

    except Exception as e:
        print("Failed: {}".format(e))
        raise e