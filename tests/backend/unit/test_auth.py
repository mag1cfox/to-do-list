#!/usr/bin/env python3
"""
用户认证模块测试
"""

import pytest
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.user import User


class TestAuth:
    """测试用户认证功能"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.test_client() as client:
            with app.app_context():
                from app import db
                db.create_all()
                yield client

    def test_register_success(self, client):
        """测试用户注册成功"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }

        response = client.post('/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result['message'] == 'User registered successfully'
        assert 'user' in result
        assert result['user']['username'] == 'testuser'
        assert result['user']['email'] == 'test@example.com'
        assert 'password_hash' not in result['user']  # 确保密码哈希不返回

    def test_register_missing_fields(self, client):
        """测试缺少必填字段的注册"""
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

    def test_register_duplicate_username(self, client):
        """测试重复用户名的注册"""
        # 先创建一个用户
        user = User(username='testuser', email='test1@example.com')
        user.set_password('password123')
        from app import db
        db.session.add(user)
        db.session.commit()

        # 尝试用相同用户名注册
        data = {
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password123'
        }

        response = client.post('/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')

        assert response.status_code == 400
        result = json.loads(response.data)
        assert result['error'] == 'Username already exists'

    def test_register_duplicate_email(self, client):
        """测试重复邮箱的注册"""
        # 先创建一个用户
        user = User(username='testuser1', email='test@example.com')
        user.set_password('password123')
        from app import db
        db.session.add(user)
        db.session.commit()

        # 尝试用相同邮箱注册
        data = {
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'password123'
        }

        response = client.post('/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')

        assert response.status_code == 400
        result = json.loads(response.data)
        assert result['error'] == 'Email already exists'

    def test_login_success(self, client):
        """测试用户登录成功"""
        # 先创建一个用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        from app import db
        db.session.add(user)
        db.session.commit()

        # 登录
        data = {
            'username': 'testuser',
            'password': 'password123'
        }

        response = client.post('/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')

        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'access_token' in result
        assert 'user' in result
        assert result['user']['username'] == 'testuser'

    def test_login_invalid_credentials(self, client):
        """测试无效凭据的登录"""
        # 先创建一个用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        from app import db
        db.session.add(user)
        db.session.commit()

        # 使用错误密码登录
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        response = client.post('/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')

        assert response.status_code == 401
        result = json.loads(response.data)
        assert result['error'] == 'Invalid credentials'

    def test_login_nonexistent_user(self, client):
        """测试不存在的用户登录"""
        data = {
            'username': 'nonexistent',
            'password': 'password123'
        }

        response = client.post('/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')

        assert response.status_code == 401
        result = json.loads(response.data)
        assert result['error'] == 'Invalid credentials'

    def test_get_current_user_with_token(self, client):
        """测试使用token获取当前用户信息"""
        # 先创建用户并登录获取token
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        from app import db
        db.session.add(user)
        db.session.commit()

        # 登录获取token
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }

        login_response = client.post('/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')

        token = json.loads(login_response.data)['access_token']

        # 使用token获取用户信息
        response = client.get('/auth/me',
                            headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'user' in result
        assert result['user']['username'] == 'testuser'
        assert result['user']['email'] == 'test@example.com'

    def test_get_current_user_without_token(self, client):
        """测试无token获取当前用户信息"""
        response = client.get('/auth/me')

        # JWT应该返回401而不是404
        assert response.status_code == 401

    def test_password_encryption(self, client):
        """测试密码加密功能"""
        # 创建用户
        user = User(username='testuser', email='test@example.com')
        original_password = 'password123'
        user.set_password(original_password)

        # 验证密码哈希不是明文
        assert user.password_hash != original_password
        assert len(user.password_hash) > 0

        # 验证密码检查功能
        assert user.check_password(original_password) == True
        assert user.check_password('wrongpassword') == False

    def test_user_preferences(self, client):
        """测试用户偏好设置功能"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')

        # 测试默认偏好
        default_prefs = user.get_preferences()
        assert isinstance(default_prefs, dict)
        assert len(default_prefs) == 0

        # 测试设置偏好
        test_prefs = {'theme': 'dark', 'language': 'zh-CN'}
        user.set_preferences(test_prefs)
        assert user.get_preferences() == test_prefs

        # 测试序列化
        assert user.preferences == json.dumps(test_prefs)