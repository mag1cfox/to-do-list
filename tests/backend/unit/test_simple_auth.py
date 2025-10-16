#!/usr/bin/env python3
"""
简化用户认证模块测试
"""

import pytest
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


class TestSimpleAuth:
    """测试用户认证功能"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'

        with app.test_client() as client:
            with app.app_context():
                from app import db
                db.create_all()
                yield client

    def test_register_and_login(self, client):
        """测试用户注册和登录流程"""
        # 测试注册
        register_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }

        register_response = client.post('/auth/register',
                                      data=json.dumps(register_data),
                                      content_type='application/json')

        assert register_response.status_code == 201
        register_result = json.loads(register_response.data)
        assert register_result['message'] == 'User registered successfully'
        assert 'user' in register_result
        assert register_result['user']['username'] == 'testuser'

        # 测试登录
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }

        login_response = client.post('/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')

        assert login_response.status_code == 200
        login_result = json.loads(login_response.data)
        assert 'access_token' in login_result
        assert 'user' in login_result
        assert login_result['user']['username'] == 'testuser'

    def test_login_invalid_password(self, client):
        """测试错误密码登录"""
        # 先注册用户
        register_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }

        client.post('/auth/register',
                   data=json.dumps(register_data),
                   content_type='application/json')

        # 使用错误密码登录
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        login_response = client.post('/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')

        assert login_response.status_code == 401
        result = json.loads(login_response.data)
        assert result['error'] == 'Invalid credentials'

    def test_register_missing_fields(self, client):
        """测试缺少必填字段"""
        # 缺少用户名
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }

        response = client.post('/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')

        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'Missing required field' in result['error']