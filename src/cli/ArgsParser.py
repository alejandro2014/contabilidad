import argparse

class ArgsParser:
    def __init__(self, possible_commands):
        parser = self.get_parser()
        self.args = parser.parse_args()

        self.possible_commands = possible_commands

    def get_parser(self):
        parser = argparse.ArgumentParser(description='Accountancy manager v0.2')

        parser.add_argument('command', help='Command to be executed')
        parser.add_argument('subcommand', help='Subcommand to be executed')

        arguments = [
            '--category',
            '--condition',
            '--date',
            '--date-from',
            '--date-to',
            '--description',
            '--expense-type',
            '--file-hash',
            '--file-path',
            '--ids',
            '--name',
            '--new-name',
            '--rule',
            '--search',
        ]

        for arg in arguments:
            parser.add_argument(arg)

        parser.add_argument('--classify', action='store_true')

        return parser

    def get_command(self):
        possible_commands = self.possible_commands.keys()

        if self.args.command not in possible_commands:
            self.print_error_in_choice('command', self.args.command, possible_commands)
            exit(1)

        possible_subcommands = self.possible_commands[self.args.command]

        if self.args.subcommand not in possible_subcommands:
            self.print_error_in_choice('subcommand', self.args.subcommand, possible_subcommands)
            exit(1)

        return self.args.command, self.args.subcommand

    def get_args(self):
        return self.args

    def print_error_in_choice(self, type, value, possible_values):
        print(f"Error: The {type} '{value}' does not exist")
        print(f'Possible {type}s:')

        for possible_value in possible_values:
            print(f'\t{possible_value}')
