import sqlite3
from sqlite3 import Error

class SqliteConnector:
    def __init__(self):
        self.db = "src/config/db/accountancy.db"

    def select(self, sql):
        print(sql)
        conn = self.create_connection()
        rows = []

        with conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()

        return rows

    def insert(self, sql):
        print(sql)
        self.execute_sql(sql)

    def delete(self, sql):
        print(sql)
        self.execute_sql(sql)

    def update(self, sql):
        print(sql)
        self.execute_sql(sql)

    def execute_sql(self, sql):
        conn = self.create_connection()

        with conn:
            cur = conn.cursor()
            cur.execute(sql)

    def create_connection(self):
        conn = None

        try:
            conn = sqlite3.connect(self.db)
        except Error as e:
            print(e)

        return conn
