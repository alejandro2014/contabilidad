class CsvReader:
    def __init__(self, file_info = {}):
        self.file_info = file_info
        self.field_name_prefix = file_info['fieldNamePrefix']
        self.has_header = file_info['hasHeader']
        self.separator = file_info['separator']

    def read_file(self, file_path):
        lines = self.read_file_lines(file_path)
        header = self.get_header(lines)

        if self.has_header == 'true':
            lines.pop(0)

        object_lines = []

        for line in lines:
            new_object = {}

            for i in range(len(line)):
                new_object[header[i]] = line[i]

            object_lines.append(new_object)

        return object_lines

    def read_file_lines(self, file_path):
        output_lines = []

        with open(file_path, 'r') as csv_file:
            input_lines = csv_file.readlines()

            for line in input_lines:
                line = line.strip()
                line = self.split_line(line, self.separator)

                output_lines.append(line)

        return output_lines

    def split_line(self, line, separator):
        return line.split(separator)

    def get_header(self, lines):
        if self.has_header == 'true':
            return lines[0]

        header_fields = []

        for i in range(len(lines[0])):
            header_fields.append(self.field_name_prefix + str(i))

        return header_fields
