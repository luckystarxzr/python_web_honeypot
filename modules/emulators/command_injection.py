from modules.logs import log_attack

def simulate_command_injection(request):
    command = request.args.get('cmd', '').strip()

    print(f"Debug: Received command: {command}")  # 调试输入

    if not command:
        return {
            "status": "ok",
            "output": "No command executed"
        }

    allowed_commands = ["ls", "whoami"]

    if command in allowed_commands:
        return {
            "status": "success",
            "output": f"Executed: {command}"
        }

    if ";" in command or "|" in command or "&&" in command or ".." in command:
        print(f"Debug: Detected malicious command: {command}")  # 调试恶意命令
        log_attack("Command Injection", f"Malicious command detected: {command}", request)
        return {
            "status": "blocked",
            "output": "Invalid command detected"
        }

    print(f"Debug: Unknown command received: {command}")  # 调试未知命令
    log_attack("Command Injection", f"Unknown command received: {command}", request)
    return {
        "status": "blocked",
        "output": "Command not recognized"
    }
