import re
from modules.logs import log_attack

def simulate_sql_injection(request):
    query = request.args.get('query', '').strip()

    if not query:
        return {
            "status": "ok",
            "query": "No query provided"
        }

    # 定义更精确的 SQL 注入模式
    sql_patterns = [
        r"(?i)(DROP TABLE|UNION SELECT|INSERT INTO|DELETE FROM|UPDATE SET)",
        r"(?i)(\sOR\s1=1|';--|\";--|';|\";)"
    ]

    # 检查是否匹配恶意 SQL 模式
    for pattern in sql_patterns:
        if re.search(pattern, query):
            log_attack("SQL Injection", f"Malicious query detected: {query}")
            return {
                "status": "blocked",
                "reason": "SQL Injection detected",
                "query": query
            }

    # 未匹配任何恶意模式，合法查询
    return {
        "status": "ok",
        "query": query
    }
