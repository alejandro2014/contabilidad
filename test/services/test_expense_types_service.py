import os
import tempfile
import unittest

from src.dao.SqliteConnector import SqliteConnector
from src.services.ExpenseTypesService import ExpenseTypesService

class ExpenseTypesServiceTestCase(unittest.TestCase):
    def setUp(self):
        # A temporary database, with a type used by some expenses and rules
        self.directory = tempfile.TemporaryDirectory()

        self.service = ExpenseTypesService()
        self.service.db = SqliteConnector()
        self.service.db.db = os.path.join(self.directory.name, 'test.db')

        self.service.db.execute_transaction([
            "DELETE FROM rules",
            "INSERT INTO expense_types (category) VALUES ('Comida'), ('Casa')",
            "INSERT INTO expenses (id, date, title, amount, category) VALUES ('1', '20260105', 'MERCADONA', -30.0, 'Comida'), ('2', '20260106', 'LIDL', -10.0, 'Comida'), ('3', '20260107', 'IKEA', -99.0, 'Casa')",
            "INSERT INTO rules (priority, rule, category) VALUES (1, 'MERCADONA', 'Comida'), (2, 'IKEA', 'Casa')"
        ])

    def tearDown(self):
        self.directory.cleanup()

    def test__rename_category__expenses_and_rules_too(self):
        self.service.rename_category('Comida', "Super's")

        self.assertEqual([ 'Casa', "Super's" ], self.service.get_categories_simple())
        self.assertEqual([ ('1', "Super's"), ('2', "Super's"), ('3', 'Casa') ], self.select("SELECT id, category FROM expenses ORDER BY id"))
        self.assertEqual([ ('MERCADONA', "Super's"), ('IKEA', 'Casa') ], self.select("SELECT rule, category FROM rules ORDER BY priority"))

    def test__rename_category__to_an_existing_one_changes_nothing(self):
        with self.assertRaises(Exception):
            self.service.rename_category('Comida', 'Casa')

        self.assertEqual([ 'Casa', 'Comida' ], self.service.get_categories_simple())
        self.assertEqual(2, self.select("SELECT count(*) FROM expenses WHERE category = 'Comida'")[0][0])

    def test__get_category_usage(self):
        self.assertEqual((2, 1), self.service.get_category_usage('Comida'))
        self.assertEqual((0, 0), self.service.get_category_usage('Otra'))

    def test__remove_category__expenses_pending_again(self):
        self.service.remove_category('Comida')

        self.assertEqual([ 'Casa' ], self.service.get_categories_simple())
        self.assertEqual([ ('1', None), ('2', None), ('3', 'Casa') ], self.select("SELECT id, category FROM expenses ORDER BY id"))
        self.assertEqual([ ('IKEA', 'Casa') ], self.select("SELECT rule, category FROM rules ORDER BY priority"))

    def test__remove_category__moved_to_another_type(self):
        self.service.remove_category('Comida', 'Casa')

        self.assertEqual([ 'Casa' ], self.service.get_categories_simple())
        self.assertEqual(3, self.select("SELECT count(*) FROM expenses WHERE category = 'Casa'")[0][0])
        self.assertEqual([ ('MERCADONA', 'Casa'), ('IKEA', 'Casa') ], self.select("SELECT rule, category FROM rules ORDER BY priority"))

    def test__update_comment_and_flag__quotes(self):
        self.service.update_comment('Comida', "Super's y mercados")
        self.service.update_expense_type_flag('Comida', 'not_computed', True)

        comida = [ t for t in self.service.select_expense_types_full() if t['category'] == 'Comida' ][0]

        self.assertEqual("Super's y mercados", comida['comment'])
        self.assertTrue(comida['not_computed'])

    def select(self, sql):
        return self.service.db.select(sql)
