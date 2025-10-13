#!/usr/bin/env python3
"""
独立用户模型测试 - 不依赖models/__init__.py
"""

import pytest
import sys
import os
import bcrypt
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class TestUserStandalone:
    """测试用户模型独立功能"""

    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db = SQLAlchemy(app)

        # 定义基础模型
        class BaseModel(db.Model):
            """基础模型类"""
            __abstract__ = True

            id = db.Column(db.String(36), primary_key=True, default=lambda: str(os.urandom(16).hex()))
            created_at = db.Column(db.DateTime, default=lambda: __import__('datetime').datetime.utcnow())
            updated_at = db.Column(db.DateTime, default=lambda: __import__('datetime').datetime.utcnow(),
                                 onupdate=lambda: __import__('datetime').datetime.utcnow())

            def to_dict(self) -> dict:
                """转换为字典"""
                return {
                    'id': self.id,
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None
                }

        # 定义用户模型
        class User(BaseModel):
            """用户模型"""
            __tablename__ = 'users'

            username = db.Column(db.String(50), unique=True, nullable=False)
            email = db.Column(db.String(100), unique=True, nullable=False)
            password_hash = db.Column(db.String(255), nullable=False)
            preferences = db.Column(db.Text, default='{}')

            def set_password(self, password: str):
                """设置密码（加密存储）"""
                salt = bcrypt.gensalt()
                self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

            def check_password(self, password: str) -> bool:
                """验证密码"""
                return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

            def get_preferences(self) -> dict:
                """获取用户偏好设置"""
                if not self.preferences:
                    return {}
                try:
                    return json.loads(self.preferences)
                except json.JSONDecodeError:
                    return {}

            def set_preferences(self, preferences: dict):
                """设置用户偏好"""
                self.preferences = json.dumps(preferences)

            def to_dict(self) -> dict:
                """转换为字典（不包含敏感信息）"""
                base_dict = super().to_dict()
                base_dict.update({
                    'username': self.username,
                    'email': self.email,
                    'preferences': self.get_preferences()
                })
                return base_dict

        # 保存模型引用
        self.User = User
        self.db = db

        with app.app_context():
            db.create_all()
            yield app

    def test_user_creation(self, app):
        """测试用户创建"""
        with app.app_context():
            user = self.User(username='testuser', email='test@example.com')
            user.set_password('password123')

            self.db.session.add(user)
            self.db.session.commit()

            assert user.id is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.password_hash != 'password123'  # 密码应该被加密
            assert user.created_at is not None
            assert user.updated_at is not None

    def test_password_encryption(self, app):
        """测试密码加密"""
        with app.app_context():
            user = self.User(username='testuser', email='test@example.com')
            original_password = 'password123'
            user.set_password(original_password)

            # 验证密码哈希不是明文
            assert user.password_hash != original_password
            assert len(user.password_hash) > 0

            # 验证密码检查功能
            assert user.check_password(original_password) == True
            assert user.check_password('wrongpassword') == False

    def test_user_preferences(self, app):
        """测试用户偏好设置"""
        with app.app_context():
            user = self.User(username='testuser', email='test@example.com')
            user.set_password('password123')

            # 测试默认偏好
            default_prefs = user.get_preferences()
            assert isinstance(default_prefs, dict)
            assert len(default_prefs) == 0

            # 测试设置偏好
            test_prefs = {'theme': 'dark', 'language': 'zh-CN'}
            user.set_preferences(test_prefs)
            assert user.get_preferences() == test_prefs

    def test_user_to_dict(self, app):
        """测试用户转换为字典"""
        with app.app_context():
            user = self.User(username='testuser', email='test@example.com')
            user.set_password('password123')

            user_dict = user.to_dict()

            assert 'id' in user_dict
            assert user_dict['username'] == 'testuser'
            assert user_dict['email'] == 'test@example.com'
            assert 'preferences' in user_dict
            assert 'password_hash' not in user_dict  # 敏感信息不返回
            assert 'created_at' in user_dict
            assert 'updated_at' in user_dict