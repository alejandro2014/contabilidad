from src.cli.BaseArgsParse import BaseArgsParse
from src.services.RulesService import RulesService

class RulesArgsParser(BaseArgsParse):
    def rules_list(self, args):
        rules_service = RulesService()
        rules = rules_service.get_rules()

        self.print_list(rules, 'rules')

    def rules_add(self, args):
        category = args.category
        rule = args.rule

        self.check_param('--category', category)
        self.check_param('--rule', rule)

        rules_service = RulesService()
        rules_service.add_rule(category, rule)

    def rules_delete(self, args):
        category = args.category
        rule = args.rule

        self.check_param('--category', category)
        self.check_param('--rule', rule)

        rules_service = RulesService()
        rules_service.delete_rule(category, rule)

    def rules_import(self, args):
        file_path = args.file_path

        self.check_param('--file-path', file_path)
        self.check_file_exist(file_path)

        rules_service = RulesService()
        rules_service.import_rules(file_path)

    def rules_export(self, args):
        file_path = args.file_path

        self.check_param('--file-path', file_path)
        self.check_file_not_exist(file_path)

        rules_service = RulesService()
        rules_service.export_rules(file_path)
