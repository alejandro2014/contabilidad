from db.SqliteConnector import SqliteConnector
from db.SqlGenerator import SqlGenerator

class BaseService:
    def __init__(self):
        self.sql_generator = SqlGenerator()
        self.db = SqliteConnector()
