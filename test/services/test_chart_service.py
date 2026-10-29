import unittest
from unittest.mock import Mock

from src.services.ChartService import ChartService

class ChartServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.chart_service = ChartService()
        self.chart_service.db = Mock()

        self.filter = { 'date': { 'from': '20260101', 'to': '20260331' } }
        self.no_dates_filter = { 'date': { 'from': None, 'to': None } }

    def test__get_bar_chart_info__expenses_and_incomes_aligned_by_month(self):
        expenses = [ ('202601', -100.0), ('202603', -50.0) ]
        incomes = [ ('202602', 2000.0) ]
        self.chart_service.db.select.side_effect = [ expenses, incomes ]

        bar_info = self.chart_service.get_bar_chart_info(self.filter)

        self.assertEqual([ 'Enero', 'Febrero', 'Marzo' ], bar_info['months'])
        self.assertEqual([ 100.0, 0.0, 50.0 ], bar_info['amounts'])
        self.assertEqual([ 0.0, 2000.0, 0.0 ], bar_info['incomes'])

    def test__no_dates__no_queries(self):
        self.assertEqual({}, self.chart_service.get_pie_chart_info(self.no_dates_filter))
        self.assertEqual([], self.chart_service.get_bar_chart_info(self.no_dates_filter)['amounts'])
        self.assertEqual({}, self.chart_service.get_evolution_chart_info(self.no_dates_filter, [ 'Comida' ])['series'])
        self.assertEqual([], self.chart_service.get_top_expenses(self.no_dates_filter))

        self.chart_service.db.select.assert_not_called()

    def test__get_evolution_chart_info__only_the_given_categories(self):
        values = [ ('Comida', '202601', -100.0), ('Salir', '202601', -40.0) ]
        self.chart_service.db.select.return_value = values

        evolution = self.chart_service.get_evolution_chart_info(self.filter, [ 'Comida' ])

        self.assertEqual({ 'Comida': [ 100.0, 0.0, 0.0 ] }, evolution['series'])

    def test__get_kpis__pending_expenses_of_the_period(self):
        self.chart_service.db.select.return_value = [ (7,) ]
        bar_info = { 'months': [ 'Enero' ], 'amounts': [ 100.0 ], 'incomes': [ 0.0 ] }

        kpis = self.chart_service.get_kpis(self.filter, {}, bar_info)

        self.assertEqual(7, kpis['pending'])
        self.assertEqual(('20260101', '20260331'), self.chart_service.db.select.call_args[0][0][1])

    def test__get_kpis__no_pending_without_dates(self):
        bar_info = { 'months': [], 'amounts': [], 'incomes': [] }

        kpis = self.chart_service.get_kpis(self.no_dates_filter, {}, bar_info)

        self.assertEqual(0, kpis['pending'])
        self.chart_service.db.select.assert_not_called()

    def test__get_merchants_info__merchants_of_the_category(self):
        self.chart_service.db.select.return_value = [ ('Pago en MERCADONA MADRID ES', -30.0), ('Pago en LIDL MADRID ES', -10.0) ]

        merchants = self.chart_service.get_merchants_info(self.filter, 'Comida')

        self.assertEqual({ 'Mercadona': 30.0, 'Lidl': 10.0 }, merchants)
        self.assertEqual('Comida', self.chart_service.db.select.call_args[0][0][1][0])

    def test__get_merchants_info__no_dates__no_queries(self):
        self.assertEqual({}, self.chart_service.get_merchants_info(self.no_dates_filter, 'Comida'))
        self.chart_service.db.select.assert_not_called()

    def test__get_kpis__compared_with_the_previous_period(self):
        # Pending count, then the expenses and incomes of October-December
        self.chart_service.db.select.side_effect = [ [ (0,) ], [ ('202510', -50.0), ('202511', -50.0) ], [] ]
        bar_info = { 'months': [ 'Enero', 'Febrero', 'Marzo' ], 'amounts': [ 100.0, 0.0, 20.0 ], 'incomes': [ 0.0, 0.0, 0.0 ] }

        kpis = self.chart_service.get_kpis(self.filter, {}, bar_info, 'previous')

        self.assertEqual(('20251001', '20251231'), self.chart_service.db.select.call_args_list[1][0][0][1])
        self.assertEqual(20.0, kpis['changes']['expenses'])

    def test__get_kpis__no_comparison(self):
        self.chart_service.db.select.return_value = [ (0,) ]
        bar_info = { 'months': [ 'Enero' ], 'amounts': [ 100.0 ], 'incomes': [ 0.0 ] }

        kpis = self.chart_service.get_kpis(self.filter, {}, bar_info)

        self.assertIsNone(kpis['changes'])
        self.assertEqual(1, self.chart_service.db.select.call_count)

    def test__expenses_filter__month_inside_the_range(self):
        filter = { 'date': { 'from': '20260115', 'to': '20260310' } }

        self.assertEqual({ 'date': { 'from': '20260115', 'to': '20260131' }, 'category': 'Comida', 'search_value': None },
                         self.chart_service.expenses_filter(filter, '202601', 'Comida'))
        self.assertEqual({ 'from': '20260301', 'to': '20260310' }, self.chart_service.expenses_filter(filter, '202603')['date'])

    def test__expenses_filter__whole_range(self):
        self.assertEqual({ 'date': { 'from': '20260101', 'to': '20260331' }, 'category': 'Comida', 'search_value': 'Mercadona' },
                         self.chart_service.expenses_filter(self.filter, category = 'Comida', search_value = 'Mercadona'))

    def test__get_category_average_info__the_12_months_before_the_end_of_the_range(self):
        self.chart_service.db.select.return_value = [ ('Comida', '202603', -100.0) ]

        average = self.chart_service.get_category_average_info(self.filter)

        self.assertEqual(('20250301', '20260331'), self.chart_service.db.select.call_args[0][0][1])
        self.assertEqual('202603', average['year_month'])

    def test__get_balance_chart_info__balances_until_the_end_of_the_range(self):
        self.chart_service.db.select.return_value = [ ('20251220', -10.0, 500.0) ]

        balances = self.chart_service.get_balance_chart_info(self.filter)

        self.assertEqual(('20260331',), self.chart_service.db.select.call_args[0][0][1])
        self.assertEqual([ 500.0, 500.0, 500.0 ], balances['balances'])

    def test__no_dates__no_average_nor_balances(self):
        self.assertIsNone(self.chart_service.get_category_average_info(self.no_dates_filter))
        self.assertEqual([], self.chart_service.get_balance_chart_info(self.no_dates_filter)['balances'])

        self.chart_service.db.select.assert_not_called()
