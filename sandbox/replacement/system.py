def system(command):
    # Mock the system call
    if command == "whoami":
        return "sandbox_user"
    elif command == "uptime":
        return " 10:15:22 up 5 days,  3:14,  2 users,  load average: 0.15, 0.10, 0.08"
    elif command == "df -h":
        return "Filesystem  Size  Used Avail Use% Mounted on\n/dev/sda1        50G   20G   30G  40% /"
    else:
        return f"Command '{command}' not found."
