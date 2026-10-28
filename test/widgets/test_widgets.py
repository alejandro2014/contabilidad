import datetime
import unittest
from unittest.mock import Mock, patch

from test.qt_app import get_app

from src.widgets.DateFilterWidget import DateFilterWidget
from src.widgets.KpiCards import KpiCards
from src.widgets.Summatory import Summatory
from src.widgets.charts.ChartPalette import ChartPalette

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

    def this_year(self):
        return datetime.date.today().year

    def last_day_of_february(self):
        return (datetime.date(self.this_year(), 3, 1) - datetime.timedelta(days=1)).day

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
