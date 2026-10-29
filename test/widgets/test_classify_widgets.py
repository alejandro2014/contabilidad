import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QMessageBox

from test.qt_app import get_app

from src.widgets.Classifier import Classifier
from src.widgets.tables.ClassifiedExpensesTable import ClassifiedExpensesTable
from src.widgets.tables.PendingExpensesTable import PendingExpensesTable

def expense(expense_id, title, amount):
    return SimpleNamespace(id = expense_id, date = '20260115', title = title, amount = amount, category = 'Comida', note = None, tags = [])

class ClassifierTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        self.pool = Mock()

        with patch('src.dialogs.WidgetCreator.ComboBoxService') as mock_service:
            mock_service.return_value.get_categories.return_value = [ 'Alquiler', 'Comida' ]
            self.classifier = Classifier(self.pool, True)

        self.pool.send_event.reset_mock()

    def test__classify_elements__typed_text_in_other_case(self):
        self.classifier.categories.setEditText('comida')

        self.classifier.classify_elements()

        self.pool.send_event.assert_any_call('pending-expenses-table', 'classify_selected', 'Comida')

    @patch('src.widgets.Classifier.ErrorDialog')
    def test__classify_elements__unknown_type(self, error_dialog):
        self.classifier.categories.setEditText('Ocio')

        self.classifier.classify_elements()

        error_dialog.assert_called_once()
        self.pool.send_event.assert_not_called()

    def test__type_ahead__writes_in_the_combo(self):
        self.classifier.type_ahead('co')

        self.assertEqual('co', self.classifier.categories.currentText())
        self.assertEqual('co', self.classifier.categories.completer().completionPrefix())

class PendingExpensesTableTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        self.pool = Mock()

        patcher = patch('src.widgets.tables.PendingExpensesTable.ExpensesService')
        self.service = patcher.start().return_value
        self.addCleanup(patcher.stop)

        # Sorted by amount, as they come from the database
        self.service.get_pending_expenses.return_value = [ expense(1, 'Mercadona', -30.0), expense(2, 'Lidl', -20.0), expense(3, 'Bar', -10.0) ]

        self.table = PendingExpensesTable(self.pool)
        self.table.refresh_rows()

    def test__classify_selected__the_next_one_is_selected(self):
        self.table.select_row(1)
        self.service.get_pending_expenses.return_value = [ expense(1, 'Mercadona', -30.0), expense(3, 'Bar', -10.0) ]

        self.table.classify_selected('Comida')

        self.service.classify_expenses.assert_called_once_with([ 2 ], 'Comida')
        self.assertEqual([ 1 ], self.table.get_selected_indexes())

    def test__classify_selected__the_last_one_selects_the_one_before(self):
        self.table.select_row(2)
        self.service.get_pending_expenses.return_value = [ expense(1, 'Mercadona', -30.0), expense(2, 'Lidl', -20.0) ]

        self.table.classify_selected('Comida')

        self.assertEqual([ 1 ], self.table.get_selected_indexes())

    def test__classify_selected__nothing_selected(self):
        self.table.clearSelection()

        self.table.classify_selected('Comida')

        self.service.classify_expenses.assert_not_called()

    def test__enter__classifies(self):
        self.table.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier))

        self.pool.send_event.assert_called_with('classificator', 'classify_elements', None)

    def test__letter__looks_for_a_type(self):
        self.table.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.NoModifier, 'c'))

        self.pool.send_event.assert_called_with('classificator', 'type_ahead', 'c')

class ClassifiedExpensesTableTestCase(unittest.TestCase):
    def setUp(self):
        get_app()

        patcher = patch('src.widgets.tables.ClassifiedExpensesTable.ExpensesService')
        self.service = patcher.start().return_value
        self.addCleanup(patcher.stop)

        types_patcher = patch('src.widgets.tables.ClassifiedExpensesTable.ExpenseTypesService')
        types_patcher.start().return_value.get_not_computed_categories.return_value = []
        self.addCleanup(types_patcher.stop)

        self.service.get_classified_expenses.return_value = [ expense(1, 'Mercadona', -30.0), expense(2, 'Lidl', -20.0) ]

        self.table = ClassifiedExpensesTable(Mock(), 'expenses_raw')
        self.table.refresh_rows()
        self.table.selectRow(1)

    @patch('src.widgets.tables.ClassifiedExpensesTable.QtWidgets.QMessageBox.question', return_value = QMessageBox.StandardButton.Yes)
    def test__unclassify_selected__confirmed(self, question):
        self.table.unclassify_selected()

        question.assert_called_once()
        self.service.unclassify_expenses.assert_called_once_with([ 2 ])

    @patch('src.widgets.tables.ClassifiedExpensesTable.QtWidgets.QMessageBox.question', return_value = QMessageBox.StandardButton.No)
    def test__unclassify_selected__cancelled(self, question):
        self.table.unclassify_selected()

        self.service.unclassify_expenses.assert_not_called()
