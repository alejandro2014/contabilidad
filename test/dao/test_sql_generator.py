import unittest

from src.dao.SqlGenerator import SqlGenerator

class SqlGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.sql_generator = SqlGenerator()

    def test_select_pending_expenses_nofilter_nosortby(self):
        expected_sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL)"
        sql = self.sql_generator.select_pending_expenses(filter=None, sort_by=None)
        
        self.assertEqual(expected_sql, sql)

    def test_select_classified_expenses_nofilter_nosortby(self):
        expected_sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NOT NULL)"
        sql = self.sql_generator.select_classified_expenses(filter=None, sort_by=None)
        
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

    def test__delete_pending_expense(self):
        expected_sql = "DELETE FROM expenses WHERE date = '20221006' AND title = 'Alquiler' AND amount = 100.87"

        expense = {
            'date': '20221006',
            'title': 'Alquiler',
            'amount': 100.87
        }

        sql = self.sql_generator.delete_pending_expense(expense)

        self.assertEqual(expected_sql, sql)

    def test__select_classified_expenses_count(self):
        expected_sql = "SELECT count(*) FROM expenses WHERE (category IS NOT NULL)"

        sql = self.sql_generator.select_classified_expenses_count()

        self.assertEqual(expected_sql, sql)

    def test__select_classified_expenses_by_type(self):
        expected_sql = "SELECT type, sum(amount) AS sum FROM expenses WHERE (category IS NOT NULL) GROUP BY type"

        sql = self.sql_generator.select_classified_expenses_by_type()

        self.assertEqual(expected_sql, sql)

    def test__select_classified_expenses_by_month(self):
        expected_sql = "SELECT substr(date, 0, 7) AS month, sum(amount) AS sum FROM expenses (category IS NOT NULL) GROUP BY month"

        sql = self.sql_generator.select_classified_expenses_by_month()

        self.assertEqual(expected_sql, sql)

    def test__select_classified_expenses_by_type_and_month(self):
        expected_sql = "SELECT type, substr(date, 0, 7) AS month, sum(quantity) AS sum FROM expenses (category IS NOT NULL) group by type, month"

        sql = self.sql_generator.select_classified_expenses_by_type_and_month()

        self.assertEqual(expected_sql, sql)

    def test__select_pending_expenses_count(self):
        expected_sql = "SELECT count(*) FROM expenses WHERE (category IS NULL)"

        sql = self.sql_generator.select_pending_expenses_count()

        self.assertEqual(expected_sql, sql)

    def test__select_expense_types_full(self):
        expected_sql = "SELECT category, comment FROM expense_types ORDER BY category"

        sql = self.sql_generator.select_expense_types_full()

        self.assertEqual(expected_sql, sql)

    def test__delete_expense_type(self):
        expected_sql = "DELETE FROM expense_types WHERE category = 'Alquiler'"

        sql = self.sql_generator.delete_expense_type('Alquiler')

        self.assertEqual(expected_sql, sql)

    def test__select_category_name(self):
        expected_sql = "SELECT count(*) FROM expense_types WHERE category = 'Alquiler'"

        sql = self.sql_generator.select_category_name('Alquiler')

        self.assertEqual(expected_sql, sql)

    def test__insert_category(self):
        expected_sql = "INSERT INTO expense_types(category, comment) VALUES ('Alquiler', 'Alquiler del mes')"

        sql = self.sql_generator.insert_category('Alquiler', 'Alquiler del mes')

        self.assertEqual(expected_sql, sql)

    def test__update_classified_expense(self):
        expected_sql = "UPDATE expenses set category = 'Alquiler' WHERE id = '73efcadc-32f7-4fb6-9ac9-5afd6a572f49'"

        sql = self.sql_generator.update_classified_expense('73efcadc-32f7-4fb6-9ac9-5afd6a572f49', 'Alquiler')

        self.assertEqual(expected_sql, sql)