from modules.logs import log_attack
from sandbox.generate import generate_environment


def simulate_file_inclusion(request):
    # 从请求中获取文件路径
    file_path = request.args.get('file', '').strip()

    # 定义合法文件路径的白名单
    allowed_paths = ["includes/header.html", "includes/footer.html"]

    # 空路径应返回 'ok'
    if not file_path:
        return {
            "status": "ok",
            "file_content": "No file provided"
        }

    # 标准化路径并检查非法路径（敏感文件或目录遍历）
    if file_path.startswith("/etc") or ".." in file_path:
        log_attack("File Inclusion", f"Unauthorized access attempt to: {file_path}")
        return {
            "status": "blocked",
            "reason": "Unauthorized file access",
            "file": file_path
        }

    # 检查路径是否在白名单中
    if file_path in allowed_paths:
        return {
            "status": "ok",
            "file_content": f"Mock content of {file_path}"
        }

    # 未知路径
    return {
        "status": "blocked",
        "reason": "File not recognized",
        "file": file_path
    }
