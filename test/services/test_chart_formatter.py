import unittest

from src.services.formatters.ChartFormatter import ChartFormatter

class ChartFormatterTestCase(unittest.TestCase):
    def setUp(self):
        self.chart_formatter = ChartFormatter()

    def test__format_income_expense_values__refunds_are_subtracted(self):
        values = self.chart_formatter.format_income_expense_values([ ('202601', 30.0) ], [], [ '202601' ])

        self.assertEqual([ -30.0 ], values['amounts'])

    def test__format_income_expense_values__labels_with_year_when_several_years(self):
        values = self.chart_formatter.format_income_expense_values([], [], [ '202512', '202601' ])

        self.assertEqual([ 'Diciembre 2025', 'Enero 2026' ], values['months'])
        self.assertEqual([ 'Dic 25', 'Ene 26' ], values['short_months'])

    def test__format_income_expense_values__empty(self):
        values = self.chart_formatter.format_income_expense_values([], [], [])

        self.assertEqual({ 'months': [], 'short_months': [], 'amounts': [], 'incomes': [] }, values)

    def test__format_categories__expenses_as_positive_amounts(self):
        categories = [ ('Alquiler', -900.0), ('Comida', -123.456) ]

        dict_categories = self.chart_formatter.format_categories(categories)

        self.assertEqual({ 'Alquiler': 900.0, 'Comida': 123.46 }, dict_categories)

    def test__format_categories__leaves_out_categories_with_more_refunds_than_expenses(self):
        categories = [ ('Comida', -100.0), ('Bizum', 139.0) ]

        dict_categories = self.chart_formatter.format_categories(categories)

        self.assertEqual({ 'Comida': 100.0 }, dict_categories)

    def test__merchant_name__chain_without_branch_nor_town(self):
        self.assertEqual('Mercadona', self.chart_formatter.merchant_name('Pago en MERCADONA C ALFREDO MARQUMADRID ES'))
        self.assertEqual('Alcampo', self.chart_formatter.merchant_name('Pago en ALCAMPO28029-VAGUADA MADRID ES'))

    def test__merchant_name__several_prefixes_and_articles(self):
        self.assertEqual('Cortefiel', self.chart_formatter.merchant_name('Devolución Tarjeta PAYPAL *CORTEFIEL 1846 901363040 ES'))
        self.assertEqual('Corte', self.chart_formatter.merchant_name('Pago en EL CORTE INGLES SANCHINARMADRID ES'))
        self.assertEqual('Amazon', self.chart_formatter.merchant_name('Devolución Tarjeta WWW.AMAZON* 8K1U12745 LUXEMBOURG LU'))

    def test__merchant_name__without_words_keeps_the_title(self):
        self.assertEqual('1234', self.chart_formatter.merchant_name('1234'))

    def test__format_merchants__branches_added_up_and_refunds_subtracted(self):
        titles = [ ('Pago en MERCADONA MADRID ES', -50.0), ('Pago en MERCADONA LEON ES', -30.0),
                   ('Pago en ZARA MADRID ES', -40.0), ('Devolución Tarjeta ZARA MADRID ES', 40.0),
                   ('Pago en LIDL MADRID ES', -90.0) ]

        merchants = self.chart_formatter.format_merchants(titles)

        # Biggest first, and Zara is left out as everything was refunded
        self.assertEqual([ ('Lidl', 90.0), ('Mercadona', 80.0) ], list(merchants.items()))

    def test__year_months__same_month(self):
        self.assertEqual([ '202602' ], self.chart_formatter.year_months('20260201', '20260228'))

    def test__year_months__across_years(self):
        year_months = self.chart_formatter.year_months('20251115', '20260210')

        self.assertEqual([ '202511', '202512', '202601', '202602' ], year_months)

    def test__format_income_expense_values__months_without_movements_are_zero(self):
        expenses = [ ('202601', -100.0), ('202603', -30.0) ]
        incomes = [ ('202601', 1000.0) ]

        values = self.chart_formatter.format_income_expense_values(expenses, incomes, [ '202601', '202602', '202603' ])

        self.assertEqual([ 'Enero', 'Febrero', 'Marzo' ], values['months'])
        self.assertEqual([ 'Ene', 'Feb', 'Mar' ], values['short_months'])
        self.assertEqual([ 100.0, 0.0, 30.0 ], values['amounts'])
        self.assertEqual([ 1000.0, 0.0, 0.0 ], values['incomes'])

    def test__format_category_evolution__one_series_per_category(self):
        values = [ ('Comida', '202512', -50.0), ('Alquiler', '202601', -900.0), ('Salir', '202601', -20.0) ]

        evolution = self.chart_formatter.format_category_evolution(values, [ 'Alquiler', 'Comida' ], [ '202512', '202601' ])

        self.assertEqual([ 'Dic 25', 'Ene 26' ], evolution['short_months'])
        self.assertEqual({ 'Alquiler': [ 0.0, 900.0 ], 'Comida': [ 50.0, 0.0 ] }, evolution['series'])

    def test__format_top_expenses(self):
        expenses = [ ('20260529', '20260529', 'Vuelo', 'Vacaciones', -2400.2, 1) ]

        top_expenses = self.chart_formatter.format_top_expenses(expenses)

        self.assertEqual([ { 'date': '29/05/2026', 'title': 'Vuelo', 'category': 'Vacaciones', 'amount': 2400.2, 'count': 1 } ], top_expenses)

    def test__format_top_expenses__repeated_ones_show_the_dates_range(self):
        expenses = [ ('20260105', '20260405', 'Transferencia periódica', 'Alquiler', -937.58, 4) ]

        top_expenses = self.chart_formatter.format_top_expenses(expenses)

        self.assertEqual([ { 'date': '05/01/2026 - 05/04/2026', 'title': 'Transferencia periódica', 'category': 'Alquiler', 'amount': 937.58, 'count': 4 } ], top_expenses)

    def test__group_categories__smallest_added_to_others(self):
        categories = { 'A': 50.0, 'B': 30.0, 'C': 15.0, 'D': 5.0 }

        grouped = self.chart_formatter.group_categories(categories, 3)

        self.assertEqual({ 'A': 50.0, 'B': 30.0, 'Otros': 20.0 }, grouped)

    def test__group_categories__no_others_when_they_fit(self):
        categories = { 'A': 50.0, 'B': 30.0 }

        self.assertEqual(categories, self.chart_formatter.group_categories(categories, 3))

    def test__format_kpis(self):
        bar_info = { 'months': [ 'Enero', 'Febrero' ], 'amounts': [ 300.0, 500.0 ], 'incomes': [ 1000.0, 0.0 ] }

        kpis = self.chart_formatter.format_kpis({ 'Alquiler': 600.0, 'Comida': 200.0 }, bar_info, 3)

        self.assertEqual(800.0, kpis['expenses'])
        self.assertEqual(1000.0, kpis['incomes'])
        self.assertEqual(200.0, kpis['balance'])
        self.assertEqual(20.0, kpis['savings_rate'])
        self.assertEqual(400.0, kpis['monthly_average'])
        self.assertEqual({ 'name': 'Alquiler', 'amount': 600.0 }, kpis['top_category'])
        self.assertEqual({ 'name': 'Febrero', 'amount': 500.0 }, kpis['max_month'])
        self.assertEqual(3, kpis['pending'])

    def test__format_kpis__spending_more_than_the_incomes(self):
        bar_info = { 'months': [ 'Enero' ], 'amounts': [ 1200.0 ], 'incomes': [ 1000.0 ] }

        kpis = self.chart_formatter.format_kpis({ 'Alquiler': 1200.0 }, bar_info, 0)

        self.assertEqual(-200.0, kpis['balance'])
        self.assertEqual(-20.0, kpis['savings_rate'])

    def test__format_kpis__no_max_month_when_there_are_only_refunds(self):
        bar_info = { 'months': [ 'Enero' ], 'amounts': [ -10.0 ], 'incomes': [ 0.0 ] }

        kpis = self.chart_formatter.format_kpis({}, bar_info, 0)

        self.assertIsNone(kpis['max_month'])

    def test__format_kpis__no_savings_rate_without_incomes(self):
        bar_info = { 'months': [], 'amounts': [], 'incomes': [] }

        kpis = self.chart_formatter.format_kpis({}, bar_info, 0)

        self.assertIsNone(kpis['savings_rate'])
        self.assertIsNone(kpis['top_category'])
        self.assertIsNone(kpis['max_month'])
        self.assertEqual(0.0, kpis['monthly_average'])
