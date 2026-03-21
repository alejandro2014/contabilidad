import json
import sys
import unittest

from src.zz_old_dao.SqlGenerator import SqlGenerator

class SqlGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        excl_categories = {
            'incomes': [ 'Nómina' ],
            'savings': [ 'Cuenta ahorro' ]
        }

        self.sql_generator = SqlGenerator(excl_categories)
        self.load_tests()

    def test_sql_test_cases(self):
        for test in self.tests:
            print('Running ' + test['method_name'])
            self.generic_sql_test(test)

    def test_excluded_categories(self):
        expected_sql = "type NOT IN ('Nómina','Cuenta ahorro')"
        sql = self.sql_generator.exclusions()

        self.assertEqual(expected_sql, sql)

    def generic_sql_test(self, data):
        method_name = data['method_name']
        expected_sql = data['expected_sql']
        params = data['data'] if data and 'data' in data else None

        if params:
            sql = getattr(self.sql_generator, method_name)(params)
        else:
            sql = getattr(self.sql_generator, method_name)()

        self.assertEqual(expected_sql, sql)

    def load_tests(self):
        with open('test/config/tests.json') as file:
            self.tests = json.load(file)
