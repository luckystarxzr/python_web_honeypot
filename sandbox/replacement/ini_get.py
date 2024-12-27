def ini_get(section, key):
    # 模拟配置文件内容
    config = {
        "database": {
            "username": "admin",
            "password": "12345"
        }
    }
    # 尝试获取指定的配置
    return config.get(section, {}).get(key, "Not Found")