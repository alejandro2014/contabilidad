import datetime
import unittest
from unittest.mock import Mock, patch

from test.qt_app import clear_settings, get_app

from src.widgets.DateFilterWidget import DateFilterWidget
from src.widgets.FilterWidget import FilterWidget
from src.widgets.KpiCards import KpiCards
from src.widgets.SearchFilter import SearchFilter
from src.widgets.Summatory import Summatory
from src.widgets.charts.BarChart import BarChart
from src.widgets.charts.ChartPalette import ChartPalette
from src.widgets.charts.PieChart import PieChart
from src.widgets.charts.Treemap import Treemap

from src.services.formatters.ChartFormatter import ChartFormatter

from PySide6.QtCharts import QChart
from PySide6.QtCore import QRectF

class SummatoryTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        self.summatory = Summatory(Mock())

    def test__sum_from_amounts__expenses_shown_as_positive(self):
        # The tables have the amounts as stored: expenses are negative
        self.summatory.update_expenses_sum_from_amounts([ '-100.5', -20, '30' ])

        self.assertEqual('90,50 €', self.summatory.lbl.text())

    def test__sum_from_amounts__no_negative_zero(self):
        self.summatory.update_expenses_sum_from_amounts([ -10, 10 ])

        self.assertEqual('0,00 €', self.summatory.lbl.text())

    def test__sum_from_chart__already_positive(self):
        self.summatory.update_expenses_sum_from_chart([ 1000.0, 234.567 ])

        self.assertEqual('1.234,57 €', self.summatory.lbl.text())

class DateFilterWidgetTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        clear_settings()
        self.pool = Mock()
        self.date_filter = DateFilterWidget(self.pool)
        self.pool.send_event.reset_mock()

    def test__change_filter_dates__a_single_event(self):
        # Changing the six combos must reload the screen only once
        self.date_filter.change_filter_dates(f'{self.this_year() - 1}0215', f'{self.this_year()}1130')

        self.pool.send_event.assert_called_once_with('filter-widget', 'change_dates', {
            'from': f'{self.this_year() - 1}0215',
            'to': f'{self.this_year()}1130'
        })

    def test__change_filter_dates__years_before_the_combo_use_the_first_one(self):
        first_year = self.date_filter.cbx['from']['year'].itemText(0)

        self.date_filter.change_filter_dates('19990101', f'{self.this_year()}0101')

        dates = self.pool.send_event.call_args[0][2]
        self.assertEqual(f'{first_year}0101', dates['from'])

    def test__select_period(self):
        with patch('src.widgets.DateFilterWidget.datetime') as mock_datetime:
            mock_datetime.date.today.return_value = datetime.date(self.this_year(), 3, 15)

            self.date_filter.select_period('last_month')

        dates = self.pool.send_event.call_args[0][2]
        self.assertEqual({ 'from': f'{self.this_year()}0201', 'to': f'{self.this_year()}02{self.last_day_of_february()}' }, dates)

    def test__select_period__all_from_the_first_year_of_the_combo(self):
        first_year = self.date_filter.cbx['from']['year'].itemText(0)

        self.date_filter.select_period('all')

        dates = self.pool.send_event.call_args[0][2]
        self.assertEqual({ 'from': f'{first_year}0101', 'to': datetime.date.today().strftime('%Y%m%d') }, dates)

    def this_year(self):
        return datetime.date.today().year

    def test__new_session__this_year(self):
        pool = Mock()

        DateFilterWidget(pool)

        today = datetime.date.today()
        self.assertEqual({ 'from': f'{today.year}0101', 'to': today.strftime('%Y%m%d') }, pool.send_event.call_args[0][2])

    def test__last_range_remembered(self):
        self.date_filter.change_filter_dates(f'{self.this_year() - 1}0215', f'{self.this_year()}0110')
        pool = Mock()

        DateFilterWidget(pool)

        self.assertEqual({ 'from': f'{self.this_year() - 1}0215', 'to': f'{self.this_year()}0110' }, pool.send_event.call_args[0][2])

    def test__range_set_by_the_app_not_remembered(self):
        self.date_filter.change_filter_dates(f'{self.this_year()}0201', f'{self.this_year()}0228', remember=False)
        pool = Mock()

        DateFilterWidget(pool)

        self.assertEqual(f'{self.this_year()}0101', pool.send_event.call_args[0][2]['from'])

    def last_day_of_february(self):
        return (datetime.date(self.this_year(), 3, 1) - datetime.timedelta(days=1)).day

class SearchFilterTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        self.pool = Mock()

        with patch('src.widgets.SearchFilter.ComboBoxService') as mock_service:
            mock_service.return_value.get_categories.return_value = [ 'Alquiler', 'Comida' ]
            mock_service.return_value.get_tags.return_value = [ 'Viaje' ]
            self.search_filter = SearchFilter(self.pool, True)

    def test__get_search__nothing_typed(self):
        self.assertEqual({
            'search_value': None,
            'amount': { 'from': None, 'to': None },
            'category': None,
            'tag': None
        }, self.search_filter.get_search())

    def test__get_search__all_the_fields(self):
        self.search_filter.line_edit.setText('mercadona')
        self.search_filter.amount_from.setText('10,5')
        self.search_filter.amount_to.setText('-20')
        self.search_filter.categories.setCurrentText('Comida')
        self.search_filter.tags.setCurrentText('Viaje')

        self.assertEqual({
            'search_value': 'mercadona',
            'amount': { 'from': 10.5, 'to': 20.0 },
            'category': 'Comida',
            'tag': 'Viaje'
        }, self.search_filter.get_search())

    def test__get_search__a_single_letter_and_wrong_amounts_are_ignored(self):
        self.search_filter.line_edit.setText('m')
        self.search_filter.amount_from.setText('12,')
        self.search_filter.amount_to.setText('abc')

        search = self.search_filter.get_search()

        self.assertIsNone(search['search_value'])
        self.assertEqual(12.0, search['amount']['from'])
        self.assertIsNone(search['amount']['to'])

    def test__get_search__no_category_without_the_combo(self):
        with patch('src.widgets.SearchFilter.ComboBoxService'):
            search_filter = SearchFilter(self.pool, False)

        self.assertIsNone(search_filter.get_search()['category'])

    def test__clear__sends_an_empty_search(self):
        self.search_filter.line_edit.setText('mercadona')
        self.search_filter.categories.setCurrentText('Comida')
        self.pool.send_event.reset_mock()

        self.search_filter.clear()

        self.pool.send_event.assert_called_once_with('filter-widget', 'change_search', {
            'search_value': None,
            'amount': { 'from': None, 'to': None },
            'category': None,
            'tag': None
        })

class KpiCardsTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        self.kpi_cards = KpiCards()

    def test__reload__savings(self):
        self.kpi_cards.reload(self.kpis(balance = 500.0, savings_rate = 20.0))

        self.assertEqual('+500,00 €', self.kpi_cards.cards['balance'].value.text())
        self.assertIn(ChartPalette.GOOD, self.kpi_cards.cards['balance'].value.styleSheet())
        self.assertEqual('+20.0%', self.kpi_cards.cards['savings_rate'].value.text())

    def test__reload__spending_more_than_the_incomes(self):
        self.kpi_cards.reload(self.kpis(balance = -200.0, savings_rate = -10.0))

        self.assertEqual('-200,00 €', self.kpi_cards.cards['balance'].value.text())
        self.assertIn(ChartPalette.CRITICAL, self.kpi_cards.cards['balance'].value.styleSheet())

    def test__reload__no_data(self):
        self.kpi_cards.reload(self.kpis(savings_rate = None, top_category = None, max_month = None, pending = 0))

        self.assertEqual('-', self.kpi_cards.cards['savings_rate'].value.text())
        self.assertEqual('Sin ingresos', self.kpi_cards.cards['savings_rate'].detail.text())
        self.assertEqual('-', self.kpi_cards.cards['top_category'].value.text())
        self.assertEqual('Todo clasificado', self.kpi_cards.cards['pending'].detail.text())

    def test__reload__pending_expenses_warn(self):
        self.kpi_cards.reload(self.kpis(pending = 4))

        self.assertEqual('4', self.kpi_cards.cards['pending'].value.text())
        self.assertIn(ChartPalette.WARNING, self.kpi_cards.cards['pending'].value.styleSheet())
        self.assertFalse(self.kpi_cards.pending_button.isHidden())

    def test__reload__no_button_without_pending_expenses(self):
        self.kpi_cards.reload(self.kpis(pending = 0))

        self.assertTrue(self.kpi_cards.pending_button.isHidden())

    def test__reload__compared_with_the_previous_period(self):
        changes = { 'expenses': 12.4, 'incomes': None, 'monthly_average': -0.3, 'balance': -120.0, 'savings_rate': 3.25 }

        self.kpi_cards.reload(self.kpis(changes = changes), 'previous')

        self.assertEqual('+12 % vs. periodo anterior', self.kpi_cards.cards['expenses'].detail.text())
        self.assertEqual('Sin datos para comparar', self.kpi_cards.cards['incomes'].detail.text())
        self.assertEqual('+0 % vs. periodo anterior', self.kpi_cards.cards['monthly_average'].detail.text())
        self.assertEqual('-120,00 € vs. periodo anterior', self.kpi_cards.cards['balance'].detail.text())
        self.assertEqual('+3,2 pp vs. periodo anterior', self.kpi_cards.cards['savings_rate'].detail.text())

    def test__reload__not_compared(self):
        self.kpi_cards.reload(self.kpis(changes = None))

        self.assertEqual('', self.kpi_cards.cards['expenses'].detail.text())
        self.assertEqual('Ingresos - gastos', self.kpi_cards.cards['balance'].detail.text())

    def kpis(self, **values):
        kpis = {
            'expenses': 1000.0,
            'incomes': 1500.0,
            'balance': 500.0,
            'savings_rate': 33.3,
            'monthly_average': 1000.0,
            'top_category': { 'name': 'Alquiler', 'amount': 900.0 },
            'max_month': { 'name': 'Enero', 'amount': 1000.0 },
            'pending': 0
        }
        kpis.update(values)

        return kpis

class TreemapTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        self.treemap = Treemap()

    def test__set_data__biggest_first_without_negative_amounts(self):
        self.treemap.set_data([ ('Ocio', 25.0), ('Bizum', -10.0), ('Comida', 75.0), ('Vacío', None) ])

        self.assertEqual([ ('Comida', 75.0, 75.0), ('Ocio', 25.0, 25.0) ], self.treemap.items)

    def test__split_rectangles__each_piece_cuts_the_space_left(self):
        self.treemap.set_data([ ('Comida', 60.0), ('Ocio', 20.0), ('Compras', 20.0) ])

        rectangles = self.treemap.split_rectangles(QRectF(0, 0, 100, 50))

        # 60 % of the width, then half of the remaining 40x50 cut along its height
        self.assertEqual([ QRectF(0, 0, 60, 50), QRectF(60, 0, 40, 25), QRectF(60, 25, 40, 25) ], rectangles)

    def test__split_rectangles__groups_pieces_in_rows(self):
        self.treemap.set_data([ ('Comida', 25.0), ('Ocio', 25.0), ('Compras', 25.0), ('Casa', 25.0) ])

        rectangles = self.treemap.split_rectangles(QRectF(0, 0, 100, 100))

        # Two pieces share the first column instead of cutting the space one by one
        self.assertEqual([ QRectF(0, 0, 50, 50), QRectF(0, 50, 50, 50), QRectF(50, 0, 50, 50), QRectF(50, 50, 50, 50) ], rectangles)

    def test__split_rectangles__no_data(self):
        self.treemap.set_data([])

        self.assertEqual([], self.treemap.split_rectangles(QRectF(0, 0, 100, 50)))

class PieChartTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        self.pie_chart = PieChart()
        self.pie_chart.chart_service = Mock()
        self.pie_chart.chart_service.formatter = ChartFormatter()

        # Ten categories, so the two smallest are grouped in "Otros"
        self.categories = { f'Categoría {i}': 100.0 - i for i in range(10) }
        self.pie_chart.chart_service.get_chart_info.return_value = self.categories
        self.pie_chart.reload({ 'date': { 'from': '20260101', 'to': '20260131' } })

    def test__reload__categories_with_others(self):
        self.assertEqual(8, len(self.pie_chart.series.slices()))
        self.assertTrue(self.pie_chart.back_button.isHidden())

    def test__reload__dark_mode(self):
        with patch.object(ChartPalette, 'is_dark', return_value = True):
            self.pie_chart.reload(self.pie_chart.filter)

        self.assertEqual(QChart.ChartTheme.ChartThemeDark, self.pie_chart.chart().theme())
        # The gaps between the slices have the color of the dark background, and the colors of the categories are kept
        slice = self.pie_chart.series.slices()[0]
        self.assertEqual(ChartPalette().background_color(self.pie_chart.chart()), slice.pen().color())
        self.assertEqual(ChartPalette.SERIES[0], slice.brush().color().name())

    def test__zoom_in__category_shows_its_merchants(self):
        self.pie_chart.chart_service.get_merchants_info.return_value = { 'Mercadona': 60.0, 'Lidl': 40.0 }

        self.pie_chart.zoom_in('Categoría 0')

        self.pie_chart.chart_service.get_merchants_info.assert_called_once_with(self.pie_chart.filter, 'Categoría 0')
        self.assertEqual(2, len(self.pie_chart.series.slices()))
        self.assertEqual('Gastos por categoría › Categoría 0', self.pie_chart.chart().title())
        self.assertFalse(self.pie_chart.back_button.isHidden())

    def test__zoom_in__others_shows_the_small_categories(self):
        self.pie_chart.zoom_in('Otros')

        self.assertEqual({ 'Categoría 7': 93.0, 'Categoría 8': 92.0, 'Categoría 9': 91.0 }, self.pie_chart.levels[-1]['items'])
        # They are still categories, so they can show their merchants
        self.assertEqual('category', self.pie_chart.levels[-1]['kind'])

    def test__zoom_in__merchant_opens_its_movements(self):
        self.pie_chart.chart_service.get_merchants_info.return_value = { 'Mercadona': 60.0 }
        self.pie_chart.chart_service.expenses_filter.return_value = { 'category': 'Categoría 8' }
        opened = []
        self.pie_chart.open_expenses.connect(opened.append)
        self.pie_chart.zoom_in('Otros')
        self.pie_chart.zoom_in('Categoría 8')

        self.pie_chart.zoom_in('Mercadona')

        # The category is the one with the merchants, not "Otros"
        self.assertEqual(3, len(self.pie_chart.levels))
        self.pie_chart.chart_service.expenses_filter.assert_called_once_with(self.pie_chart.filter, category = 'Categoría 8', search_value = 'Mercadona')
        self.assertEqual([ { 'category': 'Categoría 8' } ], opened)

    def test__zoom_out__back_to_the_previous_level(self):
        self.pie_chart.zoom_in('Otros')
        self.pie_chart.zoom_out()
        self.pie_chart.zoom_out()

        self.assertEqual(1, len(self.pie_chart.levels))
        self.assertEqual(8, len(self.pie_chart.series.slices()))
        self.assertTrue(self.pie_chart.back_button.isHidden())

class FilterWidgetTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        clear_settings()
        self.pool = Mock()

        with patch('src.services.ComboBoxService.ExpenseTypesService') as types_service, patch('src.services.ComboBoxService.ExpensesService') as expenses_service:
            types_service.return_value.get_categories_simple.return_value = [ 'Alquiler', 'Comida' ]
            expenses_service.return_value.get_tags.return_value = [ 'Viaje' ]
            self.filter_widget = FilterWidget('classified', self.pool)

    def test__set_filter__shown_and_not_remembered(self):
        year = datetime.date.today().year

        self.filter_widget.set_filter({ 'date': { 'from': f'{year}0201', 'to': f'{year}0228' }, 'category': 'Comida', 'search_value': 'Mercadona' })

        self.assertEqual('Mercadona', self.filter_widget.search_filter.line_edit.text())
        self.assertEqual('Comida', self.filter_widget.search_filter.categories.currentText())
        self.assertEqual('Comida', self.filter_widget.filter['category'])
        self.pool.send_event.assert_called_with('filter-widget', 'change_dates', { 'from': f'{year}0201', 'to': f'{year}0228' })

        # The last range chosen by the user is still the one of the next screen
        pool = Mock()
        DateFilterWidget(pool)
        self.assertEqual(f'{year}0101', pool.send_event.call_args[0][2]['from'])

class BarChartTestCase(unittest.TestCase):
    def setUp(self):
        get_app()
        self.bar_chart = BarChart()
        self.bar_chart.chart_service.db = Mock()
        self.bar_chart.chart_service.db.select.side_effect = [ [ ('202601', -100.0) ], [] ]
        self.bar_chart.reload({ 'date': { 'from': '20260115', 'to': '20260310' } })

    def test__bar_clicked__movements_of_its_month(self):
        opened = []
        self.bar_chart.open_expenses.connect(opened.append)

        self.bar_chart.bar_clicked(0)

        self.assertEqual([ { 'date': { 'from': '20260115', 'to': '20260131' }, 'category': None, 'search_value': None } ], opened)
