from src.services.categories_service import CategoriesService


class CategoriesComboboxService:
    def __init__(self):
        self.categories_service = CategoriesService()

    def get_values(self):
        return self.categories_service.get_category_names()