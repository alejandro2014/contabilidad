import json
import re

def convert_line(line):
    line = line.strip().split('\t')

    return {
        'date': line[0],
        'category1_ing': line[1],
        'category2_ing': line[2],
        'text': line[3],
        'amount': float(line[5].replace(',', ''))
    }

def get_lines(file_path):
    with open(file_path, 'r') as f:
        lines = [ convert_line(l) for l in f.readlines() ]

    return lines

def process_line(line, rules):
    for category in rules['categories']:
        for rule in category['rules']:
            if re.match(f'.*{rule}.*', line['text']):
                return category['name']

    return None

def process_lines(file_lines, rules):
    classified = []
    unclassified = []

    for line in file_lines:
        category = process_line(line, rules)

        if category is not None:
            classified.append((line, category))
        else:
            unclassified.append(line)

    return {
        'classified': classified,
        'unclassified': unclassified
    }

file_path = './csv/1909.csv'
file_lines = get_lines(file_path)

with open('./rules.json', 'r') as f:
    rules = json.load(f)

output_lines = process_lines(file_lines, rules)
print(output_lines['unclassified'])

classified_no = len(output_lines['classified'])
unclassified_no = len(output_lines['unclassified'])

print(f"Total: {classified_no + unclassified_no}")
print(f"Classified: {classified_no}")
print(f"Unclassified: {unclassified_no}")
