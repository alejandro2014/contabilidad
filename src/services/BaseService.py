from src.dao.SqliteConnector import SqliteConnector
from src.dao.SqlGenerator import SqlGenerator

class BaseService:
    def __init__(self):
        self.sql_generator = SqlGenerator()
        self.db = SqliteConnector()

    def get_single_value(self, sql):
        count = self.db.select(sql)

        return count[0][0]

    def insert(self, sql):
        inserted = True
        value = "OK"

        try:
            self.db.insert(sql)
        except:
            value = "ERROR"
            inserted = False

        print("[" + value + "] " + sql)

        return inserted

    def delete(self, sql):
        deleted = True
        value = "OK"

        try:
            self.db.delete(sql)
        except:
            value = "ERROR"
            deleted = False

        print("[" + value + "] " + sql)

        return deleted
