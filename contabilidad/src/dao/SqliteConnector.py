import sqlite3
from sqlite3 import Error

class SqliteConnector:
    def __init__(self, print_sql_flag):
        self.db = "src/config/db/accountancy.db"
        self.print_sql_flag = print_sql_flag

    def select(self, sql):
        self.print_sql(sql)
        conn = self.create_connection()
        rows = []

        with conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()

        return rows

    def insert(self, sql):
        self.print_sql(sql)
        self.execute_sql(sql)

    def delete(self, sql):
        self.print_sql(sql)
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

    def print_sql(self, sql):
        if self.print_sql_flag:
            print(sql)
