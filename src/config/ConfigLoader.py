import json

from src.config.paths import config_path

class ConfigLoader:
    def load_table(self, table_name):
        return self.load_config_file('tables/' + table_name)

    def load_config_file(self, file_name):
        with open(config_path(file_name + '.json'), encoding='utf-8') as file:
            file_content = json.load(file)

        return file_content
