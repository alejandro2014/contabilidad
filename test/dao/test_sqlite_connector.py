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

        self.connector = SqliteConnector(self.db_path)

    def tearDown(self):
        self.connector.close()
        self.directory.cleanup()

    def test__new_database__tables_and_initial_rules(self):
        self.connector.select('SELECT 1')

        self.assertEqual({ 'expenses', 'expense_types', 'expense_tags', 'rules' }, set(self.table_names()))

        with open('src/config/db/initial-rules.json', encoding='utf-8') as rules_file:
            initial_rules = json.load(rules_file)

        rules = self.connector.select('SELECT priority, rule, category FROM rules ORDER BY priority')

        # The first rule of the file has the highest priority
        self.assertEqual(len(initial_rules), len(rules))
        self.assertEqual((1, initial_rules[0]['rule'], initial_rules[0]['category']), rules[0])

        # Their types are created too, as the foreign keys need them
        self.assertEqual([ ('Nómina', 1) ], self.connector.select("SELECT category, income FROM expense_types WHERE category = 'Nómina'"))

    def test__new_database__last_version(self):
        self.connector.select('SELECT 1')

        self.assertEqual(self.connector.get_migrations()[-1][0], self.connector.select('PRAGMA user_version')[0][0])
        self.assertEqual([ (1,) ], self.connector.select('PRAGMA foreign_keys'))

    def test__single_connection(self):
        conn = self.connector.connection()

        self.connector.select('SELECT 1')
        self.connector.execute_sql("INSERT INTO expense_types (category) VALUES ('Viajes')")

        self.assertIs(conn, self.connector.connection())

    def test__close__opened_again_on_next_use(self):
        self.connector.execute_sql("INSERT INTO expense_types (category) VALUES ('Viajes')")
        self.connector.close()

        self.assertEqual([ ('Viajes',) ], self.connector.select("SELECT category FROM expense_types WHERE category = 'Viajes'"))

    def test__shared__same_connector(self):
        self.assertIs(SqliteConnector.shared(), SqliteConnector.shared())

    def test__amounts_in_cents__exact_sums(self):
        self.connector.execute_transaction([
            "INSERT INTO expenses (id, date, title, amount) VALUES ('1', '20260105', 'A', 10), ('2', '20260106', 'B', 20)"
        ])

        self.assertEqual(0.3, self.connector.select('SELECT sum(amount) / 100.0 FROM expenses')[0][0])

    def test__foreign_keys__type_renamed_in_expenses_and_rules(self):
        self.insert_type_with_expense_and_rule()

        self.connector.execute_sql("UPDATE expense_types SET category = 'Super' WHERE category = 'Mascotas'")

        self.assertEqual([ ('Super',) ], self.connector.select("SELECT category FROM expenses"))
        self.assertEqual([ ('Super',) ], self.connector.select("SELECT category FROM rules"))

    def test__foreign_keys__type_deleted_expenses_pending_and_rules_deleted(self):
        self.insert_type_with_expense_and_rule()

        self.connector.execute_sql("DELETE FROM expense_types WHERE category = 'Mascotas'")

        self.assertEqual([ (None,) ], self.connector.select("SELECT category FROM expenses"))
        self.assertEqual([], self.connector.select("SELECT category FROM rules"))

    def test__foreign_keys__unknown_type_not_accepted(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.connector.execute_sql("INSERT INTO expenses (id, date, title, amount, category) VALUES ('1', '20260105', 'A', -100, 'Desconocido')")

    def test__indexes_used_by_the_dashboard_queries(self):
        self.connector.select('SELECT 1')
        plan = self.connector.select("EXPLAIN QUERY PLAN SELECT sum(amount) FROM expenses WHERE category = 'Mascotas' AND date BETWEEN '20260101' AND '20260131'")

        self.assertIn('expenses_category_date', ' '.join(str(row) for row in plan))

    def test__execute_sql_and_select(self):
        self.connector.execute_sql("INSERT INTO expense_types (category) VALUES ('Mascotas')")

        self.assertEqual([ ('Mascotas', 0, 0) ], self.connector.select("SELECT category, income, not_computed FROM expense_types WHERE category = 'Mascotas'"))

    def test__params__quotes_in_the_values(self):
        self.connector.execute_sql(("INSERT INTO expense_types (category, comment) VALUES (?, ?)", ("O'Hara", "it's")))

        self.assertEqual([ ("O'Hara", "it's") ], self.connector.select(("SELECT category, comment FROM expense_types WHERE category = ?", ("O'Hara",))))

    def test__execute_transaction__nothing_saved_when_one_fails(self):
        self.connector.execute_sql("INSERT INTO expense_types (category) VALUES ('Mascotas')")

        with self.assertRaises(sqlite3.IntegrityError):
            self.connector.execute_transaction([
                "INSERT INTO expense_types (category) VALUES ('Viajes')",
                "INSERT INTO expense_types (category) VALUES ('Mascotas')"
            ])

        self.assertEqual([ ('Mascotas',) ], self.connector.select("SELECT category FROM expense_types WHERE category IN ('Mascotas', 'Viajes')"))

    def test__execute_many__returns_the_rows_changed(self):
        sql = "INSERT OR IGNORE INTO expense_types (category) VALUES (?)"

        self.assertEqual(2, self.connector.execute_many(sql, [ ('Mascotas',), ('Viajes',), ('Mascotas',) ]))

    def test__execute_many__nothing_saved_when_one_fails(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.connector.execute_many("INSERT INTO expense_types (category) VALUES (?)", [ ('Mascotas',), (None,) ])

        self.assertEqual(0, self.connector.select("SELECT count(*) FROM expense_types WHERE category = 'Mascotas'")[0][0])

    def test__backup__copy_of_the_database(self):
        self.connector.execute_sql("INSERT INTO expense_types (category) VALUES ('Mascotas')")

        self.connector.backup()

        backups = os.listdir(self.connector.backups_folder())
        self.assertEqual(1, len(backups))
        self.assertRegex(backups[0], r'^test-\d{8}-\d{6}\.db$')

        conn = sqlite3.connect(os.path.join(self.connector.backups_folder(), backups[0]))
        self.assertEqual([ ('Mascotas',) ], conn.execute("SELECT category FROM expense_types WHERE category = 'Mascotas'").fetchall())
        conn.close()

    def test__backup__no_database_no_backup(self):
        self.connector.backup()

        self.assertFalse(os.path.exists(self.connector.backups_folder()))

    def test__backup__only_the_last_ones_are_kept(self):
        self.connector.select('SELECT 1')
        folder = self.connector.backups_folder()
        os.makedirs(folder)

        for day in range(1, 13):
            open(os.path.join(folder, f'test-202601{day:02d}-120000.db'), 'w').close()

        self.connector.backup()

        backups = sorted(os.listdir(folder))
        self.assertEqual(SqliteConnector.BACKUPS_NO, len(backups))
        self.assertEqual('test-20260104-120000.db', backups[0])

    def test__old_database__backup_before_the_migration(self):
        self.create_old_database("CREATE TABLE expense_types (category VARCHAR NOT NULL PRIMARY KEY, comment VARCHAR NULL)")

        self.connector.select('SELECT 1')

        backups = os.listdir(self.connector.backups_folder())
        self.assertEqual(1, len(backups))

        # The copy is the database as it was before the migrations
        conn = sqlite3.connect(os.path.join(self.connector.backups_folder(), backups[0]))
        columns = [ c[1] for c in conn.execute('PRAGMA table_info(expense_types)').fetchall() ]
        conn.close()

        self.assertEqual([ 'category', 'comment' ], columns)

    def test__new_database__no_backup(self):
        self.connector.select('SELECT 1')

        self.assertFalse(os.path.exists(self.connector.backups_folder()))

    def test__old_database__positive_column_renamed_to_income(self):
        self.create_old_database("CREATE TABLE expense_types (category VARCHAR NOT NULL PRIMARY KEY, comment VARCHAR NULL, positive BOOLEAN DEFAULT FALSE)")
        self.insert_old_expense_types([ 'Nómina', 'Otros ingresos', 'Mascotas' ])

        rows = self.connector.select("SELECT category, income, not_computed FROM expense_types WHERE category IN ('Mascotas', 'Nómina', 'Otros ingresos') ORDER BY category")

        self.assertEqual([ ('Mascotas', 0, 0), ('Nómina', 1, 0), ('Otros ingresos', 1, 0) ], rows)

    def test__old_database__income_column_added(self):
        self.create_old_database("CREATE TABLE expense_types (category VARCHAR NOT NULL PRIMARY KEY, comment VARCHAR NULL)")
        self.insert_old_expense_types([ 'Nómina', 'Mascotas' ])

        rows = self.connector.select("SELECT category, income FROM expense_types WHERE category IN ('Mascotas', 'Nómina') ORDER BY category")

        self.assertEqual([ ('Mascotas', 0), ('Nómina', 1) ], rows)

    def test__old_database__rules_table_added_with_initial_rules(self):
        self.create_old_database("CREATE TABLE expense_types (category VARCHAR NOT NULL PRIMARY KEY, comment VARCHAR NULL, income BOOLEAN DEFAULT FALSE, not_computed BOOLEAN DEFAULT FALSE)")

        count = self.connector.select('SELECT count(*) FROM rules')[0][0]

        self.assertGreater(count, 0)

    def test__old_database__amounts_to_cents_and_unused_columns_dropped(self):
        self.create_old_database("CREATE TABLE expense_types (category VARCHAR NOT NULL PRIMARY KEY, comment VARCHAR NULL, income BOOLEAN DEFAULT FALSE, not_computed BOOLEAN DEFAULT FALSE)")
        conn = sqlite3.connect(self.db_path)

        with conn:
            conn.execute("INSERT INTO expenses (id, date, title, amount, category) VALUES ('1', '20260105', 'A', -937.58, 'Sin tipo'), ('2', '20260106', 'B', 0.1, NULL)")

        conn.close()

        self.assertEqual([ ('1', -93758, 'Sin tipo'), ('2', 10, None) ], self.connector.select('SELECT id, amount, category FROM expenses ORDER BY id'))
        self.assertEqual([ 'id', 'date', 'title', 'amount', 'category', 'category_src', 'subcategory_src', 'balance', 'note' ], [ c[1] for c in self.connector.select('PRAGMA table_info(expenses)') ])

        # The type missing in expense_types is created, so the expense keeps it
        self.assertEqual(1, self.connector.select("SELECT count(*) FROM expense_types WHERE category = 'Sin tipo'")[0][0])

    def test__migrations_only_once(self):
        self.connector.select('SELECT 1')
        rules_count = self.connector.select('SELECT count(*) FROM rules')[0][0]
        self.connector.close()

        # Every connection checks the version, but the migrations and the initial rules don't run twice
        self.connector.select('SELECT 1')

        self.assertEqual(rules_count, self.connector.select('SELECT count(*) FROM rules')[0][0])

    def test__failed_migration__nothing_changed(self):
        self.create_old_database("CREATE TABLE expense_types (category VARCHAR NOT NULL PRIMARY KEY, comment VARCHAR NULL, income BOOLEAN DEFAULT FALSE, not_computed BOOLEAN DEFAULT FALSE)")
        conn = sqlite3.connect(self.db_path)

        with conn:
            # Two rows that are the same movement once the amount is in cents break the new primary key
            conn.execute("INSERT INTO expenses (id, date, title, amount) VALUES ('1', '20260105', 'A', -1.001), ('2', '20260105', 'A', -1.002)")

        conn.close()

        with self.assertRaises(sqlite3.IntegrityError):
            self.connector.select('SELECT 1')

        conn = sqlite3.connect(self.db_path)
        version = conn.execute('PRAGMA user_version').fetchone()[0]
        amounts = conn.execute('SELECT amount FROM expenses ORDER BY id').fetchall()
        conn.close()

        # The migrations before the one that failed are kept
        self.assertEqual(1, version)
        self.assertEqual([ (-1.001,), (-1.002,) ], amounts)

    def insert_type_with_expense_and_rule(self):
        self.connector.execute_transaction([
            "DELETE FROM rules",
            "INSERT INTO expense_types (category) VALUES ('Mascotas')",
            "INSERT INTO expenses (id, date, title, amount, category) VALUES ('1', '20260105', 'MERCADONA', -3000, 'Mascotas')",
            "INSERT INTO rules (priority, rule, category) VALUES (1, 'MERCADONA', 'Mascotas')"
        ])

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
