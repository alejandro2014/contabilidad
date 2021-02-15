import json

class ConfigLoader:
    def load_table(self, table_name):
        return self.load_config_file('tables/' + table_name)

    def load_config_file(self, file_name):
        with open('src/config/' + file_name + '.json') as file:
            file_content = json.load(file)

        return file_content
