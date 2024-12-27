import unittest
from modules.emulators.sql_injection import simulate_sql_injection

class TestSQLInjection(unittest.TestCase):
    def test_valid_query(self):
        # 正常查询应返回成功状态
        request = type('Request', (object,), {'args': {'query': 'SELECT * FROM users'}})
        response = simulate_sql_injection(request)
        self.assertEqual(response['status'], 'ok')

    def test_injection_query(self):
        # 恶意注入应返回阻止状态
        request = type('Request', (object,), {'args': {'query': 'DROP TABLE users'}})
        response = simulate_sql_injection(request)
        self.assertEqual(response['status'], 'blocked')

    def test_empty_query(self):
        # 空查询应返回成功状态
        request = type('Request', (object,), {'args': {'query': ''}})
        response = simulate_sql_injection(request)
        self.assertEqual(response['status'], 'ok')

if __name__ == '__main__':
    unittest.main()
