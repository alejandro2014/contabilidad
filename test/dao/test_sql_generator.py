import unittest

from src.dao.SqlGenerator import SqlGenerator

class SqlGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.sql_generator = SqlGenerator()

    def test_select_pending_expenses_nofilter_nosortby(self):
        expected_sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL)"
        sql = self.sql_generator.select_pending_expenses(filter=None, sort_by=None)
        
        self.assertEqual(expected_sql, sql)

    def test_select_pending_expenses_filterfrom_nosortby(self):
        expected_sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (date BETWEEN '20221006' AND '20221106')"

        filter = {
            'date': {
                'from': '20221006',
                'to': '20221106'
            }
        }

        sql = self.sql_generator.select_pending_expenses(filter=filter, sort_by=None)
        
        self.assertEqual(expected_sql, sql)

    def test_select_pending_expenses_filterfromandto_nosortby(self):
        expected_sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (date BETWEEN '20221006' AND '20221106') AND (title LIKE '%Search%')"

        filter = {
            'date': {
                'from': '20221006',
                'to': '20221106'
            },
            'search_value': 'Search'
        }

        sql = self.sql_generator.select_pending_expenses(filter=filter, sort_by=None)
        
        self.assertEqual(expected_sql, sql)

    def test_select_pending_expenses_filtersearch_nosortby(self):
        expected_sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (title LIKE '%Search%')"

        filter = {
            'search_value': 'Search'
        }

        sql = self.sql_generator.select_pending_expenses(filter=filter, sort_by=None)
        
        self.assertEqual(expected_sql, sql)

    def test_select_pending_expenses_filterfromandtoandsearch_sortby(self):
        expected_sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (date BETWEEN '20221006' AND '20221106') AND (title LIKE '%Search%') ORDER BY title ASC"

        filter = {
            'date': {
                'from': '20221006',
                'to': '20221106'
            },
            'search_value': 'Search'
        }

        sql = self.sql_generator.select_pending_expenses(filter=filter, sort_by='title')
        
        self.assertEqual(expected_sql, sql)
    
    def test_select_pending_expenses_nofilter_sortbytitle(self):
        expected_sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) ORDER BY title ASC"
        sql = self.sql_generator.select_pending_expenses(filter=None, sort_by='title')
        
        self.assertEqual(expected_sql, sql)

    def test__get_filter_values__when_no_date__nofrom_noto_nosearchvalue(self):
        filter = {}

        date_from, date_to, search_value = self.sql_generator.get_filter_values(filter)

        self.assertIsNone(date_from)
        self.assertIsNone(date_to)
        self.assertIsNone(search_value)

    def test__get_filter_values__when_no_from_in_date__nofrom_noto_nosearchvalue(self):
        filter = {
            'date': {}
        }

        date_from, date_to, search_value = self.sql_generator.get_filter_values(filter)

        self.assertIsNone(date_from)
        self.assertIsNone(date_to)
        self.assertIsNone(search_value)

    def test__get_filter_values__when_from_in_date__yesfrom_noto_nosearchvalue(self):
        filter = {
            'date': {
                'from': '20221006'
            }
        }

        date_from, date_to, search_value = self.sql_generator.get_filter_values(filter)

        self.assertEqual('20221006', date_from)
        self.assertIsNone(date_to)
        self.assertIsNone(search_value)

    def test__get_filter_values__when_fromandto_in_date__yesfrom_yesto_nosearchvalue(self):
        filter = {
            'date': {
                'from': '20221006',
                'to': '20221106'
            }
        }

        date_from, date_to, search_value = self.sql_generator.get_filter_values(filter)

        self.assertEqual('20221006', date_from)
        self.assertEqual('20221106', date_to)
        self.assertIsNone(search_value)

    def test__get_filter_values__when_fromandtoandsearchvalue_in_date__yesfrom_yesto_yessearchvalue(self):
        filter = {
            'date': {
                'from': '20221006',
                'to': '20221106'
            },
            'search_value': 'Search'
        }

        date_from, date_to, search_value = self.sql_generator.get_filter_values(filter)

        self.assertEqual('20221006', date_from)
        self.assertEqual('20221106', date_to)
        self.assertEqual('Search', search_value)
