import unittest
from modules.emulators.csrf import simulate_csrf

class TestCSRF(unittest.TestCase):
    def test_valid_referer(self):
        # 有效的 Referer 应返回成功状态
        request = type('Request', (object,), {'headers': {'Referer': 'https://example.com'}})
        response = simulate_csrf(request)
        self.assertEqual(response['status'], 'ok')

    def test_invalid_referer(self):
        # 来自恶意站点的 Referer 应返回阻止状态
        request = type('Request', (object,), {'headers': {'Referer': 'https://evil.com'}})
        response = simulate_csrf(request)
        self.assertEqual(response['status'], 'blocked')

    def test_missing_referer(self):
        # 缺少 Referer 应返回阻止状态
        request = type('Request', (object,), {'headers': {}})
        response = simulate_csrf(request)
        self.assertEqual(response['status'], 'blocked')

if __name__ == '__main__':
    unittest.main()
