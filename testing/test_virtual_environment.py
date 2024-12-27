import unittest
from sandbox.generate import VirtualEnvironment

class TestVirtualEnvironment(unittest.TestCase):

    def setUp(self):
        self.env = VirtualEnvironment()

    def test_execute_command_valid(self):
        result = self.env.execute_command("ls")
        self.assertEqual(result["status"], "success")
        self.assertIn("file1.txt", result["output"])

    def test_execute_command_invalid(self):
        result = self.env.execute_command("rm -rf /")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["output"], "Command not recognized")

    def test_execute_command_empty(self):
        result = self.env.execute_command("")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["output"], "Invalid command")

    def test_read_file_valid(self):
        result = self.env.read_file("/etc/passwd")
        self.assertIn("root:x:0:0:root:/root:/bin/bash", result)

    def test_read_file_invalid_path(self):
        result = self.env.read_file("../../etc/passwd")
        self.assertEqual(result, "Invalid file path")

    def test_read_file_not_found(self):
        result = self.env.read_file("/nonexistent/file")
        self.assertEqual(result, "File not found")

    def test_xss_valid(self):
        payload = "<h1>Hello World</h1>"
        result = self.env.xss(payload)
        self.assertEqual(result["status"], "ok")
        self.assertIn("Rendered content", result["output"])

    def test_xss_blocked(self):
        payload = "<script>alert('XSS')</script>"
        result = self.env.xss(payload)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("Potential XSS detected", result["reason"])

    def test_sql_injection_valid(self):
        query = "SELECT * FROM users"
        result = self.env.sql_injection(query)
        self.assertEqual(result["status"], "ok")
        self.assertIn("Query executed", result["output"])

    def test_sql_injection_blocked(self):
        query = "SELECT * FROM users WHERE ' OR 1=1 --"
        result = self.env.sql_injection(query)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("Potential SQL Injection detected", result["reason"])

    def test_csrf_valid(self):
        referer = "https://trusted-site.com"
        expected_referer = "https://trusted-site.com"
        result = self.env.csrf(referer, expected_referer)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"], "Request validated")

    def test_csrf_blocked(self):
        referer = "https://malicious-site.com"
        expected_referer = "https://trusted-site.com"
        result = self.env.csrf(referer, expected_referer)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("Potential CSRF detected", result["reason"])

    def test_directory_traversal_valid(self):
        filepath = "/home/user/documents/file.txt"
        result = self.env.directory_traversal(filepath)
        self.assertEqual(result["status"], "ok")
        self.assertIn("Accessed file", result["output"])

    def test_directory_traversal_blocked(self):
        filepath = "../../etc/passwd"
        result = self.env.directory_traversal(filepath)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("Potential Directory Traversal detected", result["reason"])


if __name__ == "__main__":
    unittest.main()
