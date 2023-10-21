from src.services.LoadFileService import LoadFileService

file_path = '2301.xls'

load_file_service = LoadFileService()

print(load_file_service.load_file(file_path))