import os
import logging
import mysql.connector
from datetime import datetime
from time import sleep
from threading import Thread

# 确保日志目录存在
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "attacks.log")

# 配置日志记录
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 数据库相关设置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "honeypot_db"
}

# 初始化数据库
def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS attacks (
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
    # 创建请求日志表
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS logs (
             id INT AUTO_INCREMENT PRIMARY KEY,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
             ip_address VARCHAR(255),
             user_agent VARCHAR(255),
             url VARCHAR(2083),
             method VARCHAR(10),
             status_code INT,
             response_time FLOAT
         )
     ''')
    conn.commit()
    cursor.close()
    conn.close()
def log_attack_to_db(ip, user_agent, attack_type, payload, status, details):
    """存储攻击日志到数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = '''
            INSERT INTO attacks (ip_address, user_agent, attack_type, payload, status, details)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (ip, user_agent, attack_type, payload, status, details))
        conn.commit()
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
# 从日志文件读取攻击信息
def read_new_attacks(log_file, processed_lines):
    attacks = []
    if not os.path.exists(log_file):
        print("Log file does not exist.")
        return attacks, processed_lines

    with open(log_file, "r") as log_file:
        lines = log_file.readlines()
        new_lines = lines[processed_lines:]  # 读取尚未处理的日志行
        for line in new_lines:
            try:
                # 解析日志行
                parts = line.split(" - ", 2)  # 分割日志行
                if len(parts) < 3:
                    print(f"Invalid log format: {line.strip()}")
                    continue

                timestamp, level, message = parts
                attack_type, details = message.strip().split(": ", 1)
                ip = extract_ip(details)  # 从日志详情中提取 IP 地址
                attacks.append({
                    "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                    "attack_type": attack_type,
                    "details": details,
                    "ip": ip or "Unknown"  # 如果无法提取 IP，填入默认值
                })
            except ValueError:
                print(f"Failed to parse log line: {line.strip()}")
                continue

    return attacks, len(lines)

# 从日志详情中提取 IP 地址
def extract_ip(details):
    import re
    match = re.search(r"IP:\s*(\d+\.\d+\.\d+\.\d+)", details)
    return match.group(1) if match else None

# 将攻击信息保存到数据库
def save_attacks_to_db(attacks):
    if not attacks:
        return

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for attack in attacks:
        cursor.execute('''
            INSERT INTO attacks (timestamp, ip, attack_type, details)
            VALUES (%s, %s, %s, %s)
        ''', (attack['timestamp'], attack['ip'], attack['attack_type'], attack['details']))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved {len(attacks)} new attacks to the database.")

# 自动化任务：定期检查日志文件并保存攻击信息
def monitor_logs(log_file, interval=10):
    processed_lines = 0  # 记录已处理的日志行数
    while True:
        try:
            # 读取新攻击信息
            attacks, processed_lines = read_new_attacks(log_file, processed_lines)

            # 保存攻击信息到数据库
            if attacks:
                save_attacks_to_db(attacks)

        except Exception as e:
            logging.error(f"Error while monitoring logs: {str(e)}")

        # 每隔指定时间检查一次日志文件
        sleep(interval)

# 单独启动监控日志任务
def start_monitoring(log_file, interval=10):
    thread = Thread(target=monitor_logs, args=(log_file, interval), daemon=True)
    thread.start()
    print("Log monitoring started in the background.")

# 初始化并启动
if __name__ == "__main__":
    # 初始化数据库
    init_db()

    # 启动日志监控
    start_monitoring(LOG_FILE)

    # 主线程继续运行其他任务
    while True:
        print("Main application running... Press Ctrl+C to stop.")
        sleep(30)
