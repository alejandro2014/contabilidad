import os

from cli.BaseArgsParse import BaseArgsParse

from src.services.FilesService import FilesService

class FilesArgsParser(BaseArgsParse):
    def files_load(self, args):
        classify = args.classify
        file_path = args.file_path

        self.check_param('--file-path', file_path)
        self.check_file_exist(file_path)

        files_service = FilesService()
        files_service.load_file(file_path, classify=classify)

    def files_delete(self, args):
        file_hash = args.file_hash

        self.check_param('--file-hash', file_hash)

        files_service = FilesService()
        files_service.delete_file(file_hash)

    def files_list(self, args):
        files_service = FilesService()
        files = files_service.get_loaded_files()

        self.print_list(files, 'loaded files')
