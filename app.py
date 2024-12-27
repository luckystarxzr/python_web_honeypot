from flask import Flask, render_template, request, jsonify
from modules.logs import get_logs
from sandbox.functions import detect_attack, load_rules

app = Flask(__name__)

# 加载规则
rules = load_rules()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/command_injection", methods=['GET', 'POST'])
def command_injection():
    if request.method == 'POST':
        command = request.form.get('cmd', '')
        result = detect_attack({"command": command}, rules)
        return jsonify(result)
    return render_template("command_injection.html")

@app.route("/csrf", methods=['GET', 'POST'])
def csrf():
    if request.method == 'POST':
        result = detect_attack({"csrf": True}, rules)
        return jsonify(result)
    return render_template("csrf.html")

@app.route("/directory_traversal", methods=['GET', 'POST'])
def directory_traversal():
    if request.method == 'POST':
        path = request.form.get('path')
        result = detect_attack({"filepath": path}, rules)
        return jsonify(result)
    return render_template("directory_traversal.html")

@app.route("/file_inclusion", methods=['GET', 'POST'])
def file_inclusion():
    if request.method == 'POST':
        file_path = request.form.get('file')
        result = detect_attack({"filepath": file_path}, rules)
        return jsonify(result)
    return render_template("file_inclusion.html")

@app.route("/sql_injection", methods=['GET', 'POST'])
def sql_injection():
    if request.method == 'POST':
        query = request.form.get('query')
        result = detect_attack({"sql": query}, rules)
        return jsonify(result)
    return render_template("sql_injection.html")

@app.route("/xss", methods=['GET', 'POST'])
def xss():
    if request.method == 'POST':
        payload = request.form.get('payload')
        result = detect_attack({"xss": payload}, rules)
        return jsonify(result)
    return render_template("xss.html")

@app.route("/logs")
def show_logs():
    """显示日志页面"""
    logs = get_logs()  # 从日志文件读取内容
    page = request.args.get("page", 1, type=int)  # 获取分页参数，默认为 1
    per_page = 10  # 每页日志条数
    total_pages = (len(logs) + per_page - 1) // per_page  # 计算总页数

    # 分页逻辑
    start = (page - 1) * per_page
    end = start + per_page
    paginated_logs = logs[start:end]

    return render_template("logs.html", logs=paginated_logs, page=page, total_pages=total_pages)


@app.route("/detect", methods=['POST'])
def detect():
    """通用攻击检测接口"""
    if not request.is_json:
        return jsonify({"error": "Content type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    result = detect_attack(data, rules)
    return jsonify(result)

# 添加错误处理
@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
