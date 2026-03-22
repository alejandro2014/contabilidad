from src.dao.sqlite_connector import SqliteConnector
from src.model.Category import Category

class CategoriesDao:
    def __init__(self, db_connector=SqliteConnector()):
        self._db = db_connector

    def add_category(self, name, description=None):
        if description is None:
            sql = "INSERT INTO categories (name) VALUES (?)"
            self._db.run_sql(sql, (name,))
        else:
            sql = "INSERT INTO categories (name, description) VALUES (?, ?)"
            self._db.run_sql(sql, (name, description))

    def delete_category(self, name):
        sql = "DELETE FROM categories WHERE name = ?"
        self._db.run_sql(sql, (name,))

    def delete_categories(self, categories):
        placeholders = ",".join("?" for _ in categories)
        sql = f"DELETE FROM categories WHERE name IN ({placeholders})"
        self._db.run_sql(sql, categories)

    def category_exists(self, name):
        sql = "SELECT COUNT(*) FROM categories WHERE name = ?"

        returned = self._db.run_sql(sql, (name,))

        return returned[0][0] > 0

    def get_categories(self):
        sql = "SELECT name, description FROM categories ORDER BY name"

        result = self._db.run_sql(sql)

        return [
            Category(
                name=r[0],
                description=r[1]
            ) for r in result
        ]
    
    def get_category_names(self):
        sql = "SELECT name FROM categories ORDER BY name"

        result = self._db.run_sql(sql)

        return [ r[0] for r in result ]

    def update_category(self, name, new_name=None, description=None):
        if new_name is not None and description is None:
            self._update_category_name(name, new_name)
        elif new_name is None and description is not None:
            self._update_category_description(name, description)
        else:
            self._update_category_name_and_description(name, new_name, description)

    def _update_category_name(self, name, new_name):
        sql = "UPDATE categories SET name = ? WHERE name = ?"
        self._db.run_sql(sql, (new_name, name,))

    def _update_category_description(self, name, description=None):
        sql = "UPDATE categories SET description = ? WHERE name = ?"
        self._db.run_sql(sql, (description, name,))

    def _update_category_name_and_description(self, name, new_name, description):
        sql = "UPDATE categories SET name = ?, description = ? WHERE name = ?"
        self._db.run_sql(sql, (new_name, description, name,))


if __name__ == "__main__":
    def print_categories(dao):
        categories = dao.get_categories()

        print('-----------')
        for c in categories:
            print(c)

    dao = CategoriesDao()

    dao.delete_category(name='casoploncillo')
    print_categories(dao)
    
    print_categories(dao)

    print(dao.category_exists('casa'))

    dao.add_category(name='casa', description='Gastos de la casa')
    print_categories(dao)

    print(dao.category_exists('casa'))

    dao.update_category(name='casa', description='Casita linda')
    print_categories(dao)

    dao.update_category(name='casa', new_name='casoplon')
    print_categories(dao)

    dao.update_category(name='casoplon', new_name='casoploncillo', description='Menudo casoplon')
    print_categories(dao)

    dao.delete_category(name='casoploncillo')
    print_categories(dao)