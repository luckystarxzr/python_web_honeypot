import random
#随机生成数据
def generate_environment(file_path):
    if not file_path or ".." in file_path:
        return "Invalid file path"
    content_type = random.choice(["text", "binary", "log"])
    if content_type == "text":
        return f"Mock text content of {file_path}: {random.randint(1000, 9999)}"
    elif content_type == "binary":
        return f"Mock binary data of {file_path}: {random.getrandbits(8)}"
    elif content_type == "log":
        return f"Log entry for {file_path}: Timestamp {random.randint(1000000000, 9999999999)}"
class VirtualEnvironment:
    def __init__(self):
        self.filesystem = {
            "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash",
            "/etc/shadow": "Permission denied",
            "../../etc/passwd": "Access blocked for security reasons"
        }
        self.commands = {
            "ls": "file1.txt\nfile2.txt\n",
            "whoami": "sandbox_user",
            "cat /etc/passwd": self.filesystem["/etc/passwd"]
        }

    def execute_command(self, command):
        if not command or ".." in command:
            return {
                "status": "error",
                "output": "Invalid command"
            }
        if command in self.commands:
            return {
                "status": "success",
                "output": self.commands[command]
            }
        return {
            "status": "error",
            "output": "Command not recognized"
        }

    def read_file(self, filepath):
        if not filepath or ".." in filepath:
            return "Invalid file path"
        return self.filesystem.get(filepath, "File not found")

    def xss(self, payload):
        if "<script>" in payload or "javascript:" in payload or "onerror" in payload:
            return {
                "status": "blocked",
                "reason": "Potential XSS detected",
                "payload": payload
            }
        return {
            "status": "ok",
            "output": f"Rendered content: {payload}"
        }

    def sql_injection(self, query):
        sql_keywords = ["' OR 1=1", "UNION", "--", "DROP"]
        if any(keyword in query.upper() for keyword in sql_keywords):
            return {
                "status": "blocked",
                "reason": "Potential SQL Injection detected",
                "query": query
            }
        return {
            "status": "ok",
            "output": f"Query executed: {query}"
        }

    def csrf(self, referer, expected_referer):
        if referer != expected_referer:
            return {
                "status": "blocked",
                "reason": "Potential CSRF detected",
                "referer": referer
            }
        return {
            "status": "ok",
            "output": "Request validated"
        }

    def directory_traversal(self, filepath):
        if ".." in filepath or filepath.startswith("/etc"):
            return {
                "status": "blocked",
                "reason": "Potential Directory Traversal detected",
                "filepath": filepath
            }
        return {
            "status": "ok",
            "output": f"Accessed file: {filepath}"
        }

