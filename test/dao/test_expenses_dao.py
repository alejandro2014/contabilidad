import os
import tempfile
import unittest
from unittest import TestCase
from unittest.mock import ANY, call, Mock

from src.dao.expenses_dao import ExpensesDao
from src.dao.SqlGenerator import SqlGenerator
from src.dao.SqliteConnector import SqliteConnector
from src.model.expense import Expense

class ExpensesDaoTestCase(TestCase):
    def test__load_expenses__one_already_loaded(self):
        mock_db = Mock()
        mock_db.execute_many.return_value = 1

        dao = ExpensesDao(db=mock_db)

        successes_number, errors_number = dao.load_expenses(self.get_two_expenses())

        self.assertEqual(1, successes_number)
        self.assertEqual(1, errors_number)

    def test__load_expenses__a_single_transaction_after_a_backup(self):
        mock_db = Mock()
        mock_db.execute_many.return_value = 2

        dao = ExpensesDao(db=mock_db)

        successes_number, errors_number = dao.load_expenses(self.get_two_expenses())

        self.assertEqual((2, 0), (successes_number, errors_number))
        self.assertEqual([ call.backup(), call.execute_many(dao.sql_generator.insert_expenses(), ANY) ], mock_db.mock_calls)
        self.assertEqual(2, len(mock_db.execute_many.call_args[0][1]))

    def test__get_pending_expenses(self):
        mock_db = Mock()
        mock_db.select.return_value = [
            ('id1', 'date1', 'title1', 'amount1'),
            ('id2', 'date2', 'title2', 'amount2')
        ]

        dao = ExpensesDao(db=mock_db)

        expected_expenses = self.get_two_expenses()

        pending_expenses = dao.get_pending_expenses(filter=None, sort_by=None)

        self.assertEqual(len(expected_expenses), len(pending_expenses))
        
        for index, pending_expense in enumerate(pending_expenses):
            self.assertEqual(expected_expenses[index], pending_expense)

    def test__get_pending_expenses__sorted_by(self):
        mock_db = Mock()
        mock_db.select.return_value = []

        ExpensesDao(db=mock_db).get_pending_expenses(sort_by='title')

        self.assertTrue(mock_db.select.call_args[0][0][0].endswith(' ORDER BY title ASC'))

    def test__get_expenses_date_range(self):
        mock_db = Mock()
        mock_db.select.return_value = [
            (0, '20240105', '20240310', 3),
            (1, '20230101', '20240228', 10)
        ]

        dao = ExpensesDao(db=mock_db)

        date_range = dao.get_expenses_date_range()

        self.assertEqual({ 'min_date': '20230101', 'max_date': '20240228', 'count': 10 }, date_range['classified'])
        self.assertEqual({ 'min_date': '20240105', 'max_date': '20240310', 'count': 3 }, date_range['pending'])

    def test__get_expenses_date_range__no_pending(self):
        mock_db = Mock()
        mock_db.select.return_value = [ (1, '20230101', '20240228', 10) ]

        dao = ExpensesDao(db=mock_db)

        date_range = dao.get_expenses_date_range()

        self.assertIsNone(date_range['pending'])

    def test__update_classified_expense(self):
        uuid = '3f6d08d1-ca0c-48da-bc35-148fc037d901'
        category = 'Alquiler'

        mock_sql_generator = Mock()
        mock_db = Mock()

        dao = ExpensesDao(sql_generator=mock_sql_generator, db=mock_db)
        dao.update_classified_expense(uuid, category)

        mock_sql_generator.update_classified_expense.assert_has_calls([call(uuid, category)])
        mock_db.execute_sql.assert_has_calls([call(mock_sql_generator.update_classified_expense.return_value)])

    def get_two_expenses(self):
        return [
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


        
class ExpensesDaoDatabaseTestCase(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()

        self.db = SqliteConnector()
        self.db.db = os.path.join(self.directory.name, 'test.db')

        self.dao = ExpensesDao(sql_generator=SqlGenerator(), db=self.db)

    def tearDown(self):
        self.directory.cleanup()

    def test__load_expenses__quotes_and_already_loaded(self):
        expenses = [
            Expense(id = '1', date = '20260105', title = "Pago en O'HARA", amount = -12.5),
            Expense(id = '2', date = '20260106', title = 'Pago en LIDL', amount = -10.0, category = 'Comida')
        ]

        self.assertEqual((2, 0), self.dao.load_expenses(expenses))

        # The same movements again, with other ids
        expenses[0].id = '3'
        expenses[1].id = '4'

        self.assertEqual((0, 2), self.dao.load_expenses(expenses))

        pending = self.dao.get_pending_expenses(filter={ 'search_value': "O'HARA" }, sort_by='amount')

        self.assertEqual([ "Pago en O'HARA" ], [ e.title for e in pending ])
