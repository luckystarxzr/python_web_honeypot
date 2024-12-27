import urllib.parse
import os
from modules.logs import log_attack

def simulate_directory_traversal(request):
    file_path = request.args.get('file', '').strip()

    if not file_path:
        return {
            "status": "ok",
            "message": "No file accessed"
        }

    # 解码 URL 编码的路径
    decoded_path = urllib.parse.unquote(file_path)

    # 标准化路径
    normalized_path = os.path.normpath(decoded_path)

    # 调试输出
    print(f"Debug: Decoded path: {decoded_path}, Normalized path: {normalized_path}, Is absolute: {os.path.isabs(decoded_path)}")

    # 检测是否尝试访问上层目录或使用绝对路径
    if ".." in normalized_path or os.path.isabs(decoded_path) or decoded_path.startswith('/'):
        log_attack("Directory Traversal", f"Attempt to access: {decoded_path}")
        return {
            "status": "blocked",
            "reason": "Directory Traversal detected",
            "file": decoded_path
        }

    return {
        "status": "ok",
        "file_content": "Simulated file content"
    }
