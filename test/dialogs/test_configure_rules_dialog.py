import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QMessageBox

from test.qt_app import get_app

from src.dialogs.ConfigureRulesDialog import ConfigureRulesDialog

class ConfigureRulesDialogTestCase(unittest.TestCase):
    def setUp(self):
        get_app()

        # The services are mocked, so the dialog never touches the database
        patchers = [
            patch('src.dialogs.ConfigureRulesDialog.RulesService'),
            patch('src.dialogs.ConfigureRulesDialog.ComboBoxService'),
            patch('src.dialogs.WidgetCreator.ComboBoxService')
        ]
        mocks = [ p.start() for p in patchers ]
        for p in patchers:
            self.addCleanup(p.stop)

        self.service = mocks[0].return_value
        self.service.get_rules.return_value = [
            { 'priority': 1, 'rule': 'MERCADONA', 'category': 'Comida' },
            { 'priority': 2, 'rule': 'RENFE', 'category': 'Transporte' }
        ]
        mocks[1].return_value.get_categories.return_value = [ 'Comida', 'Transporte' ]
        mocks[2].return_value.get_categories.return_value = [ 'Comida', 'Transporte' ]

        self.dialog = ConfigureRulesDialog(None)
        self.dialog.table.selectRow(1)

    def tearDown(self):
        self.dialog.close()

    @patch('src.dialogs.ConfigureRulesDialog.QMessageBox.question', return_value = QMessageBox.StandardButton.Yes)
    def test__remove_selected_rules__confirmed(self, question):
        self.dialog.remove_selected_rules()

        self.assertIn('RENFE', question.call_args[0][2])
        self.service.delete_rule_by_priority.assert_called_once_with(2)

    @patch('src.dialogs.ConfigureRulesDialog.QMessageBox.question', return_value = QMessageBox.StandardButton.No)
    def test__remove_selected_rules__cancelled(self, question):
        self.dialog.remove_selected_rules()

        self.service.delete_rule_by_priority.assert_not_called()

    @patch('src.dialogs.ConfigureRulesDialog.QMessageBox.question')
    def test__remove_selected_rules__nothing_selected(self, question):
        self.dialog.table.clearSelection()

        self.dialog.remove_selected_rules()

        question.assert_not_called()
