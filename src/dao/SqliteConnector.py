import datetime
import glob
import json
import os
import re
import sqlite3
from sqlite3 import Error

from src.config.paths import config_path, db_path
from src.logger import get_logger

logger = get_logger(__name__)

class SqliteConnector:
    # Copies of the database kept in the backups folder
    BACKUPS_NO = 10

    # The connector used by the whole app, with a single connection
    _shared = None

    def __init__(self, db=None):
        self.db = db_path() if db is None else db
        self.conn = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = cls()

        return cls._shared

    def split_query(self, query):
        # A query is the sql alone, or (sql, params) when it has values
        sql, params = query if isinstance(query, tuple) else (query, ())
        logger.debug(f'{sql} {params}')

        return sql, params

    def select(self, query):
        sql, params = self.split_query(query)
        conn = self.connection()

        with conn:
            return conn.execute(sql, params).fetchall()

    def execute_sql(self, query):
        self.execute_transaction([ query ])

    def execute_transaction(self, queries):
        # All the queries are committed together, or none of them when one fails
        conn = self.connection()

        with conn:
            for query in queries:
                conn.execute(*self.split_query(query))

    def execute_many(self, sql, rows):
        # A single transaction for all the rows. Returns how many rows have been changed
        logger.debug(f'{sql} ({len(rows)} rows)')
        conn = self.connection()

        with conn:
            return conn.executemany(sql, rows).rowcount

    def connection(self):
        # Opened on first use and kept open until close()
        if self.conn is not None:
            return self.conn

        try:
            self.conn = sqlite3.connect(self.db)
            self.migrate(self.conn)
            # It can't be changed inside a transaction, and the migrations rebuild tables with it off
            self.conn.execute('PRAGMA foreign_keys = ON')
        except Error as e:
            logger.error(f'Cannot open the database {self.db}: {e}')
            self.close()
            raise

        return self.conn

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def backups_folder(self):
        return os.path.join(os.path.dirname(self.db), 'backups')

    def backup(self):
        # Copy of the database before changing a lot of data at once (imports, schema migrations)
        if not os.path.exists(self.db) or os.path.getsize(self.db) == 0:
            return

        self.backup_from(self.connection())

    def backup_from(self, conn):
        folder = self.backups_folder()
        os.makedirs(folder, exist_ok=True)

        name = os.path.splitext(os.path.basename(self.db))[0]
        backup_file = os.path.join(folder, f'{name}-{datetime.datetime.now():%Y%m%d-%H%M%S}.db')

        # Within the same second only the first copy is kept: it is the one from before every change
        if not os.path.exists(backup_file):
            logger.info(f'Backup of {self.db} in {backup_file}')

            # The backup API copies a consistent database even with the connection open
            target = sqlite3.connect(backup_file)

            try:
                conn.backup(target)
            finally:
                target.close()

        self.remove_old_backups(folder, name)

    def remove_old_backups(self, folder, name):
        # The names have the date, so sorted by name they are sorted by date
        backups = sorted(glob.glob(os.path.join(folder, f'{glob.escape(name)}-*.db')))

        for old_backup in backups[:-self.BACKUPS_NO]:
            os.remove(old_backup)

    def get_migrations(self):
        # Numbered scripts (001-name.sql): the number is the user_version of the database once it has run
        migrations = []

        for file in glob.glob(config_path('db', 'migrations', '*.sql')):
            match = re.match(r'^(\d+)-', os.path.basename(file))

            if match:
                migrations.append((int(match.group(1)), file))

        return sorted(migrations)

    def get_version(self, conn):
        return conn.execute('PRAGMA user_version').fetchone()[0]

    def migrate(self, conn):
        version = self.get_version(conn)
        pending = [ (number, file) for number, file in self.get_migrations() if number > version ]

        if len(pending) == 0:
            return

        # sqlite3.connect creates an empty file when the database doesn't exist yet: nothing to back up
        if self.table_exists(conn, 'expenses'):
            self.backup_from(conn)

        for number, file in pending:
            logger.info(f'Migrating {self.db} to version {number} ({os.path.basename(file)})')
            self.run_in_transaction(conn, lambda: self.apply_migration(conn, number, file))

    def split_statements(self, script):
        # executescript commits the open transaction, so the statements of a script are run one by one
        statements = []
        statement = ''

        for line in script.splitlines(keepends=True):
            statement += line

            if sqlite3.complete_statement(statement):
                statements.append(statement.strip())
                statement = ''

        return statements

    def run_in_transaction(self, conn, steps):
        # Without isolation level sqlite3 doesn't begin or commit on its own, so the whole migration is a single transaction
        isolation_level = conn.isolation_level
        conn.isolation_level = None

        try:
            conn.execute('BEGIN')

            try:
                steps()
                conn.execute('COMMIT')
            except BaseException:
                conn.execute('ROLLBACK')
                raise
        finally:
            conn.isolation_level = isolation_level

    def apply_migration(self, conn, number, file):
        if number == 1 and self.table_exists(conn, 'expenses'):
            self.upgrade_unversioned_database(conn)
        else:
            with open(file, encoding='utf-8') as sql_file:
                for statement in self.split_statements(sql_file.read()):
                    conn.execute(statement)

            if number == 1:
                self.insert_initial_rules(conn)

        if len(conn.execute('PRAGMA foreign_key_check').fetchall()) > 0:
            raise sqlite3.IntegrityError(f'The migration {os.path.basename(file)} leaves rows without their expense type')

        conn.execute(f'PRAGMA user_version = {int(number)}')

    def table_exists(self, conn, table):
        return len(conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)).fetchall()) > 0

    def get_columns(self, conn, table):
        return [ c[1] for c in conn.execute(f"PRAGMA table_info({table})").fetchall() ]

    def upgrade_unversioned_database(self, conn):
        # Databases from before the versioned migrations are brought to the schema of the first one
        for column in [ 'subcategory', 'category_src', 'subcategory_src', 'category_suggested', 'subcategory_suggested' ]:
            if column not in self.get_columns(conn, 'expenses'):
                conn.execute(f"ALTER TABLE expenses ADD COLUMN {column} STRING NULL")

        columns = self.get_columns(conn, 'expense_types')

        # Databases created before the income flag have an unused "positive" column instead
        if 'income' not in columns:
            if 'positive' in columns:
                conn.execute("ALTER TABLE expense_types RENAME COLUMN positive TO income")
            else:
                conn.execute("ALTER TABLE expense_types ADD COLUMN income BOOLEAN DEFAULT FALSE")

            # These categories were the incomes before the flag existed
            conn.execute("UPDATE expense_types SET income = TRUE WHERE category IN ('Nómina', 'Otros ingresos')")

        if 'not_computed' not in columns:
            conn.execute("ALTER TABLE expense_types ADD COLUMN not_computed BOOLEAN DEFAULT FALSE")

        if not self.table_exists(conn, 'rules'):
            conn.execute("CREATE TABLE rules (priority INTEGER NOT NULL PRIMARY KEY, rule VARCHAR NOT NULL, category VARCHAR NOT NULL)")
            self.insert_initial_rules(conn)

    def insert_initial_rules(self, conn):
        # Rules composed from the expenses already classified. The first one in the list has the highest priority
        with open(config_path('db', 'initial-rules.json'), encoding="utf-8") as rules_file:
            rules = json.load(rules_file)

        # The types of the rules have to exist. These categories are the incomes
        categories = dict.fromkeys(r['category'] for r in rules)
        conn.executemany(
            "INSERT OR IGNORE INTO expense_types (category, income) VALUES (?, ?)",
            [ (c, c in ('Nómina', 'Otros ingresos')) for c in categories ]
        )

        conn.executemany(
            "INSERT INTO rules (priority, rule, category) VALUES (?, ?, ?)",
            [ (priority, r['rule'], r['category']) for priority, r in enumerate(rules, 1) ]
        )
