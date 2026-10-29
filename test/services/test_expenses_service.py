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
