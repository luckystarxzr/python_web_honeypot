from modules.logs import log_attack
import re

def simulate_xss(request):
    payload = request.args.get('payload', '').strip()

    if not payload:
        return {
            "status": "ok",
            "message": "No payload detected"
        }

    # 定义常见 XSS 模式
    xss_patterns = [
        r"(?i)<script.*?>.*?</script.*?>",
        r"(?i)(onerror|onload|onclick|onmouseover)\s*=",
        r"(?i)<img\s+.*?src\s*=.*?javascript:.*?>"
    ]

    for pattern in xss_patterns:
        if re.search(pattern, payload):
            log_attack("XSS", f"Malicious script detected: {payload}")
            return {
                "status": "blocked",
                "reason": "XSS attack detected",
                "script": payload
            }

    return {
        "status": "ok",
        "message": "No malicious script detected"
    }