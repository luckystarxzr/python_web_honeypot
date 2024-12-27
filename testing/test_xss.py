import unittest
from modules.emulators.xss import simulate_xss

class TestXSS(unittest.TestCase):
    def test_valid_payload(self):
        # 正常输入应返回成功状态
        request = type('Request', (object,), {'args': {'payload': 'Hello, world!'}})
        response = simulate_xss(request)
        self.assertEqual(response['status'], 'ok')

    def test_xss_payload(self):
        # 恶意脚本应返回阻止状态
        request = type('Request', (object,), {'args': {'payload': '<script>alert(1)</script>'}})
        response = simulate_xss(request)
        self.assertEqual(response['status'], 'blocked')

    def test_empty_payload(self):
        # 空输入应返回成功状态
        request = type('Request', (object,), {'args': {'payload': ''}})
        response = simulate_xss(request)
        self.assertEqual(response['status'], 'ok')

if __name__ == '__main__':
    unittest.main()
