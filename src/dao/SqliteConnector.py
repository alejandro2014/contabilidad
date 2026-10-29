import datetime
import glob
import json
import os
import shutil
import sqlite3
from sqlite3 import Error

from src.logger import get_logger

logger = get_logger(__name__)

class SqliteConnector:
    # Copies of the database kept in the backups folder
    BACKUPS_NO = 10

    def __init__(self):
        self.db = "src/config/db/accountancy.db"

    def split_query(self, query):
        # A query is the sql alone, or (sql, params) when it has values
        sql, params = query if isinstance(query, tuple) else (query, ())
        logger.debug(f'{sql} {params}')

        return sql, params

    def select(self, query):
        sql, params = self.split_query(query)
        conn = self.create_connection()
        rows = []

        # "with" only commits, the connection has to be closed by hand
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                rows = cur.fetchall()
        finally:
            conn.close()

        return rows

    def execute_sql(self, query):
        self.execute_transaction([ query ])

    def execute_transaction(self, queries):
        # All the queries are committed together, or none of them when one fails
        conn = self.create_connection()

        try:
            with conn:
                for query in queries:
                    conn.execute(*self.split_query(query))
        finally:
            conn.close()

    def execute_many(self, sql, rows):
        # A single transaction for all the rows. Returns how many rows have been changed
        logger.debug(f'{sql} ({len(rows)} rows)')
        conn = self.create_connection()

        try:
            with conn:
                cur = conn.executemany(sql, rows)
                changed = cur.rowcount
        finally:
            conn.close()

        return changed

    def backups_folder(self):
        return os.path.join(os.path.dirname(self.db), 'backups')

    def backup(self):
        # Copy of the database before changing a lot of data at once (imports, schema migrations)
        if not os.path.exists(self.db) or os.path.getsize(self.db) == 0:
            return

        folder = self.backups_folder()
        os.makedirs(folder, exist_ok=True)

        name = os.path.splitext(os.path.basename(self.db))[0]
        backup_file = os.path.join(folder, f'{name}-{datetime.datetime.now():%Y%m%d-%H%M%S}.db')

        # Within the same second only the first copy is kept: it is the one from before every change
        if not os.path.exists(backup_file):
            logger.info(f'Backup of {self.db} in {backup_file}')
            shutil.copy2(self.db, backup_file)

        self.remove_old_backups(folder, name)

    def remove_old_backups(self, folder, name):
        # The names have the date, so sorted by name they are sorted by date
        backups = sorted(glob.glob(os.path.join(folder, f'{glob.escape(name)}-*.db')))

        for old_backup in backups[:-self.BACKUPS_NO]:
            os.remove(old_backup)

    def create_connection(self):
        conn = None

        try:
            conn = sqlite3.connect(self.db)
            self.create_tables_if_needed(conn)
        except Error as e:
            logger.error(f'Cannot connect to the database {self.db}: {e}')

        return conn

    def create_tables_if_needed(self, conn):
        # sqlite3.connect creates an empty file when the database doesn't exist yet
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'expenses'").fetchall()

        if len(tables) > 0:
            self.add_income_column_if_needed(conn)
            self.add_not_computed_column_if_needed(conn)
            self.add_rules_table_if_needed(conn)
            return

        logger.info(f'Creating the tables in {self.db}')

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

        logger.info(f'Adding the income column to expense_types in {self.db}')
        self.backup()

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

        logger.info(f'Adding the not_computed column to expense_types in {self.db}')
        self.backup()

        with conn:
            conn.execute("ALTER TABLE expense_types ADD COLUMN not_computed BOOLEAN DEFAULT FALSE")

    def add_rules_table_if_needed(self, conn):
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'rules'").fetchall()

        if len(tables) > 0:
            return

        logger.info(f'Adding the rules table to {self.db}')
        self.backup()

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
