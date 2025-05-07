Web 安全检测与蜜罐系统
项目概述
Web 安全检测与蜜罐系统是一个基于 Flask 的 Web 应用程序，旨在模拟和检测常见的 Web 安全威胁，包括命令注入、跨站请求伪造（CSRF）、目录遍历、文件包含、SQL 注入和跨站脚本（XSS）攻击。该系统通过规则匹配、正则表达式和虚拟环境，识别潜在的恶意行为，并将攻击信息记录到日志文件和 MySQL 数据库中，供后续分析。系统提供交互式 Web 界面，允许用户测试攻击场景、查看检测结果和浏览攻击日志。
功能特性

攻击模拟与检测：
支持检测命令注入、CSRF、目录遍历、文件包含、SQL 注入和 XSS 攻击。
使用正则表达式和规则匹配（rules.json）识别恶意输入。
虚拟环境（VirtualEnvironment）模拟文件系统和命令执行，防止真实系统受损。


日志记录：
攻击信息记录到日志文件（logs/attacks.log）和 MySQL 数据库。
包含时间戳、IP 地址、用户代理、攻击类型和详细描述。


数据库支持：
使用 MySQL 存储攻击日志和请求日志，支持查询和分析。
自动初始化数据库表（attacks 和 logs）。


日志监控：
后台线程定期扫描日志文件，将新攻击信息同步到数据库。


Web 界面：
提供交互式页面（templates/），支持测试攻击场景和查看结果。
日志页面（/logs）支持分页浏览历史攻击记录。


虚拟环境：
模拟文件系统（/etc/passwd 等）和命令（ls、whoami），生成伪装内容。
防止非法访问敏感文件或执行危险命令。


错误处理：
自定义 404 页面，提升用户体验。


配置管理：
通过 config.py 支持开发和生产环境配置。
动态加载规则（rules.json）和命令映射（functions.json）。



技术栈

后端：
Python 3.6+
Flask：Web 框架
MySQL Connector：数据库连接
Logging：日志记录
Regular Expressions (re)：恶意模式检测
Threading：异步日志监控


前端：
HTML/CSS/JavaScript
Jinja2：模板引擎


数据库：
MySQL：存储攻击和请求日志


数据文件：
JSON：规则（rules.json）和命令映射（functions.json）


其他：
urllib.parse：URL 解码
os：路径规范化



安装与配置
环境要求

Python 3.6 或更高版本
MySQL 5.7 或更高版本
必要的 Python 库（见 requirements.txt）

安装步骤

克隆项目：
git clone <repository-url>
cd web-security-honeypot


创建虚拟环境：
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


安装依赖：
pip install -r requirements.txt

示例 requirements.txt：
flask==2.0.1
mysql-connector-python==8.0.27


配置 MySQL 数据库：

确保 MySQL 服务运行。
创建数据库 honeypot_db：CREATE DATABASE honeypot_db;


更新 database.py 中的 DB_CONFIG：DB_CONFIG = {
    "host": "localhost",
    "user": "<your-mysql-user>",
    "password": "<your-mysql-password>",
    "database": "honeypot_db"
}




（可选）配置 Flask：

设置环境变量 SECRET_KEY：export SECRET_KEY="your-secret-key"  # Linux/Mac
set SECRET_KEY="your-secret-key"     # Windows


或在 config.py 中修改 SECRET_KEY。


创建数据目录：

创建 data/ 目录并确保 rules.json 存在。
可选：创建 functions.json 或使用默认命令映射。


初始化数据库：

运行 database.py 初始化表结构：python database.py




运行应用：
python app.py


访问 http://localhost:5000 查看 Web 界面。



使用方法

打开 Web 界面：
浏览器访问 http://localhost:5000。


测试攻击场景：
导航到攻击页面，例如：
/command_injection：输入命令如 ls 或 rm -rf /。
/xss：输入脚本如 <script>alert('xss')</script>。
/sql_injection：输入查询如 1' OR '1'='1。


查看 JSON 响应，确认是否检测到攻击。


查看日志：
访问 /logs 查看攻击日志，支持分页浏览。


监控攻击：
后台日志监控（database.py）自动将新攻击记录同步到数据库。
检查 logs/attacks.log 或查询数据库表 attacks。


通用检测接口：
使用 /detect 端点发送 JSON 数据：curl -X POST http://localhost:5000/detect -H "Content-Type: application/json" -d '{"xss": "<script>alert(1)</script>"}'





项目结构
web-security-honeypot/
├── app.py                   # Flask 主应用
├── config.py                # 配置管理
├── database.py              # 数据库初始化和日志存储
├── logs.py                  # 日志记录和读取
├── command_injection.py     # 命令注入检测
├── csrf.py                  # CSRF 检测
├── directory_traversal.py   # 目录遍历检测
├── file_inclusion.py        # 文件包含检测
├── sql_injection.py         # SQL 注入检测
├── xss.py                   # XSS 检测
├── sandbox/
│   ├── generate.py          # 虚拟环境和伪装内容生成
│   ├── functions.py         # 攻击检测和规则应用
│   ├── replacement/
│       ├── getenv.py        # 环境变量访问模拟
│       ├── ini_get.py       # 配置文件访问模拟
│       ├── system.py        # 系统命令执行模拟
├── data/
│   ├── rules.json           # 攻击检测规则
│   ├── functions.json       # 命令映射（可选）
├── templates/               # HTML 模板
│   ├── index.html
│   ├── command_injection.html
│   ├── csrf.html
│   ├── directory_traversal.html
│   ├── file_inclusion.html
│   ├── sql_injection.html
│   ├── xss.html
│   ├── logs.html
│   ├── 404.html
├── logs/                    # 日志目录
│   ├── attacks.log
├── requirements.txt         # 依赖列表

注意事项

数据库安全：
确保 DB_CONFIG 中的 MySQL 凭证安全，避免硬编码敏感信息（如当前 root:123456）。
生产环境中使用强密码并限制数据库访问。


日志管理：
日志文件 logs/attacks.log 会持续增长，建议配置日志轮转。


规则扩展：
编辑 rules.json 添加新规则，支持更复杂的攻击模式。
当前规则基于正则表达式，可能需优化以减少误报。


虚拟环境：
VirtualEnvironment 仅模拟有限文件和命令，需扩展以支持更多场景。


生产部署：
禁用 app.run(debug=True)，使用 Gunicorn 等 WSGI 服务器。
配置 HTTPS 和防火墙，防止真实攻击。


安全测试：
测试环境应隔离，避免影响真实系统。



常见问题

Q：数据库连接失败？
A：检查 MySQL 服务状态，确认 DB_CONFIG 中的主机、用户和密码。


Q：规则未生效？
A：确保 rules.json 存在且格式正确，或检查正则表达式是否匹配输入。


Q：日志为空？
A：确认 logs/ 目录有写权限，触发攻击以生成日志。


Q：检测误报或漏报？
A：优化 rules.json 中的正则表达式，或添加机器学习模型提升准确性。
