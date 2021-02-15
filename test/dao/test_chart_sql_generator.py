import json
import sys
import unittest

from src.dao.ChartSqlGenerator import ChartSqlGenerator

class ChartSqlGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.sql_generator = ChartSqlGenerator()
        self.load_tests()

    def test_sql_test_cases(self):
        for test in self.tests:
            print('Running ' + test['method_name'])
            self.generic_sql_test(test)

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
        with open('test/config/tests-charts.json') as file:
            self.tests = json.load(file)
