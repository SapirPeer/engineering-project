import csv
import io
from lxml import etree
import os

PATH = "/mnt/d/Naomi/Desktop/Naomi/Final_Project/finalproject/tools/patent_db/tmp"


class FileHandler():
    def __init__(self, zfile):
        self.zfile = zfile

    def readline(self):
        return self.zfile.readline()

    def listXmls(self):
        output = io.StringIO()
        line = self.readline()
        output.write(line)
        line = self.readline()
        while line is not '':
            if '<?xml version="1.0" encoding="UTF-8"?>' in line:
                line = line.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                output.write(line)
                output.seek(0)
                yield output
                output = io.StringIO()
                output.write('<?xml version="1.0" encoding="UTF-8"?>')
            elif '<?xml version="1.0"?>' in line:
                line = line.replace('<?xml version="1.0"?>', '')
                output.write(line)
                output.seek(0)
                yield output
                output = io.StringIO()
                output.write('<?xml version="1.0"?>')
            else:
                output.write(line)
            try:
                line = self.readline()
            except StopIteration:
                break
        output.seek(0)
        yield output


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
              'ACN', 'patent abstract', 'patent description']
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


def parse_file(folder_in, file_in):

    file = folder_in + '/' + file_in
    if os.path.isfile(file):
        f = open(file, 'rU')
        parser = etree.XMLParser(target=SimpleXMLHandler(), resolve_entities=False)
        result, fields_dict = etree.parse(f, parser)

        fields_dict['file name'] = os.path.basename(file)
        return fields_dict

        file_name = 'File name: ' + os.path.basename(file)
        return create_fields(result, file_name)


def main():
    folder_in = PATH
    # out_file = 'names-in-patents.txt'

    header = [
        'file name', 'id', 'date', 'patent title', 'author-name', 'ICN', 'organization-name',
        'ACN', 'patent abstract', 'patent description',
    ]

    with open('output.csv', 'w', newline='') as fs:
        writer = csv.writer(fs)

        for filename in os.listdir(folder_in):
            fields_dict = parse_file(folder_in, filename)
            row = [fields_dict[k] if k in fields_dict else '' for k in header]
            writer.writerow(row)



def usage():
    print(main.__doc__)


if __name__ == "__main__":
    main()


