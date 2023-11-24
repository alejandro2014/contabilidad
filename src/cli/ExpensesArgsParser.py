from cli.BaseArgsParse import BaseArgsParse
from src.services.ExpensesService import ExpensesService

class ExpensesArgsParser(BaseArgsParse):
    def expenses_classify(self, args):
        expense_type = args.expense_type

        if expense_type is None:
            expense_type = 'unclassified'

        expenses_service = ExpensesService()
        expenses = expenses_service.classify_expenses(expense_type=expense_type)

    def expenses_unclassify(self, args):
        ids = args.ids
        file_hash = args.file_hash
        search = args.search
        date = args.date
        date_from = args.date_from
        date_to = args.date_to
        condition = args.condition

        expenses_service = ExpensesService()
        expenses_service.unclassify_expenses(
            ids=ids,
            file_hash=file_hash,
            search=search,
            date=date,
            date_from=date_from,
            date_to=date_to,
            condition=condition
        )

    def expenses_list(self, args):
        expenses_service = ExpensesService()
        expenses = expenses_service.get_expenses(args)

        self.print_list(expenses, 'expenses')

        total_amount = round(sum(map(lambda r: r['amount'], expenses)), 2)
        print(f'Total amount: {total_amount}€')
