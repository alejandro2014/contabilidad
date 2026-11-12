import unittest
from unittest.mock import Mock

from src.services.expenses_service import ExpensesService

class ExpensesServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.dao = Mock()
        self.dao.get_tags.return_value = [ 'Viaje Roma' ]
        self.expenses_service = ExpensesService(dao=self.dao)

    def test__update_notes_and_tags__cleaned(self):
        self.expenses_service.update_notes_and_tags([ 'id1' ], '  Con amigos ', ' viaje  roma, Regalos ,, REGALOS ')

        # The tags that exist keep how they are written, and the repeated ones are only once
        self.dao.update_notes_and_tags.assert_called_once_with([ 'id1' ], 'Con amigos', [ 'Viaje Roma', 'Regalos' ])

    def test__update_notes_and_tags__empty(self):
        self.expenses_service.update_notes_and_tags([ 'id1' ], '   ', '')

        self.dao.update_notes_and_tags.assert_called_once_with([ 'id1' ], None, [])

    def test__add_cash_expense__given_back_to_cash(self):
        self.expenses_service.add_cash_expense('20261104', 'Mercado', 20.5, 'Comida')

        # The expense with its type, and the same amount back to the cash withdrawn, so it doesn't count twice
        expense, cash = self.dao.add_expenses.call_args[0][0]

        self.assertEqual((expense.date, expense.title, expense.amount, expense.category), ('20261104', 'Mercado', -20.5, 'Comida'))
        self.assertEqual((cash.date, cash.title, cash.amount, cash.category), ('20261104', 'Mercado', 20.5, 'Efectivo'))
        self.assertNotEqual(expense.id, cash.id)
