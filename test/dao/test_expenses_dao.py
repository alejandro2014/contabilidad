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
        # How many expenses there are before and after loading them
        mock_db.select.side_effect = [ [ (10,) ], [ (11,) ] ]

        dao = ExpensesDao(db=mock_db)

        successes_number, errors_number = dao.load_expenses(self.get_two_expenses())

        self.assertEqual(1, successes_number)
        self.assertEqual(1, errors_number)

    def test__load_expenses__a_single_transaction_after_a_backup(self):
        mock_db = Mock()
        mock_db.select.side_effect = [ [ (0,) ], [ (2,) ] ]

        dao = ExpensesDao(db=mock_db)

        successes_number, errors_number = dao.load_expenses(self.get_two_expenses())

        self.assertEqual((2, 0), (successes_number, errors_number))
        self.assertEqual([ call.backup(), call.execute_many(dao.sql_generator.insert_expenses(), ANY) ], [ c for c in mock_db.mock_calls if c[0] != 'select' ])
        self.assertEqual(2, len(mock_db.execute_many.call_args[0][1]))

    def test__get_pending_expenses(self):
        mock_db = Mock()
        mock_db.select.return_value = [
            ('id1', 'date1', 'title1', -1.5),
            ('id2', 'date2', 'title2', -2.5)
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
                amount = -1.5
            ),
            Expense(
                id = 'id2',
                date = 'date2',
                title = 'title2',
                amount = -2.5
            )
        ]


        
class ExpensesDaoDatabaseTestCase(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()

        self.db = SqliteConnector(os.path.join(self.directory.name, 'test.db'))

        self.dao = ExpensesDao(sql_generator=SqlGenerator(), db=self.db)

    def tearDown(self):
        self.db.close()
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

    def test__amounts__stored_in_cents_and_read_in_euros(self):
        self.db.execute_sql("INSERT INTO expense_types (category) VALUES ('Café')")

        self.dao.load_expenses([
            Expense(id = '1', date = '20260105', title = 'Café', amount = -0.1, category = 'Café'),
            Expense(id = '2', date = '20260106', title = 'Café', amount = -0.2, category = 'Café')
        ])

        self.assertEqual([ (-10,), (-20,) ], self.db.select('SELECT amount FROM expenses ORDER BY id'))
        self.assertEqual([ -0.1, -0.2 ], [ e.amount for e in self.dao.get_classified_expenses(sort_by='date') ])
        self.assertEqual([ { 'type': 'Café', 'quantity': '-0.3' } ], self.dao.get_classified_expenses_by_type())

    def test__get_classified_expenses_by_month(self):
        self.db.execute_transaction([
            "DELETE FROM rules",
            "DELETE FROM expense_types",
            "INSERT INTO expense_types (category) VALUES ('Comida')",
            "INSERT INTO expenses (id, date, title, amount, category) VALUES ('1', '20260105', 'A', -1000, 'Comida'), ('2', '20260215', 'B', -550, 'Comida')"
        ])

        self.assertEqual([ { 'month': '202601', 'quantity': '-10.0' }, { 'month': '202602', 'quantity': '-5.5' } ], self.dao.get_classified_expenses_by_month())

    def test__load_expenses__already_loaded_get_their_balance(self):
        # Loaded before the balance was stored, and loaded again from a statement with it
        self.dao.load_expenses([ Expense(id = '1', date = '20260105', title = 'Café', amount = -1.5) ])

        inserted = self.dao.load_expenses([
            Expense(id = '2', date = '20260105', title = 'Café', amount = -1.5, balance = 998.5),
            Expense(id = '3', date = '20260106', title = 'Pan', amount = -1.0, balance = 997.5)
        ])

        self.assertEqual((1, 1), inserted)
        self.assertEqual([ ('1', 99850), ('3', 99750) ], self.db.select('SELECT id, balance FROM expenses ORDER BY date'))

    def test__load_expenses__balance_already_known_is_kept(self):
        self.dao.load_expenses([ Expense(id = '1', date = '20260105', title = 'Café', amount = -1.5, balance = 998.5) ])
        self.dao.load_expenses([ Expense(id = '2', date = '20260105', title = 'Café', amount = -1.5, balance = 1.0) ])

        self.assertEqual([ (99850,) ], self.db.select('SELECT balance FROM expenses'))

    def test__notes_and_tags(self):
        self.insert_classified_expenses()

        self.dao.update_notes_and_tags([ '1', '2' ], 'Con amigos', [ 'Viaje', 'Roma' ])
        self.dao.update_notes_and_tags([ '2' ], None, [ 'Viaje' ])

        expenses = self.dao.get_classified_expenses(sort_by='date')

        self.assertEqual([ ('Con amigos', [ 'Roma', 'Viaje' ]), (None, [ 'Viaje' ]), (None, []), (None, []) ], [ (e.note, e.tags) for e in expenses ])
        self.assertEqual([ 'Roma', 'Viaje' ], self.dao.get_tags())

    def test__get_classified_expenses__by_tag(self):
        self.insert_classified_expenses()
        self.dao.update_notes_and_tags([ '2' ], None, [ 'Viaje' ])

        self.assertEqual([ '2' ], [ e.id for e in self.dao.get_classified_expenses({ 'tag': 'Viaje' }) ])

    def test__get_tag_totals__only_the_expenses_of_the_range(self):
        self.insert_classified_expenses()
        self.dao.update_notes_and_tags([ '1', '2', '3', '4' ], None, [ 'Viaje' ])

        # The income is left out, and the third expense is out of the range
        totals = self.dao.get_tag_totals({ 'date': { 'from': '20260101', 'to': '20260131' } })

        self.assertEqual([ { 'tag': 'Viaje', 'quantity': '-15.5', 'count': '2' } ], totals)

    def test__tags__deleted_with_their_expense(self):
        self.insert_classified_expenses()
        self.dao.update_notes_and_tags([ '1' ], None, [ 'Viaje' ])

        self.db.execute_sql("DELETE FROM expenses WHERE id = '1'")

        self.assertEqual([], self.dao.get_tags())

    def insert_classified_expenses(self):
        self.db.execute_transaction([
            "DELETE FROM rules",
            "DELETE FROM expense_types",
            "INSERT INTO expense_types (category, income) VALUES ('Comida', FALSE), ('Nómina', TRUE)",
            "INSERT INTO expenses (id, date, title, amount, category) VALUES ('1', '20260105', 'A', -1000, 'Comida'), ('2', '20260115', 'B', -550, 'Comida'), " +
                "('3', '20260215', 'C', -100, 'Comida'), ('4', '20260128', 'Nómina', 200000, 'Nómina')"
        ])
