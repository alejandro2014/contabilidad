from src.cli.BaseArgsParse import BaseArgsParse

from src.services.CategoriesService import CategoriesService

class CategoriesArgsParser(BaseArgsParse):
    def categories_add(self, args):
        name = args.name
        description = args.description

        self.check_param('--name', name)

        categories_service = CategoriesService()
        categories_service.add_category(name, description)

    def categories_delete(self, args):
        name = args.name

        self.check_param('--name', name)

        categories_service = CategoriesService()
        categories_service.delete_category(name)

    def categories_edit(self, args):
        name = args.name
        new_name = args.new_name
        description = args.description

        self.check_param('--name', name)

        categories_service = CategoriesService()
        categories_service.edit_category(name, new_name, description)

    def categories_list(self, args):
        categories_service = CategoriesService()
        categories = categories_service.get_categories()

        self.print_list(categories, 'categories')
