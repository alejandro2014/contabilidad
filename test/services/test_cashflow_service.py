import os
import tempfile
import unittest
from unittest.mock import Mock

from src.services.CashflowService import CashflowService

class CashflowServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.cashflow_service = CashflowService()
        self.cashflow_service.db = Mock()

    def test__get_cashflow__formats_the_query_rows(self):
        self.cashflow_service.db.select.return_value = [ (1, 'Nómina', 1, 2000.0), (0, 'Comida', 1, -150.0) ]

        cashflow = self.cashflow_service.get_cashflow('2026', 'type')

        self.assertEqual([ 'Balance', 1850.0 ] + [ None ] * 11 + [ 1850.0, 92.5 ], cashflow['balance'])
        self.assertEqual(('2026%',), self.cashflow_service.db.select.call_args[0][0][1])

    def test__export_cashflow__tab_separated_with_empty_cells(self):
        header = [ 'Categoría', 'Enero', 'Febrero', 'Total' ]
        rows = [ [ 'Comida', 100.5, None, 100.5 ], [ '', None, None, None ] ]

        with tempfile.TemporaryDirectory() as directory:
            file_name = os.path.join(directory, 'cashflow.csv')

            self.cashflow_service.export_cashflow(file_name, header, rows)

            with open(file_name, encoding='utf-8') as f:
                content = f.read()

        self.assertEqual('Categoría\tEnero\tFebrero\tTotal\nComida\t100.50\t\t100.50\n\t\t\t\n', content)
