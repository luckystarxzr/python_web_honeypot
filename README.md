基于Python的web_honeypot系统，带有测试代码，还能继续完善
Web 安全检测与蜜罐系统
项目概述
Web 安全检测与蜜罐系统是一个基于 Flask 的 Web 应用程序，旨在模拟和检测常见的 Web 安全威胁，包括命令注入、CSRF、目录遍历、文件包含、SQL 注入和 XSS 攻击。该系统通过规则匹配和日志记录，识别潜在的恶意行为，并将攻击信息存储到日志文件和 MySQL 数据库中，供后续分析。系统还提供了一个交互式 Web 界面，允许用户测试攻击场景并查看攻击日志。
功能特性

攻击模拟与检测：
支持检测命令注入、CSRF、目录遍历、文件包含、SQL 注入和 XSS 攻击。
使用规则匹配和正则表达式识别恶意输入。


日志记录：
将攻击信息记录到日志文件（logs/attacks.log）和 MySQL 数据库。
包含攻击类型、IP 地址、用户代理、时间戳等详细信息。


数据库支持：
使用 MySQL 存储攻击日志和请求日志，便于查询和分析。
自动初始化数据库表结构。


日志监控：
后台线程定期扫描日志文件，将新攻击信息同步到数据库。


Web 界面：
提供交互式页面，允许用户输入测试数据并查看检测结果。
显示分页的攻击日志，支持浏览历史记录。


错误处理：
自定义 404 页面，提升用户体验。


配置管理：
通过 config.py 支持开发和生产环境的配置切换。



技术栈

后端：
Python 3.6+
Flask：Web 框架
MySQL Connector：数据库连接
Logging：日志记录


前端：
HTML/CSS/JavaScript
Jinja2：模板引擎


数据库：
MySQL：存储攻击和请求日志


其他：
Regular Expressions (re)：用于检测恶意模式
Threading：异步日志监控



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


或在 config.py 中直接修改 SECRET_KEY。


初始化数据库：

运行 database.py 初始化表结构：python database.py




运行应用：
python app.py


访问 http://localhost:5000 查看 Web 界面。



使用方法

打开 Web 界面：
浏览器访问 http://localhost:5000。


测试攻击场景：
导航到各攻击页面（例如 /command_injection、/xss）。
输入测试数据（例如命令 ls; rm -rf / 或 XSS 脚本 <script>alert('xss')</script>）。
查看检测结果（JSON 响应或页面提示）。


查看日志：
访问 /logs 查看攻击日志，支持分页浏览。


监控攻击：
后台日志监控自动将新攻击记录同步到数据库。
检查 logs/attacks.log 或查询数据库表 attacks。



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
确保 DB_CONFIG 中的 MySQL 凭证安全，避免硬编码敏感信息。
生产环境中建议使用更强的密码和限制数据库访问。


日志管理：
日志文件 logs/attacks.log 会持续增长，建议定期清理或使用日志轮转。


攻击检测：
当前规则基于简单模式匹配，可能无法检测复杂攻击。
可扩展 rules 或添加机器学习模型以提高检测准确性。


生产部署：
禁用 debug=True（在 app.py 中）。
使用 WSGI 服务器（如 Gunicorn）部署 Flask 应用。


安全测试：
测试环境应隔离，避免真实系统受到测试攻击的影响。



常见问题

Q：数据库连接失败？
A：检查 MySQL 服务是否运行，确认 DB_CONFIG 中的主机、用户和密码正确。


Q：日志文件为空？
A：确保 logs/ 目录有写权限，检查是否有攻击触发日志记录。


Q：检测结果不准确？
A：当前规则可能不完整，可在 rules 文件中添加更多模式或改进正则表达式。



贡献
欢迎提交 Issue 或 Pull Request！请遵循以下步骤：

Fork 项目。
创建特性分支（git checkout -b feature/xxx）。
提交更改（git commit -m "Add xxx"）。
推送分支（git push origin feature/xxx）。
创建 Pull Request。

许可证
本项目采用 MIT 许可证。详情见 LICENSE 文件。
