from modules.logs import log_attack

def simulate_csrf(request):
    try:
        referer = request.headers.get("Referer", "")
        origin = request.headers.get("Origin", "")
        if not referer or "evil.com" in referer or "evil.com" in origin:
            log_attack("CSRF", f"Possible CSRF attack detected")
            return {
                "status": "blocked",
                "reason": "CSRF attack detected"
            }
        return {
            "status": "ok",
            "message": "No CSRF detected"
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": f"Failed to process CSRF detection: {str(e)}"
        }
