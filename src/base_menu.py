from src.config.ConfigLoader import ConfigLoader

class BaseMenu:
    def init_menu(self, menu_name, main_window):
        menu_info = self._load_menu_info(menu_name)
        self.main_window = main_window
        self.menubar = self.main_window.menuBar()

        menu = self.menubar.addMenu(menu_info['title'])

        for option in menu_info['options']:
            if 'separator' in option:
                menu.addSeparator()
            else:
                action = menu.addAction(option['title'])
                action.triggered.connect(getattr(self, option['method']))

    def _load_menu_info(self, menu_name):
        return ConfigLoader().load_menu(menu_name)