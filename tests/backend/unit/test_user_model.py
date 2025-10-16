#!/usr/bin/env python3
"""
用户模型基本功能测试
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.user import User


class TestUserModel:
    """测试用户模型基本功能"""

    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db = SQLAlchemy(app)

        # 临时替换全局db
        import models
        models.db = db

        with app.app_context():
            # 只创建users表
            User.__table__.create(db.engine)
            yield app

    @pytest.fixture
    def db(self, app):
        """获取数据库实例"""
        from models import db
        return db

    def test_user_creation(self, db):
        """测试用户创建"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')

        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.password_hash != 'password123'  # 密码应该被加密
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_password_encryption(self, db):
        """测试密码加密"""
        user = User(username='testuser', email='test@example.com')
        original_password = 'password123'
        user.set_password(original_password)

        # 验证密码哈希不是明文
        assert user.password_hash != original_password
        assert len(user.password_hash) > 0

        # 验证密码检查功能
        assert user.check_password(original_password) == True
        assert user.check_password('wrongpassword') == False

    def test_user_preferences(self, db):
        """测试用户偏好设置"""
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

    def test_user_to_dict(self, db):
        """测试用户转换为字典"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')

        user_dict = user.to_dict()

        assert 'id' in user_dict
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert 'preferences' in user_dict
        assert 'password_hash' not in user_dict  # 敏感信息不返回
        assert 'created_at' in user_dict
        assert 'updated_at' in user_dict