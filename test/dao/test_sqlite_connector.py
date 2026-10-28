import json
import os
import sqlite3
import tempfile
import unittest

from src.dao.SqliteConnector import SqliteConnector

class SqliteConnectorTestCase(unittest.TestCase):
    def setUp(self):
        # Every test works on its own database, never on the real one
        self.directory = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.directory.name, 'test.db')

        self.connector = SqliteConnector()
        self.connector.db = self.db_path

    def tearDown(self):
        self.directory.cleanup()

    def test__new_database__tables_and_initial_rules(self):
        self.connector.select('SELECT 1')

        self.assertEqual({ 'expenses', 'expense_types', 'rules' }, set(self.table_names()))

        with open('src/config/db/initial-rules.json', encoding='utf-8') as rules_file:
            initial_rules = json.load(rules_file)

        rules = self.connector.select('SELECT priority, rule, category FROM rules ORDER BY priority')

        # The first rule of the file has the highest priority
        self.assertEqual(len(initial_rules), len(rules))
        self.assertEqual((1, initial_rules[0]['rule'], initial_rules[0]['category']), rules[0])

    def test__execute_sql_and_select(self):
        self.connector.execute_sql("INSERT INTO expense_types (category) VALUES ('Comida')")

        self.assertEqual([ ('Comida', 0, 0) ], self.connector.select('SELECT category, income, not_computed FROM expense_types'))

    def test__old_database__positive_column_renamed_to_income(self):
        self.create_old_database("CREATE TABLE expense_types (category VARCHAR NOT NULL PRIMARY KEY, comment VARCHAR NULL, positive BOOLEAN DEFAULT FALSE)")
        self.insert_old_expense_types([ 'Nómina', 'Otros ingresos', 'Comida' ])

        rows = self.connector.select('SELECT category, income, not_computed FROM expense_types ORDER BY category')

        self.assertEqual([ ('Comida', 0, 0), ('Nómina', 1, 0), ('Otros ingresos', 1, 0) ], rows)

    def test__old_database__income_column_added(self):
        self.create_old_database("CREATE TABLE expense_types (category VARCHAR NOT NULL PRIMARY KEY, comment VARCHAR NULL)")
        self.insert_old_expense_types([ 'Nómina', 'Comida' ])

        rows = self.connector.select('SELECT category, income FROM expense_types ORDER BY category')

        self.assertEqual([ ('Comida', 0), ('Nómina', 1) ], rows)

    def test__old_database__rules_table_added_with_initial_rules(self):
        self.create_old_database("CREATE TABLE expense_types (category VARCHAR NOT NULL PRIMARY KEY, comment VARCHAR NULL, income BOOLEAN DEFAULT FALSE, not_computed BOOLEAN DEFAULT FALSE)")

        count = self.connector.select('SELECT count(*) FROM rules')[0][0]

        self.assertGreater(count, 0)

    def test__migrations_only_once(self):
        self.connector.select('SELECT 1')
        rules_count = self.connector.select('SELECT count(*) FROM rules')[0][0]

        # Every connection checks the migrations again, but the initial rules are not inserted twice
        self.connector.select('SELECT 1')

        self.assertEqual(rules_count, self.connector.select('SELECT count(*) FROM rules')[0][0])

    def create_old_database(self, expense_types_sql):
        conn = sqlite3.connect(self.db_path)

        with conn:
            conn.execute("CREATE TABLE expenses (id CHAR(36) NOT NULL, date CHAR(8) NOT NULL, title STRING NOT NULL, amount FLOAT NOT NULL, category STRING NULL)")
            conn.execute(expense_types_sql)

        conn.close()

    def insert_old_expense_types(self, categories):
        # Inserted before the connector opens the database, so the migrations run on them
        conn = sqlite3.connect(self.db_path)

        with conn:
            conn.executemany("INSERT INTO expense_types (category) VALUES (?)", [ (c,) for c in categories ])

        conn.close()

    def table_names(self):
        return [ t[0] for t in self.connector.select("SELECT name FROM sqlite_master WHERE type = 'table'") ]
