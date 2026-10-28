import unittest

from src.model.expense import Expense

class ExpenseTestCase(unittest.TestCase):
    def test__eq__same_date_title_and_amount(self):
        # The same movement loaded twice has a different id, and maybe a category
        expense = Expense(id = 'id1', date = '20260105', title = 'Alquiler', amount = -937.58)
        same_expense = Expense(id = 'id2', date = '20260105', title = 'Alquiler', amount = -937.58, category = 'Alquiler')

        self.assertEqual(expense, same_expense)

    def test__eq__different_amount(self):
        expense = Expense(date = '20260105', title = 'Alquiler', amount = -937.58)
        other_expense = Expense(date = '20260105', title = 'Alquiler', amount = -900.0)

        self.assertNotEqual(expense, other_expense)

    def test__eq__other_type_is_an_error(self):
        with self.assertRaises(TypeError):
            Expense() == 'Alquiler'
