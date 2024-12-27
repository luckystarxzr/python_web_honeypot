import unittest
from unittest.mock import MagicMock, patch
from modules.emulators.command_injection import simulate_command_injection


class TestCommandInjection(unittest.TestCase):
    def setUp(self):
        # 创建一个模拟的 request 对象
        self.mock_request = MagicMock()
        self.mock_request.args = MagicMock()
        self.mock_request.args.get = MagicMock()

        # 设置模拟的请求属性
        self.mock_request.remote_addr = "127.0.0.1"
        self.mock_request.headers = {"User-Agent": "Test Browser"}

    @patch('modules.emulators.command_injection.log_attack')  # 修正路径
    def test_no_command(self, mock_log_attack):
        self.mock_request.args.get.return_value = ''
        result = simulate_command_injection(self.mock_request)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['output'], 'No command executed')
        mock_log_attack.assert_not_called()

    @patch('modules.emulators.command_injection.log_attack')  # 修正路径
    def test_allowed_command(self, mock_log_attack):
        self.mock_request.args.get.return_value = 'ls'
        result = simulate_command_injection(self.mock_request)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['output'], 'Executed: ls')
        mock_log_attack.assert_not_called()

    @patch('modules.emulators.command_injection.log_attack')  # 修正路径
    def test_malicious_command(self, mock_log_attack):
        self.mock_request.args.get.return_value = 'ls; rm -rf /'
        result = simulate_command_injection(self.mock_request)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['output'], 'Invalid command detected')
        mock_log_attack.assert_called_once_with(
            "Command Injection",
            "Malicious command detected: ls; rm -rf /",
            self.mock_request
        )

    @patch('modules.emulators.command_injection.log_attack')  # 修正路径
    def test_unknown_command(self, mock_log_attack):
        self.mock_request.args.get.return_value = 'cat /etc/passwd'
        result = simulate_command_injection(self.mock_request)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['output'], 'Command not recognized')
        mock_log_attack.assert_called_once_with(
            "Command Injection",
            "Unknown command received: cat /etc/passwd",
            self.mock_request
        )

    @patch('modules.emulators.command_injection.log_attack')  # 修正路径
    def test_command_with_pipe(self, mock_log_attack):
        self.mock_request.args.get.return_value = 'ls | grep test'
        result = simulate_command_injection(self.mock_request)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['output'], 'Invalid command detected')
        mock_log_attack.assert_called_once_with(
            "Command Injection",
            "Malicious command detected: ls | grep test",
            self.mock_request
        )

    @patch('modules.emulators.command_injection.log_attack')  # 修正路径
    def test_command_with_path_traversal(self, mock_log_attack):
        self.mock_request.args.get.return_value = 'ls ../../../etc'
        result = simulate_command_injection(self.mock_request)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['output'], 'Invalid command detected')
        mock_log_attack.assert_called_once_with(
            "Command Injection",
            "Malicious command detected: ls ../../../etc",
            self.mock_request
        )


if __name__ == '__main__':
    unittest.main()
