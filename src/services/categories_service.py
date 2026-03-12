from src.dao.categories_dao import CategoriesDao

class CategoriesService:
    def __init__(self, categories_dao=CategoriesDao()):
        self.categories_dao = categories_dao

    def category_exists(self, category_name):
        return self.categories_dao.category_exists(category_name)
    
    def add_category(self, name, description=None):
        self.categories_dao.add_category(name, description)
        return True #TODO Add False condition as well

    def delete_category(self, name):
        self.categories_dao.delete_category(name)

    def delete_categories(self, names):
        self.categories_dao.delete_categories(names)

    def get_categories(self):
        return self.categories_dao.get_categories()

    def edit_category(self, name, new_name, description):
        self.categories_dao.update_category(name, new_name, description)