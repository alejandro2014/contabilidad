from sqlite3 import IntegrityError

import unittest
from unittest import TestCase
from unittest.mock import Mock

from src.dao.expenses_dao import ExpensesDao
from src.model.expense import Expense

class ExpensesDaoTestCase(TestCase):
    def test__load_expenses(self):
        mock_db = Mock()
        mock_db.execute_sql.side_effect = [[], IntegrityError("Test integrity error")]

        dao = ExpensesDao(db=mock_db)

        input_expenses = [
            Expense(
                id = 'id1',
                date = 'date1',
                title = 'title1',
                amount = 'amount1'
            ),
            Expense(
                id = 'id2',
                date = 'date2',
                title = 'title2',
                amount = 'amount2'
            )
        ]

        successes_number, errors_number = dao.load_expenses(input_expenses)

        self.assertEqual(1, successes_number)
        self.assertEqual(1, errors_number)

    def test__get_pending_expenses(self):
        mock_db = Mock()
        mock_db.select.return_value = [
            ('id1', 'date1', 'title1', 'amount1'),
            ('id2', 'date2', 'title2', 'amount2')
        ]

        dao = ExpensesDao(db=mock_db)

        expected_expenses = [
            Expense(
                id = 'id1',
                date = 'date1',
                title = 'title1',
                amount = 'amount1'
            ),
            Expense(
                id = 'id2',
                date = 'date2',
                title = 'title2',
                amount = 'amount2'
            )
        ]

        pending_expenses = dao.get_pending_expenses(filter=None, sort_by=None)

        self.assertEqual(len(expected_expenses), len(pending_expenses))
        
        for index, pending_expense in enumerate(pending_expenses):
            self.assertEqual(expected_expenses[index], pending_expense)


        