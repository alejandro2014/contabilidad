import unittest
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QInputDialog, QMessageBox

from test.qt_app import get_app

from src.dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog

class ConfigureExpensesDialogTestCase(unittest.TestCase):
    def setUp(self):
        get_app()

        # The service is mocked, so the dialog never touches the database
        patcher = patch('src.dialogs.ConfigureExpensesDialog.ExpenseTypesService')
        self.service = patcher.start().return_value
        self.addCleanup(patcher.stop)

        self.service.select_expense_types_full.return_value = [
            { 'category': 'Casa', 'comment': '', 'income': False, 'not_computed': False },
            { 'category': 'Comida', 'comment': 'Super', 'income': False, 'not_computed': False }
        ]
        self.service.get_categories_simple.return_value = [ 'Casa', 'Comida' ]

        self.dialog = ConfigureExpensesDialog(None, Mock())

    def tearDown(self):
        self.dialog.close()

    @patch('src.dialogs.ConfigureExpensesDialog.ErrorDialog')
    def test__rename__expenses_and_rules_renamed(self, error_dialog):
        self.service.check_category_exists.return_value = False

        self.dialog.table.item(1, 0).setText('Supermercado')

        self.service.rename_category.assert_called_once_with('Comida', 'Supermercado')
        error_dialog.assert_not_called()

        # A second rename starts from the new name
        self.dialog.table.item(1, 0).setText('Comida')

        self.service.rename_category.assert_called_with('Supermercado', 'Comida')

    @patch('src.dialogs.ConfigureExpensesDialog.ErrorDialog')
    def test__rename__to_an_existing_one_is_undone(self, error_dialog):
        self.service.check_category_exists.return_value = True

        self.dialog.table.item(1, 0).setText('Casa')

        self.service.rename_category.assert_not_called()
        error_dialog.assert_called_once()
        self.assertEqual('Comida', self.dialog.table.item(1, 0).text())

    def test__comment__saved_for_its_type(self):
        self.dialog.table.item(1, 1).setText("Super's")

        self.service.update_comment.assert_called_once_with('Comida', "Super's")

    @patch.object(QInputDialog, 'getItem', return_value = ('Pasarlos a "Casa"', True))
    def test__remove__moved_to_another_type(self, get_item):
        self.service.get_category_usage.return_value = (5, 2)
        self.dialog.table.selectRow(1)

        self.dialog.remove_selected_rows()

        self.service.remove_category.assert_called_once_with('Comida', 'Casa')
        self.assertEqual(1, self.dialog.table.rowCount())

    @patch.object(QInputDialog, 'getItem', return_value = (ConfigureExpensesDialog.LEAVE_PENDING, True))
    def test__remove__pending_again(self, get_item):
        self.service.get_category_usage.return_value = (5, 2)
        self.dialog.table.selectRow(1)

        self.dialog.remove_selected_rows()

        self.service.remove_category.assert_called_once_with('Comida', None)

    @patch.object(QInputDialog, 'getItem', return_value = ('', False))
    def test__remove__cancelled(self, get_item):
        self.service.get_category_usage.return_value = (5, 2)
        self.dialog.table.selectRow(1)

        self.dialog.remove_selected_rows()

        self.service.remove_category.assert_not_called()
        self.assertEqual(2, self.dialog.table.rowCount())

    @patch.object(QMessageBox, 'question', return_value = QMessageBox.StandardButton.Yes)
    def test__remove__unused_type_only_confirmed(self, question):
        self.service.get_category_usage.return_value = (0, 0)
        self.dialog.table.selectRow(0)

        self.dialog.remove_selected_rows()

        question.assert_called_once()
        self.service.remove_category.assert_called_once_with('Casa', None)
