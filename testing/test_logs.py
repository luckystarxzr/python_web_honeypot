import unittest
from unittest.mock import MagicMock
from app import app
from modules.logs import log_attack, get_logs


class TestLogs(unittest.TestCase):
    log_file = "logs/attacks.log"  # 日志文件路径
    @classmethod
    def setUpClass(cls):
        """初始化 Flask 测试客户端"""
        cls.client = app.test_client()
        cls.client.testing = True
    def setUp(self):
        """确保每个测试用例前清空日志文件"""
        with open(self.log_file, "w") as f:
            f.truncate(0)  # 清空日志文件

    def tearDown(self):
        """每个测试用例后清空日志文件"""
        with open(self.log_file, "w") as f:
            f.truncate(0)  # 清空日志文件

    def test_log_attack(self):
        """测试 log_attack 函数是否正确记录日志"""
        # 模拟请求对象
        mock_request = MagicMock()
        mock_request.remote_addr = "127.0.0.1"
        mock_request.headers = {"User-Agent": "Test Browser"}

        # 调用 log_attack
        log_attack("Command Injection", "Detected malicious command: ls; rm -rf /", mock_request)

        # 读取日志文件内容
        with open(self.log_file, "r") as f:
            logs = f.readlines()

        print(f"Debug: Current logs - {logs}")  # 调试输出
        logs = [log for log in logs if "Database error" not in log]  # 过滤非测试日志
        self.assertEqual(len(logs), 1)  # 验证日志条目数
        self.assertIn("Command Injection", logs[0])  # 验证日志内容
        self.assertIn("127.0.0.1", logs[0])
        self.assertIn("Test Browser", logs[0])
        self.assertIn("Detected malicious command: ls; rm -rf /", logs[0])

    def test_get_logs(self):
        """测试 get_logs 函数是否正确解析日志"""
        # 写入模拟日志
        with open(self.log_file, "w") as f:
            f.write("2024-12-27 10:00:00 - INFO - Attack type: SQL Injection, IP: 192.168.1.1, User-Agent: Test API Client, Details: SELECT * FROM users\n")
            f.write("2024-12-27 10:05:00 - INFO - Attack type: XSS, IP: 127.0.0.1, User-Agent: Browser, Details: <script>alert(1)</script>\n")

        # 调用 get_logs
        logs = get_logs()
        print(f"Debug: Parsed logs - {logs}")  # 调试输出

        # 验证日志条目解析
        self.assertEqual(len(logs), 2)  # 验证解析条目数
        self.assertEqual(logs[0]["type"], "SQL Injection")
        self.assertIn("SELECT * FROM users", logs[0]["details"])
        self.assertEqual(logs[1]["type"], "XSS")
        self.assertIn("<script>alert(1)</script>", logs[1]["details"])

    def test_logs_page_pagination(self):
        """测试日志页面分页功能"""
        # 模拟多条日志记录
        with open('logs/attacks.log', 'w') as file:
            for i in range(25):
                file.write(
                    f"2024-12-27 10:00:{i:02d} - INFO - Attack type: Test Attack {i}, Details: Log details {i}\n")

        # 请求第一页
        response = self.client.get("/logs?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Page 1 of 3", response.data)  # 检查分页内容
        self.assertIn(b"Test Attack 0", response.data)  # 检查第一页日志内容
        self.assertIn(b"Test Attack 9", response.data)  # 检查第一页日志内容

        # 请求第二页
        response = self.client.get("/logs?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Page 2 of 3", response.data)
        self.assertIn(b"Test Attack 10", response.data)
        self.assertIn(b"Test Attack 19", response.data)

        # 请求第三页
        response = self.client.get("/logs?page=3")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Page 3 of 3", response.data)
        self.assertIn(b"Test Attack 20", response.data)
        self.assertIn(b"Test Attack 24", response.data)


if __name__ == "__main__":
    unittest.main()
