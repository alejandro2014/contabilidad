import os

class BaseArgsParse:
    def check_param(self, param, value):
        if value is None:
            print(f'Error: {param} must be specified')
            exit(1)

    def check_file_exist(self, file_path):
        if not os.path.exists(file_path):
            print(f'Error: The file "{file_path}" does not exist')
            exit(1)

    def check_file_not_exist(self, file_path):
        if os.path.exists(file_path):
            print(f'Error: The file "{file_path}" already exists')
            exit(1)

    def print_list(self, list_elems, category):
        if len(list_elems) == 0:
            print('No elements')
            return

        max_lengths = self.get_max_lengths(list_elems)
        separator = self.get_separator(max_lengths)

        print(separator)

        for elem in list_elems:
            row = '| '

            for i, cell in enumerate(elem.values()):
                content = str(cell) if cell is not None else ''
                spaces = ' ' * (max_lengths[i] - len(content))
                content = f'{content}{spaces}'

                row += f'{content} | '

            print(row)

        print(separator)
        print(f'{len(list_elems)} {category}')


    def get_separator(self, max_lengths):
        lines = ['-' * (ml + 2) for ml in max_lengths]
        separator = '+'.join(lines)

        return f'+{separator}+'

    def get_max_lengths(self, list_elems):
        max_lengths = [ 0 for _ in range(len(list_elems[0]))]

        for elem in list_elems:
            for i, cell in enumerate(elem):
                cell_len = len(str(elem[cell]))

                if cell_len > max_lengths[i]:
                    max_lengths[i] = cell_len

        return max_lengths
