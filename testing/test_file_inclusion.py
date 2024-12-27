import unittest
from modules.emulators.file_inclusion import simulate_file_inclusion

# 模拟 Flask Request 对象
class MockRequest:
    def __init__(self, args):
        self.args = args

class TestFileInclusion(unittest.TestCase):
    def test_valid_file(self):
        # 测试合法文件路径
        request = MockRequest({'file': 'includes/header.html'})
        response = simulate_file_inclusion(request)
        self.assertEqual(response['status'], 'ok')
        self.assertIn('Mock content of includes/header.html', response['file_content'])

    def test_sensitive_file(self):
        # 测试访问敏感文件
        request = MockRequest({'file': '/etc/passwd'})
        response = simulate_file_inclusion(request)
        self.assertEqual(response['status'], 'blocked')
        self.assertIn('Unauthorized file access', response['reason'])

    def test_empty_file(self):
        # 测试空文件路径
        request = MockRequest({'file': ''})
        response = simulate_file_inclusion(request)
        self.assertEqual(response['status'], 'ok')
        self.assertIn('No file provided', response['file_content'])

    def test_unknown_file(self):
        # 测试未知文件路径
        request = MockRequest({'file': 'random/file.txt'})
        response = simulate_file_inclusion(request)
        self.assertEqual(response['status'], 'blocked')
        self.assertIn('File not recognized', response['reason'])

if __name__ == '__main__':
    unittest.main()
