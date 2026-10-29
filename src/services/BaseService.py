from src.dao.SqliteConnector import SqliteConnector
from src.dao.SqlGenerator import SqlGenerator
from src.logger import get_logger

logger = get_logger(__name__)

class BaseService:
    def __init__(self):
        self.sql_generator = SqlGenerator()
        self.db = SqliteConnector()

    def get_single_value(self, sql):
        count = self.db.select(sql)

        return count[0][0]

    def insert(self, sql):
        inserted = True

        try:
            self.db.insert(sql)
        except Exception as e:
            logger.error(f'The insert failed: {e}. SQL: {sql}')
            inserted = False

        return inserted

    def delete(self, sql):
        deleted = True

        try:
            self.db.delete(sql)
        except Exception as e:
            logger.error(f'The delete failed: {e}. SQL: {sql}')
            deleted = False

        return deleted
