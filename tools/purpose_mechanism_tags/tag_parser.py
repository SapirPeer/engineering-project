import csv
from collections import defaultdict

PATH = "/cs/engproj/324/parse_patents_tags_csv/patents_tags_crf_format.csv"
OUTPUT_PATH = "/cs/engproj/324/parse_patents_tags_csv/output.csv"

FIRST_PAPER_ID = '198'
PURPOSE = "Purpose"
MECHANISM = "Mechanism"

HEADER = ['Title', 'Purpose', 'Mechanism']


def read_csv(path):
    # Reads csv file
    with open(path, 'r', encoding='utf8', newline='') as fs:
        reader = csv.reader(x.replace('\0', '') for x in fs)
        rows = [r for r in reader]
    return rows


def extract_info(info_dict, contant, type, sentence_id, title):
    # Get patent title
    if sentence_id.endswith('_0'):
        title += contant + " "

    # Get patent purpose
    if type == PURPOSE:
        info_dict[PURPOSE].append(contant)

    # Get patent mechanism
    if type == MECHANISM:
        info_dict[MECHANISM].append(contant)
    return info_dict, title


def write_to_csv(path, write_to):
    rows = read_csv(path)
    old_paper_id = FIRST_PAPER_ID
    info_dict = defaultdict(list)
    title = ""
    first_row = True

    with open(write_to, 'w', newline='', encoding='utf8') as fs:
        for row in rows:

            if first_row:
                first_row = False
                continue

            _, contant, type, paper_id, sentence_id = row

            if paper_id == old_paper_id:
                info_dict, title = extract_info(info_dict, contant, type, sentence_id, title)

            else:
                info_dict["Title"] = title.strip(" .")

                writer = csv.writer(fs)
                row = [info_dict[k] if k in info_dict else '' for k in HEADER]
                writer.writerow(row)

                # in case we enter a new patent information
                old_paper_id = paper_id
                info_dict = defaultdict(list)
                title = ""
                info_dict, title = extract_info(info_dict, contant, type, sentence_id, title)


if __name__ == '__main__':
    write_to_csv(PATH, OUTPUT_PATH)
