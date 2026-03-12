from CsvReader import CsvReader

class FileReader:
    def __init__(self, file_info):
        reader_type = file_info['readerType']

        if reader_type == 'csv':
            self.reader = CsvReader(file_info)

    def read_file(self, file_path):
        return self.reader.read_file(file_path)
