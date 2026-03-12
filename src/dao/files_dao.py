from datetime import datetime
from model.File import File

class FilesDao:
    def __init__(self, db_connector):
        self._db = db_connector

    def add_file(self, file_name, hash):
        date_loaded = str(datetime.now())

        sql = "INSERT INTO files (hash, name, date_loaded) VALUES (?, ?, ?)"
        params = (hash, file_name, date_loaded)
        self._db.run_sql(sql, params)

    def delete_file(self, hash_file):
        sql = "DELETE FROM files WHERE hash = ?"

        self._db.run_sql(sql, (hash_file,))

    def is_file_loaded(self, hash_file):
        sql = "SELECT * FROM files WHERE hash = ?"

        returned = self._db.run_sql(sql, (hash_file,))

        return len(returned) > 0

    def get_loaded_files(self):
        sql = f"SELECT * FROM files ORDER BY file_name"

        raw_result = self._db.run_query(sql)

        return [
            File(
                hash=r[0],
                name=r[1],
                date_loaded=r[2]
            ) for r in raw_result
        ]
