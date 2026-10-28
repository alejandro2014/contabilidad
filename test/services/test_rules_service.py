import unittest
from unittest.mock import Mock

from src.model.expense import Expense
from src.services.RulesService import RulesService

class RulesServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.rules_service = RulesService()

        self.rules = [
            { 'rule': 'Prime Video', 'category': 'Suscripciones' },
            { 'rule': 'AMAZON', 'category': 'Amazon' },
            { 'rule': 'MERCADONA', 'category': 'Comida' }
        ]

    def test__find_category__contains(self):
        category = self.rules_service.find_category(self.rules, 'Pago en MERCADONA C ALFREDO MARQUMADRID ES')

        self.assertEqual('Comida', category)

    def test__find_category__ignores_case(self):
        category = self.rules_service.find_category(self.rules, 'Pago en Amazon.es')

        self.assertEqual('Amazon', category)

    def test__find_category__first_match_wins(self):
        category = self.rules_service.find_category(self.rules, 'Pago en AMAZON Prime Video')

        self.assertEqual('Suscripciones', category)

    def test__find_category__no_match(self):
        category = self.rules_service.find_category(self.rules, 'Pago en LIDL')

        self.assertIsNone(category)

    def test__classify_expenses__keeps_the_category_already_set(self):
        self.rules_service.db = Mock()
        self.rules_service.db.select.return_value = [ (1, 'MERCADONA', 'Comida') ]

        matched = Expense(title = 'Pago en MERCADONA')
        not_matched = Expense(title = 'Pago en LIDL')
        already_classified = Expense(title = 'Pago en MERCADONA', category = 'Casa')

        self.rules_service.classify_expenses([ matched, not_matched, already_classified ])

        self.assertEqual('Comida', matched.category)
        self.assertIsNone(not_matched.category)
        self.assertEqual('Casa', already_classified.category)
