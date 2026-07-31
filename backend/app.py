"""
┌─────────────────────────────────────────────────────┐
│  翼澜 — 无人机洪涝应急决策系统                      │
│  Flask 后端主入口                                   │
│  启动方式：python app.py                            │
│  启动后访问：http://localhost:5000                   │
└─────────────────────────────────────────────────────┘
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# ============================================================
# 注册蓝图（路由模块）
# ============================================================
from routes.water_extract import water_bp
from routes.path_plan import path_bp
from routes.object_detect import detect_bp
from routes.orchestrator import orc_bp
from routes.gis_analysis import gis_bp
from routes.agent import agent_bp

app.register_blueprint(water_bp, url_prefix='/api/water')
app.register_blueprint(path_bp, url_prefix='/api/path')
app.register_blueprint(detect_bp, url_prefix='/api/detect')
app.register_blueprint(orc_bp, url_prefix='/api/orchestrator')
app.register_blueprint(gis_bp, url_prefix='/api/gis')
app.register_blueprint(agent_bp, url_prefix='/api/agent')

# ============================================================
# 前端静态文件服务
# ============================================================
@app.route('/')
def serve_frontend():
    return send_from_directory(os.path.join(app.static_folder, 'public'), 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(app.static_folder, 'public', path)
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(app.static_folder, 'public'), path)
    return send_from_directory(os.path.join(app.static_folder, 'public'), 'index.html')

# ============================================================
# 健康检查接口（测试后端是否启动成功）
# ============================================================
@app.route('/api/hello')
def hello():
    """✅ 第一个 API：验证后端已启动"""
    return jsonify({
        "message": "Hello! 翼澜系统后端已启动",
        "status": "running",
        "version": "0.1.0"
    })

# ============================================================
# 启动
# ============================================================
if __name__ == '__main__':
    print("=" * 55)
    print("  翼澜系统后端已启动")
    print("  API: http://localhost:5000")
    print("  Ctrl+C 停止")
    print("=" * 55)
    app.run(host='127.0.0.1', port=5000, debug=False)
