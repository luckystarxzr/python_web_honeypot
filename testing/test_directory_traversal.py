import unittest
from unittest.mock import patch, MagicMock
from modules.emulators.directory_traversal import simulate_directory_traversal


class TestDirectoryTraversal(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.args = MagicMock()
        self.mock_request.args.get = MagicMock()

        self.mock_request.remote_addr = "127.0.0.1"
        self.mock_request.headers = {"User-Agent": "Test Browser"}

    @patch('modules.emulators.directory_traversal.log_attack')
    def test_no_file_accessed(self, mock_log_attack):
        self.mock_request.args.get.return_value = ''
        response = simulate_directory_traversal(self.mock_request)
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["message"], "No file accessed")
        mock_log_attack.assert_not_called()

    @patch('modules.emulators.directory_traversal.log_attack')
    def test_valid_file_access(self, mock_log_attack):
        self.mock_request.args.get.return_value = 'valid_file.txt'
        response = simulate_directory_traversal(self.mock_request)
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["file_content"], "Simulated file content")
        mock_log_attack.assert_not_called()

    @patch('modules.emulators.directory_traversal.log_attack')
    def test_directory_traversal_attempt(self, mock_log_attack):
        self.mock_request.args.get.return_value = '../etc/passwd'
        response = simulate_directory_traversal(self.mock_request)
        self.assertEqual(response["status"], "blocked")
        self.assertEqual(response["reason"], "Directory Traversal detected")
        self.assertEqual(response["file"], "../etc/passwd")
        mock_log_attack.assert_called_once_with(
            "Directory Traversal",
            "Attempt to access: ../etc/passwd"
        )

    @patch('modules.emulators.directory_traversal.log_attack')
    def test_url_encoded_directory_traversal_attempt(self, mock_log_attack):
        self.mock_request.args.get.return_value = '%2E%2E%2Fetc%2Fpasswd'
        response = simulate_directory_traversal(self.mock_request)
        self.assertEqual(response["status"], "blocked")
        self.assertEqual(response["reason"], "Directory Traversal detected")
        self.assertEqual(response["file"], "../etc/passwd")
        mock_log_attack.assert_called_once_with(
            "Directory Traversal",
            "Attempt to access: ../etc/passwd"
        )

    @patch('modules.emulators.directory_traversal.log_attack')
    def test_absolute_path_attempt(self, mock_log_attack):
        self.mock_request.args.get.return_value = '/etc/passwd'
        response = simulate_directory_traversal(self.mock_request)
        self.assertEqual(response["status"], "blocked")
        self.assertEqual(response["reason"], "Directory Traversal detected")
        self.assertEqual(response["file"], "/etc/passwd")
        mock_log_attack.assert_called_once_with(
            "Directory Traversal",
            "Attempt to access: /etc/passwd"
        )

    @patch('modules.emulators.directory_traversal.log_attack')
    def test_normalized_path_attack(self, mock_log_attack):
        self.mock_request.args.get.return_value = 'folder/../../etc/passwd'
        response = simulate_directory_traversal(self.mock_request)
        self.assertEqual(response["status"], "blocked")
        self.assertEqual(response["reason"], "Directory Traversal detected")
        self.assertEqual(response["file"], "folder/../../etc/passwd")
        mock_log_attack.assert_called_once_with(
            "Directory Traversal",
            "Attempt to access: folder/../../etc/passwd"
        )

    @patch('modules.emulators.directory_traversal.log_attack')
    def test_valid_relative_path(self, mock_log_attack):
        self.mock_request.args.get.return_value = 'folder/valid_file.txt'
        response = simulate_directory_traversal(self.mock_request)
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["file_content"], "Simulated file content")
        mock_log_attack.assert_not_called()


if __name__ == "__main__":
    unittest.main()
