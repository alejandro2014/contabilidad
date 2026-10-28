import json
import sqlite3
from sqlite3 import Error

class SqliteConnector:
    def __init__(self):
        self.db = "src/config/db/accountancy.db"

    def select(self, sql):
        print(f'[SQL] {sql}')
        conn = self.create_connection()
        rows = []

        # "with" only commits, the connection has to be closed by hand
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(sql)
                rows = cur.fetchall()
        finally:
            conn.close()

        return rows

    def execute_sql(self, sql):
        print(sql)
        conn = self.create_connection()

        try:
            with conn:
                cur = conn.cursor()
                cur.execute(sql)
        finally:
            conn.close()

    def create_connection(self):
        conn = None

        try:
            conn = sqlite3.connect(self.db)
            self.create_tables_if_needed(conn)
        except Error as e:
            print(e)

        return conn

    def create_tables_if_needed(self, conn):
        # sqlite3.connect creates an empty file when the database doesn't exist yet
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'expenses'").fetchall()

        if len(tables) > 0:
            self.add_income_column_if_needed(conn)
            self.add_not_computed_column_if_needed(conn)
            self.add_rules_table_if_needed(conn)
            return

        print(f'[INFO] Creating the tables in {self.db}')

        with open("src/config/db/create_database.sql") as sql_file:
            conn.executescript(sql_file.read())

        self.insert_initial_rules(conn)

    def get_expense_types_columns(self, conn):
        return [ c[1] for c in conn.execute("PRAGMA table_info(expense_types)").fetchall() ]

    def add_income_column_if_needed(self, conn):
        # Databases created before the income flag have an unused "positive" column instead
        columns = self.get_expense_types_columns(conn)

        if 'income' in columns:
            return

        print(f'[INFO] Adding the income column to expense_types in {self.db}')

        with conn:
            if 'positive' in columns:
                conn.execute("ALTER TABLE expense_types RENAME COLUMN positive TO income")
            else:
                conn.execute("ALTER TABLE expense_types ADD COLUMN income BOOLEAN DEFAULT FALSE")

            # These categories were the incomes before the flag existed
            conn.execute("UPDATE expense_types SET income = TRUE WHERE category IN ('Nómina', 'Otros ingresos')")

    def add_not_computed_column_if_needed(self, conn):
        if 'not_computed' in self.get_expense_types_columns(conn):
            return

        print(f'[INFO] Adding the not_computed column to expense_types in {self.db}')

        with conn:
            conn.execute("ALTER TABLE expense_types ADD COLUMN not_computed BOOLEAN DEFAULT FALSE")

    def add_rules_table_if_needed(self, conn):
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'rules'").fetchall()

        if len(tables) > 0:
            return

        print(f'[INFO] Adding the rules table to {self.db}')

        with conn:
            conn.execute("CREATE TABLE rules (priority INTEGER NOT NULL PRIMARY KEY, rule VARCHAR NOT NULL, category VARCHAR NOT NULL)")

        self.insert_initial_rules(conn)

    def insert_initial_rules(self, conn):
        # Rules composed from the expenses already classified. The first one in the list has the highest priority
        with open("src/config/db/initial-rules.json", encoding="utf-8") as rules_file:
            rules = json.load(rules_file)

        with conn:
            conn.executemany(
                "INSERT INTO rules (priority, rule, category) VALUES (?, ?, ?)",
                [ (priority, r['rule'], r['category']) for priority, r in enumerate(rules, 1) ]
            )
