#!/usr/bin/env python3
"""
pytest全局配置文件
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置测试环境变量
os.environ['TESTING'] = 'True'
os.environ['FLASK_ENV'] = 'testing'

@pytest.fixture(scope='session')
def test_config():
    """测试配置"""
    return {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'CORS_ORIGINS': ['http://localhost:3000']
    }