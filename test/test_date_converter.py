import datetime
import unittest

from DateConverter import DateConverter

class DateConverterTestCase(unittest.TestCase):
    def setUp(self):
        self.date_converter = DateConverter()

    def test__format_raw_dmy__pads_day_and_month(self):
        self.assertEqual('20260105', self.date_converter.format_raw_dmy(5, 1, '2026'))
        self.assertEqual('20261231', self.date_converter.format_raw_dmy(31, 12, '2026'))

    def test__format_pretty(self):
        self.assertEqual('05/01/2026', self.date_converter.format_pretty('20260105'))

    def test__period_dates__this_month(self):
        self.assert_period('this_month', datetime.date(2026, 10, 28), datetime.date(2026, 10, 1), datetime.date(2026, 10, 28))

    def test__period_dates__last_month_ends_on_its_last_day(self):
        self.assert_period('last_month', datetime.date(2026, 3, 31), datetime.date(2026, 2, 1), datetime.date(2026, 2, 28))

    def test__period_dates__last_month_in_a_leap_year(self):
        self.assert_period('last_month', datetime.date(2028, 3, 15), datetime.date(2028, 2, 1), datetime.date(2028, 2, 29))

    def test__period_dates__last_month_in_january_is_previous_december(self):
        self.assert_period('last_month', datetime.date(2026, 1, 15), datetime.date(2025, 12, 1), datetime.date(2025, 12, 31))

    def test__period_dates__last_3_months_include_the_current_one(self):
        self.assert_period('last_3_months', datetime.date(2026, 10, 28), datetime.date(2026, 8, 1), datetime.date(2026, 10, 28))

    def test__period_dates__last_3_months_across_years(self):
        self.assert_period('last_3_months', datetime.date(2026, 1, 15), datetime.date(2025, 11, 1), datetime.date(2026, 1, 15))

    def test__period_dates__last_12_months(self):
        self.assert_period('last_12_months', datetime.date(2026, 10, 28), datetime.date(2025, 11, 1), datetime.date(2026, 10, 28))

    def test__period_dates__last_12_months_from_december(self):
        self.assert_period('last_12_months', datetime.date(2026, 12, 5), datetime.date(2026, 1, 1), datetime.date(2026, 12, 5))

    def test__period_dates__this_year(self):
        self.assert_period('this_year', datetime.date(2026, 10, 28), datetime.date(2026, 1, 1), datetime.date(2026, 10, 28))

    def test__period_dates__last_year(self):
        self.assert_period('last_year', datetime.date(2026, 10, 28), datetime.date(2025, 1, 1), datetime.date(2025, 12, 31))

    def assert_period(self, period, today, expected_from, expected_to):
        self.assertEqual((expected_from, expected_to), self.date_converter.period_dates(period, today))

    def test__month_dates__last_day_of_the_month(self):
        self.assertEqual(('20240201', '20240229'), self.date_converter.month_dates('202402'))
        self.assertEqual(('20261201', '20261231'), self.date_converter.month_dates('202612'))

    def test__comparison_dates__previous_part_of_a_month(self):
        # This month until today, compared with the same days of the month before
        self.assertEqual(('20260901', '20260929'), self.date_converter.comparison_dates('20261001', '20261029', 'previous'))

    def test__comparison_dates__previous_whole_months(self):
        self.assertEqual(('20251001', '20251231'), self.date_converter.comparison_dates('20260101', '20260331', 'previous'))
        self.assertEqual(('20250101', '20250131'), self.date_converter.comparison_dates('20250201', '20250228', 'previous'))

    def test__comparison_dates__previous_month_end_to_a_longer_month(self):
        self.assertEqual(('20251101', '20251130'), self.date_converter.comparison_dates('20251201', '20251231', 'previous'))
        # The end of the month is the end of the other month, not the same day
        self.assertEqual(('20260301', '20260331'), self.date_converter.comparison_dates('20260401', '20260430', 'previous'))

    def test__comparison_dates__previous_days(self):
        # Ranges that don't start on the first day are compared with the same number of days before them
        self.assertEqual(('20260925', '20261004'), self.date_converter.comparison_dates('20261005', '20261014', 'previous'))

    def test__comparison_dates__last_year(self):
        self.assertEqual(('20250101', '20251029'), self.date_converter.comparison_dates('20260101', '20261029', 'last_year'))
        self.assertEqual(('20230201', '20230228'), self.date_converter.comparison_dates('20240201', '20240229', 'last_year'))
