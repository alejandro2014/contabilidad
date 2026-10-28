import unittest

from src.services.formatters.CashflowFormatter import CashflowFormatter

class CashflowFormatterTestCase(unittest.TestCase):
    def setUp(self):
        self.cashflow_formatter = CashflowFormatter()

    def test__format_cashflow__expenses_shown_as_positive_and_sorted(self):
        values = [ (0, 'Ocio', 1, -50.0), (0, 'Alimentación', 1, -100.0), (0, 'Alimentación', 3, -20.554) ]

        cashflow = self.cashflow_formatter.format_cashflow(values)

        expected_rows = [
            [ 'Alimentación', 100.0, None, 20.55 ] + [ None ] * 9 + [ 120.55 ],
            [ 'Ocio', 50.0 ] + [ None ] * 11 + [ 50.0 ]
        ]

        self.assertEqual(expected_rows, cashflow['expenses']['rows'])
        self.assertEqual([ 'Total gastos', 150.0, None, 20.55 ] + [ None ] * 9 + [ 170.55 ], cashflow['expenses']['total'])

    def test__format_cashflow__refunds_reduce_the_expenses(self):
        values = [ (0, 'Compras', 1, -80.0), (0, 'Bizum', 1, 30.0) ]

        cashflow = self.cashflow_formatter.format_cashflow(values)

        self.assertEqual([ 'Total gastos', 50.0 ] + [ None ] * 11 + [ 50.0 ], cashflow['expenses']['total'])

    def test__format_cashflow__incomes_in_their_own_section(self):
        values = [ (1, 'Nómina', 1, 2000.0), (0, 'Ocio', 1, -50.0) ]

        cashflow = self.cashflow_formatter.format_cashflow(values)

        self.assertEqual([ [ 'Nómina', 2000.0 ] + [ None ] * 11 + [ 2000.0 ] ], cashflow['incomes']['rows'])
        self.assertEqual([ [ 'Ocio', 50.0 ] + [ None ] * 11 + [ 50.0 ] ], cashflow['expenses']['rows'])

    def test__format_cashflow__balance_is_incomes_minus_expenses(self):
        values = [ (1, 'Nómina', 1, 2000.0), (0, 'Ocio', 1, -50.0), (0, 'Ocio', 2, -30.0) ]

        cashflow = self.cashflow_formatter.format_cashflow(values)

        self.assertEqual([ 'Balance', 1950.0, -30.0 ] + [ None ] * 10 + [ 1920.0 ], cashflow['balance'])

    def test__format_cashflow__empty(self):
        cashflow = self.cashflow_formatter.format_cashflow([])

        self.assertEqual([], cashflow['incomes']['rows'])
        self.assertEqual([], cashflow['expenses']['rows'])
        self.assertEqual([ 'Balance' ] + [ None ] * 13, cashflow['balance'])
