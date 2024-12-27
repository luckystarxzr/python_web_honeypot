import unittest
import os
import mysql.connector
from datetime import datetime
from threading import Thread
from time import sleep
from modules.database import extract_ip, read_new_attacks, save_attacks_to_db, monitor_logs

# 测试数据库配置
TEST_DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "honeypot_db"
}

TEST_LOG_FILE = "attacks.log"


class TestHoneypotLog(unittest.TestCase):
    def setUp(self):
        """初始化测试环境"""
        # 初始化测试数据库
        conn = mysql.connector.connect(**TEST_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS attacks")
        cursor.execute('''
            CREATE TABLE attacks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(255),
                user_agent VARCHAR(255),
                attack_type VARCHAR(255),
                payload TEXT,
                status VARCHAR(50),
                details TEXT
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

        # 创建测试日志文件
        with open(TEST_LOG_FILE, "w") as f:
            f.write(
                "2024-12-26 12:00:00 - INFO - XSS: IP: 192.168.1.1, User-Agent: TestAgent, Payload: <script>alert(1)</script>\n"
                "2024-12-26 12:05:00 - INFO - SQL Injection: IP: 192.168.1.2, User-Agent: TestAgent, Query: SELECT * FROM users WHERE 1=1\n"
            )

    def tearDown(self):
        """清理测试环境"""
        # 删除测试数据库表
        conn = mysql.connector.connect(**TEST_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS attacks")
        conn.commit()
        cursor.close()
        conn.close()

        # 删除测试日志文件
        if os.path.exists(TEST_LOG_FILE):
            os.remove(TEST_LOG_FILE)

    def test_extract_ip(self):
        """测试 IP 提取功能"""
        details = "IP: 192.168.1.1, User-Agent: TestAgent, Payload: <script>alert(1)</script>"
        ip = extract_ip(details)
        self.assertEqual(ip, "192.168.1.1")

    def test_read_new_attacks(self):
        """测试日志解析功能"""
        attacks, processed_lines = read_new_attacks(TEST_LOG_FILE, 0)
        self.assertEqual(len(attacks), 2)
        self.assertEqual(attacks[0]["attack_type"], "XSS")
        self.assertEqual(attacks[0]["ip"], "192.168.1.1")
        self.assertEqual(attacks[1]["attack_type"], "SQL Injection")
        self.assertEqual(attacks[1]["ip"], "192.168.1.2")

    def test_save_attacks_to_db(self):
        """测试将攻击信息保存到数据库"""
        attacks = [
            {
                "timestamp": datetime(2024, 12, 26, 12, 0, 0),
                "attack_type": "XSS",
                "details": "IP: 192.168.1.1, User-Agent: TestAgent, Payload: <script>alert(1)</script>",
                "ip": "192.168.1.1"
            },
            {
                "timestamp": datetime(2024, 12, 26, 12, 5, 0),
                "attack_type": "SQL Injection",
                "details": "IP: 192.168.1.2, User-Agent: TestAgent, Query: SELECT * FROM users WHERE 1=1",
                "ip": "192.168.1.2"
            }
        ]
        save_attacks_to_db(attacks)

        # 检查数据库内容
        conn = mysql.connector.connect(**TEST_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM attacks")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 2)
        cursor.close()
        conn.close()

    def test_monitor_logs(self):
        """测试日志监控功能"""
        # 启动日志监控线程
        thread = Thread(target=monitor_logs, args=(TEST_LOG_FILE, 2), daemon=True)
        thread.start()

        # 模拟新日志写入
        sleep(1)
        with open(TEST_LOG_FILE, "a") as f:
            f.write(
                "2024-12-26 12:10:00 - INFO - Directory Traversal: IP: 192.168.1.3, User-Agent: TestAgent, Path: ../../etc/passwd\n"
            )

        # 等待监控线程处理
        sleep(5)  # 增加等待时间，确保日志被处理

        # 检查数据库内容
        conn = mysql.connector.connect(**TEST_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM attacks")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)  # 检查是否检测到新日志
        cursor.close()
        conn.close()


if __name__ == "__main__":
    unittest.main()
