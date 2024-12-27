import logging
import os
from flask import has_request_context, request

# 确保日志目录存在
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "attacks.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setUp(self):
    """确保日志文件在每次测试前被清空"""
    with open(self.log_file, "w") as f:
        f.truncate(0)  # 清空文件内容
def log_attack(attack_type, details, request=None):
    """记录攻击信息到日志文件和数据库"""
    ip_address = request.remote_addr if request else "Unknown IP"
    user_agent = request.headers.get("User-Agent", "Unknown User-Agent") if request else "Unknown User-Agent"
    print(f"Debug: log_attack called with: {attack_type}, {details}")
    # 记录到日志文件
    logging.info(
        f"Attack type: {attack_type}, IP: {ip_address}, User-Agent: {user_agent}, Details: {details}"
    )
    
    # 记录到数据库
    from modules.database import log_attack_to_db
    log_attack_to_db(
        ip_address,
        user_agent,
        attack_type,
        details,
        "blocked",
        f"Attack detected from {ip_address}"
    )

def get_logs():
    logs = []
    try:
        with open(LOG_FILE, "r") as file:
            for line in file:
                print(f"Debug: Raw log line - {line.strip()}")  # 添加调试信息
                parts = line.strip().split(" - ", 2)
                if len(parts) == 3:
                    timestamp_str, level, message = parts
                    try:
                        message_parts = message.split(", ")
                        if "Attack type:" in message:
                            attack_type = message_parts[0].replace("Attack type: ", "")
                            details = message_parts[-1].replace("Details: ", "")
                            logs.append({
                                "timestamp": timestamp_str,
                                "type": attack_type,
                                "details": details
                            })
                    except Exception as e:
                        print(f"Error parsing log message: {message}, Error: {e}")
    except FileNotFoundError:
        print(f"Log file not found: {LOG_FILE}")
    except Exception as e:
        print(f"Error reading log file: {e}")

    # 如果日志为空，返回占位消息
    if not logs:
        logs.append({"timestamp": "N/A", "type": "N/A", "details": "No logs available"})

    print(f"Debug: Parsed logs - {logs}")  # 添加调试信息
    return logs
