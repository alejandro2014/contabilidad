import sqlite3
from sqlite3 import Error

class SqliteConnector:
    def __init__(self):
        self.db = "src/config/db/accountancy.db"

    def select(self, sql):
        print(f'[SQL] {sql}')
        conn = self.create_connection()
        rows = []

        with conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()

        return rows

    def execute_sql(self, sql):
        print(sql)
        conn = self.create_connection()

        with conn:
            cur = conn.cursor()
            cur.execute(sql)

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
            return

        print(f'[INFO] Creating the tables in {self.db}')

        with open("src/config/db/create_database.sql") as sql_file:
            conn.executescript(sql_file.read())
