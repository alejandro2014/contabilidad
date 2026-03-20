import json


class ConfigLoader:
    def load_table(self, name):
        return self.load_config_file(f'tables/{name}')
    
    def load_menu(self, name):
        return self.load_config_file(f'menus/{name}')
    
    def load_buttons(self, name):
        return self.load_config_file(f'buttons/{name}')

    def load_config_file(self, file_name):
        with open('src/config/' + file_name + '.json') as file:
            file_content = json.load(file)

        return file_content
