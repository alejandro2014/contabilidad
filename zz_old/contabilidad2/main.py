from dao.categories_dao import CategoriesDao
from backup.contabilidad2.services.categories_service import CategoriesService

service = CategoriesService(categories_dao=CategoriesDao())