import unittest

from src.dao.SqlGenerator import SqlGenerator

from src.model.expense import Expense

class SqlGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.sql_generator = SqlGenerator()

    def test__insert_expenses(self):
        expense = Expense(
            id = 'id',
            date = 'date',
            category_src = 'category_src',
            subcategory_src = 'subcategory_src',
            title = 'title',
            amount = 10.11,
            category = 'category',
            subcategory = 'subcategory',
            category_suggested = 'category_suggested',
            subcategory_suggested = 'subcategory_suggested'
        )

        expected_sql = "INSERT OR IGNORE INTO expenses (id, date, category_src, subcategory_src, title, amount, category, subcategory, category_suggested, subcategory_suggested) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        expected_values = ('id', 'date', 'category_src', 'subcategory_src', 'title', 10.11, 'category', 'subcategory', 'category_suggested', 'subcategory_suggested')

        self.assertEqual(expected_sql, self.sql_generator.insert_expenses())
        self.assertEqual(expected_values, self.sql_generator.expense_values(expense))

    def test__expense_values__missing_values_are_null(self):
        values = self.sql_generator.expense_values(Expense(id = 'id', date = '20260105', title = "O'Hara", amount = -3.5))

        self.assertEqual(('id', '20260105', None, None, "O'Hara", -3.5, None, None, None, None), values)

    def test_select_pending_expenses_nofilter_nosortby(self):
        expected_sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL)"
        sql = self.sql_generator.select_pending_expenses(filter=None, sort_by=None)
        
        self.assertEqual((expected_sql, ()), sql)

    def test_select_classified_expenses_nofilter_nosortby(self):
        expected_sql = "SELECT id, date, title, amount, category FROM expenses WHERE (category IS NOT NULL)"
        sql = self.sql_generator.select_classified_expenses(filter=None, sort_by=None)
        
        self.assertEqual((expected_sql, ()), sql)

    def test_select_pending_expenses_filterfrom_nosortby(self):
        expected_sql = ("SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (date BETWEEN ? AND ?)", ('20221006', '20221106'))

        filter = {
            'date': {
                'from': '20221006',
                'to': '20221106'
            }
        }

        sql = self.sql_generator.select_pending_expenses(filter=filter, sort_by=None)
        
        self.assertEqual(expected_sql, sql)

    def test_select_pending_expenses_filterfromandto_nosortby(self):
        expected_sql = ("SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (date BETWEEN ? AND ?) AND (title LIKE ?)", ('20221006', '20221106', '%Search%'))

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
        expected_sql = ("SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (title LIKE ?)", ('%Search%',))

        filter = {
            'search_value': 'Search'
        }

        sql = self.sql_generator.select_pending_expenses(filter=filter, sort_by=None)
        
        self.assertEqual(expected_sql, sql)

    def test_select_pending_expenses_filterfromandtoandsearch_sortby(self):
        expected_sql = ("SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (date BETWEEN ? AND ?) AND (title LIKE ?) ORDER BY title ASC", ('20221006', '20221106', '%Search%'))

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
        
        self.assertEqual((expected_sql, ()), sql)

    def test_select_pending_expenses_sortby_table_field(self):
        # The fields of the table configs are translated to their columns
        sql, _ = self.sql_generator.select_pending_expenses(filter=None, sort_by='quantity')

        self.assertTrue(sql.endswith(' ORDER BY amount ASC'))

    def test_select_pending_expenses_sortby_unknown_column(self):
        with self.assertRaises(ValueError):
            self.sql_generator.select_pending_expenses(filter=None, sort_by='amount; DROP TABLE expenses')

    def test_select_classified_expenses_filteramountandcategory(self):
        expected_sql = ("SELECT id, date, title, amount, category FROM expenses WHERE (category IS NOT NULL) AND (ROUND(ABS(amount), 2) >= ?) AND (ROUND(ABS(amount), 2) <= ?) AND (category = ?)", (10.5, 20.0, 'Alquiler'))

        filter = {
            'amount': {
                'from': 10.5,
                'to': 20
            },
            'category': 'Alquiler'
        }

        sql = self.sql_generator.select_classified_expenses(filter=filter, sort_by=None)

        self.assertEqual(expected_sql, sql)

    def test_select_pending_expenses_filteronlyamountfrom(self):
        expected_sql = ("SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (ROUND(ABS(amount), 2) >= ?)", (45.2,))

        filter = {
            'amount': {
                'from': 45.2,
                'to': None
            },
            'category': None
        }

        sql = self.sql_generator.select_pending_expenses(filter=filter, sort_by=None)

        self.assertEqual(expected_sql, sql)

    def test_select_pending_expenses_filtersearch_quotes_as_parameters(self):
        expected_sql = ("SELECT id, date, title, amount FROM expenses WHERE (category IS NULL) AND (title LIKE ?)", ("%L'Oreal%",))

        sql = self.sql_generator.select_pending_expenses(filter={ 'search_value': "L'Oreal" }, sort_by=None)

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

    def test__select_classified_expenses_count(self):
        expected_sql = "SELECT count(*) FROM expenses WHERE (category IS NOT NULL)"

        sql = self.sql_generator.select_classified_expenses_count()

        self.assertEqual(expected_sql, sql)

    def test__select_classified_expenses_by_type(self):
        expected_sql = "SELECT category, sum(amount) AS sum FROM expenses WHERE (category IS NOT NULL) GROUP BY category"

        sql = self.sql_generator.select_classified_expenses_by_type()

        self.assertEqual(expected_sql, sql)

    def test__select_classified_expenses_by_month(self):
        expected_sql = "SELECT substr(date, 0, 7) AS month, sum(amount) AS sum FROM expenses WHERE (category IS NOT NULL) AND category NOT IN (SELECT category FROM expense_types WHERE income OR not_computed) GROUP BY month"

        sql = self.sql_generator.select_classified_expenses_by_month()

        self.assertEqual(expected_sql, sql)

    def test__select_classified_expenses_by_type_and_month(self):
        expected_sql = "SELECT category, substr(date, 0, 7) AS month, sum(amount) AS sum FROM expenses WHERE (category IS NOT NULL) GROUP BY category, month"

        sql = self.sql_generator.select_classified_expenses_by_type_and_month()

        self.assertEqual(expected_sql, sql)

    def test__select_pending_expenses_count(self):
        expected_sql = "SELECT count(*) FROM expenses WHERE (category IS NULL)"

        sql = self.sql_generator.select_pending_expenses_count()

        self.assertEqual(expected_sql, sql)

    def test__select_expenses_date_range(self):
        expected_sql = "SELECT (category IS NOT NULL) AS classified, MIN(date), MAX(date), count(*) FROM expenses GROUP BY classified"

        sql = self.sql_generator.select_expenses_date_range()

        self.assertEqual(expected_sql, sql)

    def test__select_not_computed_categories(self):
        expected_sql = "SELECT category FROM expense_types WHERE income OR not_computed"

        sql = self.sql_generator.select_not_computed_categories()

        self.assertEqual(expected_sql, sql)

    def test__select_expense_types_full(self):
        expected_sql = "SELECT category, comment, income, not_computed FROM expense_types ORDER BY category"

        sql = self.sql_generator.select_expense_types_full()

        self.assertEqual(expected_sql, sql)

    def test__delete_expense_type(self):
        expected_sql = ("DELETE FROM expense_types WHERE category = ?", ('Alquiler',))

        sql = self.sql_generator.delete_expense_type('Alquiler')

        self.assertEqual(expected_sql, sql)

    def test__select_category_name(self):
        expected_sql = ("SELECT count(*) FROM expense_types WHERE category = ?", ('Alquiler',))

        sql = self.sql_generator.select_category_name('Alquiler')

        self.assertEqual(expected_sql, sql)

    def test__insert_category(self):
        expected_sql = ("INSERT INTO expense_types(category, comment, income, not_computed) VALUES (?, ?, ?, ?)", ('Alquiler', 'Alquiler del mes', False, False))

        sql = self.sql_generator.insert_category('Alquiler', 'Alquiler del mes')

        self.assertEqual(expected_sql, sql)

    def test__insert_category__income(self):
        expected_sql = ("INSERT INTO expense_types(category, comment, income, not_computed) VALUES (?, ?, ?, ?)", ('Nómina', 'Sueldo', True, False))

        sql = self.sql_generator.insert_category('Nómina', 'Sueldo', True)

        self.assertEqual(expected_sql, sql)

    def test__insert_category__not_computed(self):
        expected_sql = ("INSERT INTO expense_types(category, comment, income, not_computed) VALUES (?, ?, ?, ?)", ('Cuenta ahorro', 'Traspasos', False, True))

        sql = self.sql_generator.insert_category('Cuenta ahorro', 'Traspasos', not_computed=True)

        self.assertEqual(expected_sql, sql)

    def test__update_expense_type_flag__income(self):
        expected_sql = ("UPDATE expense_types SET income = ? WHERE category = ?", (True, 'Nómina'))

        sql = self.sql_generator.update_expense_type_flag('Nómina', 'income', True)

        self.assertEqual(expected_sql, sql)

    def test__update_expense_type_flag__not_computed(self):
        expected_sql = ("UPDATE expense_types SET not_computed = ? WHERE category = ?", (False, 'Cuenta ahorro'))

        sql = self.sql_generator.update_expense_type_flag('Cuenta ahorro', 'not_computed', False)

        self.assertEqual(expected_sql, sql)

    def test__update_expense_type_flag__only_the_flags(self):
        with self.assertRaises(ValueError):
            self.sql_generator.update_expense_type_flag('Comida', 'category', 'Otra')

    def test__rename_expense_type(self):
        expected_sql = ("UPDATE expense_types SET category = ? WHERE category = ?", ("O'Hara", 'Comida'))

        self.assertEqual(expected_sql, self.sql_generator.rename_expense_type('Comida', "O'Hara"))

    def test__update_expense_type_comment(self):
        expected_sql = ("UPDATE expense_types SET comment = ? WHERE category = ?", ('Supermercados', 'Comida'))

        self.assertEqual(expected_sql, self.sql_generator.update_expense_type_comment('Comida', 'Supermercados'))

    def test__move_expenses_to_type__pending_again(self):
        expected_sql = ("UPDATE expenses SET category = ? WHERE category = ?", (None, 'Comida'))

        self.assertEqual(expected_sql, self.sql_generator.move_expenses_to_type('Comida', None))

    def test__move_rules_to_type(self):
        expected_sql = ("UPDATE rules SET category = ? WHERE category = ?", ('Casa', 'Hogar'))

        self.assertEqual(expected_sql, self.sql_generator.move_rules_to_type('Hogar', 'Casa'))

    def test__delete_rules_of_type(self):
        self.assertEqual(("DELETE FROM rules WHERE category = ?", ('Hogar',)), self.sql_generator.delete_rules_of_type('Hogar'))

    def test__update_classified_expense(self):
        expected_sql = ("UPDATE expenses set category = ? WHERE id = ?", ('Alquiler', '73efcadc-32f7-4fb6-9ac9-5afd6a572f49'))

        sql = self.sql_generator.update_classified_expense('73efcadc-32f7-4fb6-9ac9-5afd6a572f49', 'Alquiler')

        self.assertEqual(expected_sql, sql)

    def test__update_unclassified_expense(self):
        expected_sql = ("UPDATE expenses set category = NULL WHERE id = ?", ('73efcadc-32f7-4fb6-9ac9-5afd6a572f49',))

        sql = self.sql_generator.update_unclassified_expense('73efcadc-32f7-4fb6-9ac9-5afd6a572f49')

        self.assertEqual(expected_sql, sql)

    def test__select_pie_chart_categories(self):
        params = {
            'date_from': '20220101',
            'date_to': '20220103',
        }

        expected_sql = "SELECT category, sum(amount) AS amnt FROM expenses WHERE category IS NOT NULL AND category NOT IN (SELECT category FROM expense_types WHERE income OR not_computed) AND date BETWEEN ? AND ? GROUP BY category ORDER BY abs(amnt) DESC", ('20220101', '20220103')

        sql = self.sql_generator.select_pie_chart_categories(params)

        self.assertEqual(expected_sql, sql)

    def test__select_bar_chart_values(self):
        params = {
            'date_from': '20220101',
            'date_to': '20220103',
        }

        expected_sql = "SELECT SUBSTR(date, 1, 6) AS d, SUM(amount) FROM expenses WHERE category IS NOT NULL AND category NOT IN (SELECT category FROM expense_types WHERE income OR not_computed) AND date BETWEEN ? AND ? GROUP BY d", ('20220101', '20220103')

        sql = self.sql_generator.select_bar_chart_values(params)

        self.assertEqual(expected_sql, sql)

    def test__select_income_chart_values(self):
        params = { 'date_from': '20220101', 'date_to': '20220103' }

        expected_sql = "SELECT SUBSTR(date, 1, 6) AS d, SUM(amount) FROM expenses WHERE category IN (SELECT category FROM expense_types WHERE income) AND date BETWEEN ? AND ? GROUP BY d", ('20220101', '20220103')

        self.assertEqual(expected_sql, self.sql_generator.select_income_chart_values(params))

    def test__select_category_month_values(self):
        params = { 'date_from': '20220101', 'date_to': '20220103' }

        expected_sql = "SELECT category, SUBSTR(date, 1, 6) AS d, SUM(amount) FROM expenses WHERE category IS NOT NULL AND category NOT IN (SELECT category FROM expense_types WHERE income OR not_computed) AND date BETWEEN ? AND ? GROUP BY category, d", ('20220101', '20220103')

        self.assertEqual(expected_sql, self.sql_generator.select_category_month_values(params))

    def test__select_top_expenses(self):
        params = { 'date_from': '20220101', 'date_to': '20220103' }

        expected_sql = "SELECT MIN(date), MAX(date), title, category, amount, count(*) FROM expenses WHERE category IS NOT NULL AND category NOT IN (SELECT category FROM expense_types WHERE income OR not_computed) AND amount < 0 AND date BETWEEN ? AND ? GROUP BY title, category, amount ORDER BY amount ASC LIMIT ?", ('20220101', '20220103', 10)

        self.assertEqual(expected_sql, self.sql_generator.select_top_expenses(params, 10))

    def test__select_pending_expenses_count_between(self):
        params = { 'date_from': '20220101', 'date_to': '20220103' }

        expected_sql = "SELECT count(*) FROM expenses WHERE (category IS NULL) AND date BETWEEN ? AND ?", ('20220101', '20220103')

        self.assertEqual(expected_sql, self.sql_generator.select_pending_expenses_count_between(params))

    def test__select_cashflow__by_bank_category(self):
        expected_sql = "SELECT (category IS NOT NULL AND category IN (SELECT category FROM expense_types WHERE income)) AS is_income, category_src AS grp, CAST(substr(date, 5, 2) AS INTEGER) AS month, sum(amount) FROM expenses WHERE date LIKE ? AND (category IS NULL OR category NOT IN (SELECT category FROM expense_types WHERE not_computed)) GROUP BY is_income, grp, month", ('2026%',)

        sql = self.sql_generator.select_cashflow('2026', 'bank')

        self.assertEqual(expected_sql, sql)

    def test__select_cashflow__by_expense_type(self):
        expected_sql = "SELECT (category IS NOT NULL AND category IN (SELECT category FROM expense_types WHERE income)) AS is_income, COALESCE(category, 'Sin clasificar') AS grp, CAST(substr(date, 5, 2) AS INTEGER) AS month, sum(amount) FROM expenses WHERE date LIKE ? AND (category IS NULL OR category NOT IN (SELECT category FROM expense_types WHERE not_computed)) GROUP BY is_income, grp, month", ('2026%',)

        sql = self.sql_generator.select_cashflow('2026', 'type')

        self.assertEqual(expected_sql, sql)

    def test__select_rules(self):
        expected_sql = "SELECT priority, rule, category FROM rules ORDER BY priority"

        sql = self.sql_generator.select_rules()

        self.assertEqual(expected_sql, sql)

    def test__insert_rule(self):
        expected_sql = ("INSERT INTO rules (priority, rule, category) VALUES ((SELECT COALESCE(MAX(priority), 0) + 1 FROM rules), ?, ?)", ('MERCADONA', 'Comida'))

        sql = self.sql_generator.insert_rule('Comida', 'MERCADONA')

        self.assertEqual(expected_sql, sql)

    def test__insert_rule__quotes_as_parameters(self):
        expected_sql = ("INSERT INTO rules (priority, rule, category) VALUES ((SELECT COALESCE(MAX(priority), 0) + 1 FROM rules), ?, ?)", ("McDonald's", 'Salir'))

        sql = self.sql_generator.insert_rule('Salir', "McDonald's")

        self.assertEqual(expected_sql, sql)

    def test__delete_rule_by_priority(self):
        expected_sql = ("DELETE FROM rules WHERE priority = ?", (3,))

        sql = self.sql_generator.delete_rule_by_priority(3)

        self.assertEqual(expected_sql, sql)

    def test__update_rule(self):
        expected_sql = ("UPDATE rules SET rule = ?, category = ? WHERE priority = ?", ('LIDL', 'Comida', 3))

        sql = self.sql_generator.update_rule(3, 'LIDL', 'Comida')

        self.assertEqual(expected_sql, sql)

    def test__update_rule_priority(self):
        expected_sql = ("UPDATE rules SET priority = ? WHERE priority = ?", (4, 3))

        sql = self.sql_generator.update_rule_priority(3, 4)

        self.assertEqual(expected_sql, sql)

    def test__select_category_titles__quotes_as_parameters(self):
        expected_sql = ("SELECT title, sum(amount) FROM expenses WHERE category = ? AND date BETWEEN ? AND ? GROUP BY title", ("Hogar's", '20260101', '20260131'))

        sql = self.sql_generator.select_category_titles({ 'date_from': '20260101', 'date_to': '20260131' }, "Hogar's")

        self.assertEqual(expected_sql, sql)
