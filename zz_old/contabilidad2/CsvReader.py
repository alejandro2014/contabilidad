import hashlib

class CsvReader:
    def __init__(self, line_transform):
        self.line_transform = line_transform

    def read_file(self, file_path):
        hash_file = self.get_hash_file(file_path)

        with open(file_path, 'r') as f:
            lines = [ self.convert_line(l) for l in f.readlines() ]

        return lines, hash_file

    def get_hash_file(self, file_path):
        with open(file_path, 'rb') as f:
            file_content = f.read()
            hash_file = hashlib.sha256(file_content).hexdigest()

        return hash_file[:10]

    def convert_line(self, line):
        line = line.strip().split('\t')

        return self.line_transform(line)
