import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from test.qt_app import get_app

from src.dialogs.LoadFileDialog import LoadFileDialog

class LoadFileDialogTestCase(unittest.TestCase):
    def setUp(self):
        get_app()

        self.directory = tempfile.TemporaryDirectory()
        self.listeners_pool = Mock()

        self.dialog = LoadFileDialog(None, self.listeners_pool)
        self.dialog.expenses_service = Mock()

    def tearDown(self):
        self.dialog.close()
        self.directory.cleanup()

    def create_file(self, name):
        path = os.path.join(self.directory.name, name)
        open(path, 'w').close()

        return path

    def test__check_file(self):
        self.assertIsNotNone(self.dialog.check_file(''))
        self.assertIsNotNone(self.dialog.check_file(os.path.join(self.directory.name, 'missing.xls')))
        self.assertIsNotNone(self.dialog.check_file(self.create_file('statement.csv')))
        self.assertIsNone(self.dialog.check_file(self.create_file('statement.XLS')))

    @patch('src.dialogs.LoadFileDialog.ErrorDialog')
    def test__load_file__wrong_file_is_not_loaded(self, error_dialog):
        self.dialog.load_file_textbox.setText(self.create_file('statement.csv'))

        self.dialog.load_file()

        error_dialog.assert_called_once()
        self.dialog.expenses_service.load_file.assert_not_called()

    @patch('src.dialogs.LoadFileDialog.ErrorDialog')
    def test__load_file__error_while_loading(self, error_dialog):
        self.dialog.load_file_textbox.setText(self.create_file('statement.xls'))
        self.dialog.expenses_service.load_file.side_effect = ValueError('The header row (F. VALOR) has not been found in the xls file')

        self.dialog.load_file()

        error_dialog.assert_called_once()
        self.listeners_pool.send_event.assert_not_called()

    @patch('src.dialogs.LoadFileDialog.InfoDialog')
    def test__load_file__loaded(self, info_dialog):
        file_name = self.create_file('statement.xls')
        self.dialog.load_file_textbox.setText(file_name)
        self.dialog.expenses_service.load_file.return_value = { 'inserted': 3, 'ignored': 1 }

        self.dialog.load_file()

        self.dialog.expenses_service.load_file.assert_called_once_with(file_name)
        info_dialog.assert_called_once()
        self.assertEqual('', self.dialog.load_file_textbox.text())
