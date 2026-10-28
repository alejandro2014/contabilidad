import unittest
from unittest.mock import call, Mock

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

    def test__find_rule_index(self):
        self.assertEqual(1, self.rules_service.find_rule_index(self.rules, 'Pago en Amazon.es'))
        self.assertIsNone(self.rules_service.find_rule_index(self.rules, 'Pago en LIDL'))

    def test__add_rule__not_added_twice(self):
        self.rules_service.db = Mock()
        self.rules_service.db.select.return_value = [ (1,) ]

        result = self.rules_service.add_rule('Comida', 'MERCADONA')

        self.assertEqual(1, result)
        self.rules_service.db.execute_sql.assert_not_called()

    def test__add_rule__new_rule(self):
        self.rules_service.db = Mock()
        self.rules_service.db.select.return_value = [ (0,) ]

        self.rules_service.add_rule('Comida', 'MERCADONA')

        self.rules_service.db.execute_sql.assert_called_once_with(self.rules_service.sql_generator.insert_rule('Comida', 'MERCADONA'))

    def test__swap_priorities__moves_one_out_of_the_way_first(self):
        self.rules_service.db = Mock()

        self.rules_service.swap_priorities(3, 4)

        sql_generator = self.rules_service.sql_generator
        self.rules_service.db.execute_sql.assert_has_calls([
            call(sql_generator.update_rule_priority(3, 0)),
            call(sql_generator.update_rule_priority(4, 3)),
            call(sql_generator.update_rule_priority(0, 4))
        ])
