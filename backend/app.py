#!/usr/bin/env python3
"""
时间管理系统 - 后端应用入口
"""

import os
from dotenv import load_dotenv
from app import create_app

# 加载环境变量
load_dotenv()

# 创建应用实例
app = create_app()


@app.route('/')
def index():
    """根路由 - 健康检查"""
    return {
        'message': 'Time Management System API',
        'version': '1.0.0',
        'status': 'running'
    }


@app.route('/api/health')
def health_check():
    """健康检查端点"""
    return {
        'status': 'healthy',
        'timestamp': '2025-01-01T00:00:00Z'
    }


if __name__ == '__main__':
    # 开发环境运行
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug
    )