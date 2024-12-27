def getenv(variable):
    # Mock environment variable access
    environment = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": "/root",
    }
    return environment.get(variable, "Unknown variable")
