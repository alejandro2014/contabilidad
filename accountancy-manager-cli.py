#!/usr/bin/env python3
from src.cli.ArgsParser import ArgsParser
from src.cli.CategoriesArgsParser import CategoriesArgsParser
from src.cli.ExpensesArgsParser import ExpensesArgsParser
from src.cli.FilesArgsParser import FilesArgsParser
from src.cli.RulesArgsParser import RulesArgsParser

class Cli:
    def __init__(self):
        self.possible_commands = {
            'categories': ['add', 'delete', 'edit', 'list'],
            'expenses': ['classify', 'unclassify', 'list'],
            'files': ['load', 'delete', 'list'],
            'rules': ['list', 'add', 'delete', 'import', 'export'],
        }

        self.categories_args_parser = CategoriesArgsParser()
        self.expenses_args_parser = ExpensesArgsParser()
        self.files_args_parser = FilesArgsParser()
        self.rules_args_parser = RulesArgsParser()

        self.args_parser = ArgsParser(self.possible_commands)

    def parse_input(self):
        command, subcommand = self.args_parser.get_command()
        args = self.args_parser.args

        args_parser = getattr(self, f'{command}_args_parser')

        getattr(args_parser, f'{command}_{subcommand}')(args)

cli = Cli()
cli.parse_input()

exit()
from src.services.LoadFileService import LoadFileService

file_path = '2301.xls'

load_file_service = LoadFileService()

print(load_file_service.load_file(file_path))