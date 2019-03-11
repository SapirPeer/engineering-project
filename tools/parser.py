import csv
import io
from lxml import etree
import os
import re

PATH = "/mnt/d/Naomi/Desktop/Naomi/Final_Project/finalproject/tools/patent_db/xml_db_files"
HEADER = [
    'id', 'date', 'patent title', 'author-name', 'ICN', 'organization-name',
    'ACN', 'patent abstract', 'patent description', 'uid'
]

DATA_FORM_ID = re.compile(r'([A-Z]*)(\d+)')


class SimpleXMLHandler(object):
    def __init__(self):
        ''' xml elements '''
        self.last_name = 0
        self.first_name = 0
        self.organization_name = 0
        self.inventor = 0
        self.assignee = 0
        self.country_code = 0
        self.document_date = 0
        self.pct_application = 0
        self.title = 0
        self.abstract = 0
        self.document_id = 0
        self.set_id = False
        self.addressbook = 0
        self.description_text = 0

        ''' buffer '''
        self.buffer = ''
        self.firstname_buffer = ''
        self.lastname_buffer = ''
        self.organization_buffer = ''
        self.country_buffer = ''
        self.date_buffer = ''
        self.title_buffer = ''
        self.abstract_buffer = ''
        self.id_buffer = ''
        self.description_buffer = ''

        ''' storage '''
        self.write_buffer = []
        self.fields_dict = {}

    def start(self, tag, attributes):
        if tag == 'last-name':
            self.last_name = 1
        elif tag == 'first-name':
            self.first_name = 1
        elif tag == 'organization-name' or tag == 'orgname':
            self.organization_name = 1
        elif tag == 'inventors' or tag == 'applicants':
            self.inventor = 1
        elif tag == 'assignees':
            self.assignee = 1
        elif tag == 'country-code' or tag == 'country':
            self.country_code = 1
        elif tag == 'publication-reference':
            self.pct_application = 0
        elif tag == 'addressbook':
            self.addressbook = 1
        elif tag == 'document-date' or tag == 'date':
            self.document_date = 1
        elif tag == 'title-of-invention' or tag == 'invention-title':
            self.title = 1
        elif tag == 'subdoc-abstract' or tag == 'abstract':
            self.abstract = 1
        elif tag == 'doc-number':
            self.document_id = 1
        elif tag == 'description':
            self.description_text = 1

    def data(self, data):
        if self.last_name == 1:
            self.lastname_buffer += data
        elif self.first_name == 1:
            self.firstname_buffer += data
        elif self.organization_name == 1:
            self.organization_buffer += data
        elif self.country_code == 1:
            self.country_buffer += data
        elif self.document_date == 1:
            self.date_buffer += data
        elif self.title == 1:
            self.title_buffer += data
        elif self.abstract == 1:
            self.abstract_buffer += data
        elif self.document_id == 1:
            self.id_buffer += data
        elif self.description_text == 1:
            self.description_buffer += data

    def end(self, tag):
        if tag == 'last-name':
            self.last_name = 0
        elif tag == 'first-name':
            if self.addressbook == 1:
                if self.inventor == 1:
                    self.firstname_buffer += ' '
                    self.write_buffer.append(
                        "author-name: " + self.firstname_buffer + self.lastname_buffer)
                    self.fields_dict['author-name'] = self.firstname_buffer + self.lastname_buffer
            self.firstname_buffer = ''
            self.lastname_buffer = ''
            self.first_name = 0

        elif tag == 'organization-name' or tag == 'orgname':
            if self.addressbook == 1:
                if self.assignee == 1:
                    self.write_buffer.append("organization-name: " +
                                             self.organization_buffer.strip())
                    self.fields_dict['organization-name'] = self.organization_buffer.strip()
            self.organization_buffer = ''
            self.organization_name = 0

        elif tag == 'inventors' or tag == 'applicants':
            self.inventor = 0

        elif tag == 'assignees':
            self.assignee = 0

        elif tag == 'addressbook':
            self.addressbook = 0

        elif tag == 'country-code' or tag == 'country':
            if self.addressbook == 1:
                if self.inventor == 1:
                    self.write_buffer.append("ICN: " + self.country_buffer)
                    self.fields_dict['ICN'] = self.country_buffer
                elif self.assignee == 1:
                    self.write_buffer.append("ACN: " + self.country_buffer)
                    self.fields_dict["ACN"] = self.country_buffer
            self.country_buffer = ''
            self.country_code = 0

        elif tag == 'doc-number':
            if not self.set_id:
                self.write_buffer.append("ID: " + self.id_buffer)
                self.fields_dict["id"] = self.id_buffer
                self.set_id = True
            self.id_buffer = ''
            self.document_id = 0

        elif tag == 'document-date' or tag == 'date':
            if self.pct_application == 0:
                self.write_buffer.append("date: " + self.date_buffer)
                self.fields_dict["date"] = self.date_buffer
            self.date_buffer = ''
            self.document_date = 0

        elif tag == 'publication-reference':
            self.pct_application = 1

        elif tag == 'title-of-invention' or tag == 'invention-title':
            self.write_buffer.append("patent title: " + self.title_buffer)
            self.fields_dict["patent title"] = self.title_buffer
            self.title_buffer = ''
            self.title = 0

        elif tag == 'subdoc-abstract' or tag == 'abstract':
            if self.abstract_buffer != '':
                self.abstract_buffer = self.abstract_buffer.expandtabs(1)
                self.abstract_buffer = ' '.join(self.abstract_buffer.splitlines())
                self.abstract_buffer = self.abstract_buffer.strip()
                self.write_buffer.append("patent abstract: " + self.abstract_buffer)
                self.fields_dict["patent abstract"] = self.abstract_buffer
            self.abstract_buffer = ''
            self.abstract = 0

        elif tag == 'description':
            self.write_buffer.append("patent description: " + self.description_buffer)
            self.fields_dict["patent description"] = self.description_buffer

    def close(self):
        return self.write_buffer, self.fields_dict


def create_fields(result, file_name):
    fields = ['ID', 'date', 'patent title', 'author-name', 'ICN', 'organization-name',
              'ACN', 'patent abstract', 'patent description', 'uid']
    field_counter = 1

    if len(fields) == len(result):
        result.insert(0, file_name)
    else:
        result.insert(0, file_name)
        for i in range(len(fields)):
            tmp = result[field_counter].split(":", 1)
            if fields[i] in tmp[0]:
                field_counter += 1
            else:
                result.insert(field_counter, fields[i] + ': ')
                field_counter += 1

    return result


def parse_file(file):

    file = file.encode('utf-8')
    parser = etree.XMLParser(target=SimpleXMLHandler(), resolve_entities=False)
    result, fields_dict = etree.fromstring(file, parser)
    match_letters = DATA_FORM_ID.match(fields_dict['id'])
    fields_dict['uid'] = fields_dict['ICN'] + match_letters.group(1) + match_letters.group(2)[1:]

    return fields_dict


def write_to_csv(all_files, csv_name, start):
    csv_file_name = csv_name + str(start) + ".csv"
    with open(csv_file_name, 'w', newline='', encoding='utf8') as fs:
        writer = csv.writer(fs)
        for file in all_files:
            fields_dict = parse_file(file)
            try:
                if fields_dict["ICN"] != "US" or fields_dict["ACN"] != "US":
                    continue
            except:
                print("\n fields_dict do not contain ICN or ACN")

            row = [fields_dict[k] if k in fields_dict else '' for k in HEADER]
            writer.writerow(row)


def check_patent(buffer):
    counter = 0
    for line in buffer:
        if line.startswith('<?xml version="1.0" encoding="UTF-8"?>'):
            counter += 1
            if counter > 1:
                return False
    return True


def read_file(name, folder_in, start = 0):
    file_name = folder_in + '/' + name
    buffer = []
    all_files = []
    i = 0

    print("\nReading large file...")
    print("\rProcessed {} entries".format(0), end='', flush=True)

    with open(file_name, 'r') as file:
        for line in file:
            buffer.append(line)
            if '</us-patent-grant>' in line:
                if check_patent(buffer):
                    new_xml = ''.join(buffer)
                    all_files.append(new_xml)
                    i += 1

                    # to create a new csv every 1000 patents
                    if len(all_files) == 1000:
                        write_to_csv(all_files, "patent_db/csv_db/output", start)
                        all_files = []
                        start += 1
                        i = 0
                buffer = []
            print("\rProcessed {} entries".format(i), end='', flush=True)

        # in case of the lasts patents in the file
        if len(all_files) < 1000:
            write_to_csv(all_files, "patent_db/csv_db/output", start)
            start += 1

    return start


def main():
    folder_in = PATH
    start = 0
    for filename in os.listdir(folder_in):
        print("====== file name " + str(filename))
        start = read_file(filename, folder_in, start)


def usage():
    print(main.__doc__)


if __name__ == "__main__":
    main()
