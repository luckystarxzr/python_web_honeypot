import json
import os
import unittest
from app import app


class TestWebFunctionality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.client.testing = True

        # 动态创建 rules.json 文件
        os.makedirs('data', exist_ok=True)
        with open('data/rules.json', 'w', encoding='utf-8') as file:
            json.dump({
                "command_injection": ["ls", "whoami"],
                "directory_traversal": ["../", "..\\", "/etc"],
                "file_inclusion": ["includes/header.html"],
                "sql_injection": ["SELECT", "DROP", "UNION"],
                "xss": ["<script>", "</script>"]
            }, file)

        os.makedirs('logs', exist_ok=True)
        with open('logs/attacks.log', 'w') as file:
            file.write("2024-12-27 10:30:00 - INFO - Attack type: SQL Injection, Details: SELECT * FROM users\n")
            file.write("2024-12-27 10:35:00 - INFO - Attack type: XSS, Details: <script>alert(1)</script>\n")
    @classmethod
    def tearDownClass(cls):
        # 删除测试生成的 rules.json 文件
        if os.path.exists('data/rules.json'):
            os.remove('data/rules.json')
            # 删除测试生成的日志文件
        if os.path.exists('logs/attacks.log'):
            os.remove('logs/attacks.log')

    def test_home_page(self):
        """测试首页加载"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome", response.data)  # 检查首页内容是否正确

    def test_command_injection_page(self):
        """测试命令注入页面"""
        response = self.client.get("/command_injection")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Command Injection Test", response.data)

    def test_command_injection_post(self):
        """测试命令注入功能"""
        response = self.client.post("/command_injection", data={"cmd": "ls"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"status", response.data)  # 返回的 JSON 包含 'status'

    def test_csrf_page(self):
        """测试 CSRF 页面"""
        response = self.client.get("/csrf")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CSRF Test", response.data)

    def test_csrf_post(self):
        """测试 CSRF 功能"""
        response = self.client.post("/csrf")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"status", response.data)  # 返回的 JSON 包含 'status'

    def test_directory_traversal_page(self):
        """测试目录遍历页面"""
        response = self.client.get("/directory_traversal")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Directory Traversal", response.data)

    def test_directory_traversal_post(self):
        """测试目录遍历功能"""
        response = self.client.post("/directory_traversal", data={"path": "../etc/passwd"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"status", response.data)

    def test_file_inclusion_page(self):
        """测试文件包含页面"""
        response = self.client.get("/file_inclusion")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"File Inclusion", response.data)

    def test_file_inclusion_post(self):
        """测试文件包含功能"""
        response = self.client.post("/file_inclusion", data={"file": "includes/header.html"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"status", response.data)

    def test_sql_injection_page(self):
        """测试 SQL 注入页面"""
        response = self.client.get("/sql_injection")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SQL Injection Test", response.data)

    def test_sql_injection_post(self):
        """测试 SQL 注入功能"""
        response = self.client.post("/sql_injection", data={"query": "SELECT * FROM users"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"status", response.data)

    def test_xss_page(self):
        """测试 XSS 页面"""
        response = self.client.get("/xss")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"XSS Test", response.data)

    def test_xss_post(self):
        """测试 XSS 功能"""
        response = self.client.post("/xss", data={"payload": "<script>alert('XSS')</script>"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"status", response.data)

    def test_logs_page(self):
        """测试日志页面是否正确返回"""
        response = self.client.get("/logs")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Attack Logs", response.data)  # 检查页面标题
        self.assertIn(b"SQL Injection", response.data)  # 检查日志内容
        self.assertIn(b"XSS", response.data)  # 检查日志内容

    def test_404_page(self):
        """测试 404 错误页面"""
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page Not Found", response.data)


if __name__ == "__main__":
    unittest.main()
