import math
import unittest
from unittest.mock import Mock, patch

import pandas as pd

from src.model.expense import Expense
from src.services.LoadFileService import LoadFileService

class LoadFileServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.load_file_service = LoadFileService()

    def test__find_xls_header_row(self):
        df = pd.DataFrame([ [ 'Movimientos de la cuenta' ], [ None ], [ ' f. valor ' ], [ '05/01/2026' ] ])

        self.assertEqual(2, self.load_file_service.find_xls_header_row(df))

    def test__find_xls_header_row__not_a_bank_statement(self):
        df = pd.DataFrame([ [ 'Fecha' ], [ '05/01/2026' ] ])

        with self.assertRaises(ValueError):
            self.load_file_service.find_xls_header_row(df)

    def test__format_amount__spanish_format(self):
        self.assertEqual(-1234.56, self.load_file_service.format_amount('-1.234,56 €'))
        self.assertEqual(50.0, self.load_file_service.format_amount('50,00'))

    def test__format_amount__numbers_are_kept(self):
        self.assertEqual(-12.5, self.load_file_service.format_amount(-12.5))

    def test__format_amount__not_an_amount(self):
        self.assertTrue(math.isnan(self.load_file_service.format_amount('Total')))

    def test__extract_expenses_from_xls__only_the_movements(self):
        rows = [
            [ 'Cuenta: ES00 0000', None, None, None, None, None, None ],
            [ 'F. VALOR', 'CATEGORÍA', 'SUBCATEGORÍA', 'DESCRIPCIÓN', 'COMENTARIO', 'IMPORTE (€)', 'SALDO (€)' ],
            [ '05/01/2026', 'Vivienda', 'Alquiler', 'Transferencia periódica', None, '-937,58', '1.000,00' ],
            [ '28/01/2026', 'Nómina', None, 'Nómina enero', 'Comentario', 2500.0, 3500.0 ],
            [ None, None, None, None, None, None, None ],
            [ 'Total', None, None, None, None, '1.562,42', None ]
        ]

        with patch('src.services.LoadFileService.pd.read_excel', return_value = pd.DataFrame(rows)):
            expenses = self.load_file_service.extract_expenses_from_xls('statement.xls')

        self.assertEqual(2, len(expenses))

        self.assertEqual(('20260105', 'Transferencia periódica', -937.58), (expenses[0].date, expenses[0].title, expenses[0].amount))
        self.assertEqual(('Vivienda', 'Alquiler'), (expenses[0].category_src, expenses[0].subcategory_src))

        self.assertEqual(('20260128', 'Nómina enero', 2500.0), (expenses[1].date, expenses[1].title, expenses[1].amount))
        self.assertIsNone(expenses[1].subcategory_src)

        # Every expense gets its own id
        self.assertNotEqual(expenses[0].id, expenses[1].id)

    def test__insert_expense_lines__classifies_before_saving(self):
        expenses = [ Expense(title = 'Pago en MERCADONA') ]

        self.load_file_service.rules_service = Mock()
        self.load_file_service.expenses_service = Mock()
        self.load_file_service.expenses_service.load_expenses.return_value = (3, 1)

        result = self.load_file_service.insert_expense_lines(expenses)

        self.load_file_service.rules_service.classify_expenses.assert_called_once_with(expenses)
        self.load_file_service.expenses_service.load_expenses.assert_called_once_with(expenses)
        self.assertEqual({ 'inserted': 3, 'ignored': 1 }, result)
