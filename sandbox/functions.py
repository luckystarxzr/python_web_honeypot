import re
import json
import os
from flask import request
from sandbox.generate import VirtualEnvironment, generate_environment
from modules.logs import log_attack
from sandbox.replacement.getenv import getenv
from sandbox.replacement.ini_get import ini_get
from sandbox.replacement.system import system
from urllib.parse import unquote

# 动态加载命令映射
FUNCTIONS = {
    "ls": "list_files",
    "cat /etc/passwd": "mock_passwd",
    "whoami": "sandbox_user"
}

def load_functions(file_path="data/functions.json"):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Command mapping file {file_path} not found, using default mapping.")
        return FUNCTIONS
    except json.JSONDecodeError:
        print(f"Command mapping file {file_path} format error, using default mapping.")
        return FUNCTIONS

# 动态加载规则
def load_rules():
    # 获取当前文件的目录路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    rules_path = os.path.join(base_dir, 'data', 'rules.json')
    try:
        with open(rules_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Rules file not found at {rules_path}! Using default rules.")
        return {}

# 文件访问检测
def detect_file_access(filepath):
    try:
        env = VirtualEnvironment()  # 初始化虚拟环境
        file_content = env.read_file(filepath)
        if file_content in ["Invalid file path", "File not found"]:
            # 如果文件不存在或访问非法，使用 generate_environment 生成虚拟内容
            file_content = generate_environment(filepath)
            ip_address = request.remote_addr if request else "Unknown IP"
            user_agent = request.headers.get("User-Agent", "Unknown User-Agent")
            log_attack("File Access Blocked", f"IP: {ip_address}, User-Agent: {user_agent}, Unauthorized access to {filepath}, Generated mock content.")
            return {
                "status": "blocked",
                "reason": "Invalid or unauthorized file access",
                "filepath": filepath,
                "mock_content": file_content
            }
        return {
            "status": "ok",
            "content": file_content
        }
    except Exception as e:
        log_attack("Error", f"Exception in file access detection: {e}")
        return {
            "status": "error",
            "reason": "Internal error during file access detection"
        }

# 定义 detect_config_access 函数
def detect_config_access(section, key):
    try:
        # 调用 ini_get 获取配置
        value = ini_get(section, key)
        if value == "Not Found":
            ip_address = "192.168.1.1"  # 模拟 IP 地址
            user_agent = "MockAgent/1.0"  # 模拟 User-Agent
            print(f"Config Access Blocked: IP={ip_address}, User-Agent={user_agent}, Access to config {section}.{key} denied")
            return {
                "status": "blocked",
                "reason": "Configuration not accessible",
                "section": section,
                "key": key
            }
        return {
            "status": "ok",
            "value": value
        }
    except Exception as e:
        print(f"Error: Exception in config access detection: {e}")
        return {
            "status": "error",
            "reason": "Internal error during config access detection"
        }

# 命令注���检测
def detect_command_injection(command):
    try:
        env = VirtualEnvironment()  # 初始化虚拟环境
        result = env.execute_command(command)  # 使用虚拟环境执行命令
        if result["status"] == "error":
            ip_address = request.remote_addr if request else "Unknown IP"
            user_agent = request.headers.get("User-Agent", "Unknown User-Agent")
            log_attack("Command Injection Detected", f"IP: {ip_address}, User-Agent: {user_agent}, Invalid command {command}")
            return {
                "status": "blocked",
                "reason": "Invalid or unauthorized command",
                "command": command
            }
        return {
            "status": "ok",
            "output": result["output"]
        }
    except Exception as e:
        log_attack("Error", f"Exception in command injection detection: {e}")
        return {
            "status": "error",
            "reason": "Internal error during command injection detection"
        }

# 环境变量访问检测
def detect_env_access(variable_name):
    value = getenv(variable_name)
    if value == "Not Found":
        ip_address = request.remote_addr if request else "Unknown IP"
        user_agent = request.headers.get("User-Agent", "Unknown User-Agent")
        log_attack("Environment Access Blocked", f"IP: {ip_address}, User-Agent: {user_agent}, Access to {variable_name} denied")
        return {
            "status": "blocked",
            "reason": "Environment variable not accessible",
            "variable": variable_name
        }
    return {
        "status": "ok",
        "value": value
    }

# 配置文件访问检测
def detect_config_access(section, key):
    try:
        # 调用 ini_get 获取配置
        value = ini_get(section, key)
        if value == "Not Found":
            ip_address = request.remote_addr if request else "Unknown IP"
            user_agent = request.headers.get("User-Agent", "Unknown User-Agent")
            log_attack("Config Access Blocked", f"IP: {ip_address}, User-Agent: {user_agent}, Access to config {section}.{key} denied")
            return {
                "status": "blocked",
                "reason": "Configuration not accessible",
                "section": section,
                "key": key
            }
        return {
            "status": "ok",
            "value": value
        }
    except Exception as e:
        log_attack("Error", f"Exception in config access detection: {e}")
        return {
            "status": "error",
            "reason": "Internal error during config access detection"
        }


# 系统信息访问检测
def detect_system_info_access():
    # 定义要执行的命令
    command = "uname -a"
    info = system(command)
    return {
        "status": "ok",
        "system_info": info
    }

def apply_rule(rule, content):
    """应用规则进行检测"""
    if re.search(rule["patternString"], content, re.IGNORECASE):
        return {
            "matched": True,
            "rule_id": rule["id"],
            "description": rule["patternDescription"],
            "severity": rule["severity"],
            "action": rule["action"]
        }
    return {"matched": False}

def detect_attack(request_data, rules):
    # 添加输入验证
    if not isinstance(request_data, dict):
        return {
            "status": "error",
            "reason": "Invalid request data format"
        }
    
    ip_address = request.remote_addr if request else "Unknown IP"
    user_agent = request.headers.get("User-Agent", "Unknown User-Agent")

    # 检查每个可能的攻击向量
    for key, value in request_data.items():
        if isinstance(value, str):
            for rule in rules:
                result = apply_rule(rule, value)
                if result["matched"]:
                    log_attack(
                        rule["patternDescription"],
                        f"Matched pattern in {key}: {value}",
                        request
                    )
                    return {
                        "status": "blocked" if rule["action"] == "block" else "logged",
                        "rule_id": rule["id"],
                        "description": rule["patternDescription"],
                        "severity": rule["severity"],
                        "matched_content": value
                    }

    return {
        "status": "ok",
        "message": "No attack detected"
    }

