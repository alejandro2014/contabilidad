import sqlite3
from sqlite3 import Error
import os

class SqliteConnector:
    def __init__(self, db_path="db/accountancy.db", debug_mode=True):
        print(f"Current directory: {os.getcwd()}")

        self.db = os.getcwd() + "/" + db_path
        self.debug_mode = debug_mode
    
    def run_sql(self, sql, params=None):
        if self.debug_mode:
            print('-------------------')
            print(sql)
            print(params)

        conn = self.create_connection()
        rows = []

        with conn:
            cur = conn.cursor()

            if params is None:
                cur.execute(sql)
            else:
                cur.execute(sql, params)

            rows = cur.fetchall()

        return rows

    def create_connection(self):
        conn = None

        try:
            conn = sqlite3.connect(self.db)
        except Error as e:
            print(e)
            raise e

        return conn
    
if __name__ == "__main__":
    connector = SqliteConnector("../db/accountancy.db")
    connector.run_sql("""INSERT INTO categories (name, description) VALUES (?, ?)""", ("casa", "Gastos de la casa"))