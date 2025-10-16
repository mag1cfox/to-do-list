#!/usr/bin/env python3
"""
独立标签模型测试 - 不依赖models/__init__.py
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class TestTagStandalone:
    """测试标签模型独立功能"""

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

        # 定义用户模型（简化版）
        class User(BaseModel):
            __tablename__ = 'users'
            username = db.Column(db.String(50), unique=True, nullable=False)
            email = db.Column(db.String(100), unique=True, nullable=False)
            password_hash = db.Column(db.String(255), nullable=False)

        # 定义任务模型（简化版）
        class Task(BaseModel):
            __tablename__ = 'tasks'
            title = db.Column(db.String(200), nullable=False)
            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

        # 定义标签模型
        class Tag(BaseModel):
            __tablename__ = 'tags'

            name = db.Column(db.String(50), nullable=False)
            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
            color = db.Column(db.String(7))  # HEX颜色值

            # 多对多关联
            tasks = db.relationship('Task', secondary='task_tags', backref='tags')

            def to_dict(self) -> dict:
                """转换为字典"""
                base_dict = super().to_dict()
                base_dict.update({
                    'name': self.name,
                    'user_id': self.user_id,
                    'color': self.color,
                    'usage_count': self.get_usage_count()
                })
                return base_dict

            def get_usage_count(self) -> int:
                """获取标签使用次数"""
                return len(self.tasks) if self.tasks else 0

        # 定义任务标签关联表
        class TaskTag(db.Model):
            __tablename__ = 'task_tags'
            task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), primary_key=True)
            tag_id = db.Column(db.String(36), db.ForeignKey('tags.id'), primary_key=True)

        # 保存模型引用
        self.User = User
        self.Task = Task
        self.Tag = Tag
        self.TaskTag = TaskTag
        self.db = db

        with app.app_context():
            db.create_all()
            yield app

    def test_tag_creation(self, app):
        """测试标签创建"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建标签
            tag = self.Tag(
                name='重要',
                color='#FF5733',
                user_id=user.id
            )

            self.db.session.add(tag)
            self.db.session.commit()

            assert tag.id is not None
            assert tag.name == '重要'
            assert tag.color == '#FF5733'
            assert tag.user_id == user.id

    def test_tag_usage_count(self, app):
        """测试标签使用次数统计"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建标签
            tag = self.Tag(
                name='紧急',
                color='#FF3333',
                user_id=user.id
            )
            self.db.session.add(tag)
            self.db.session.commit()

            # 测试空标签的使用次数
            assert tag.get_usage_count() == 0

            # 创建任务
            task1 = self.Task(title='紧急任务1', user_id=user.id)
            task2 = self.Task(title='紧急任务2', user_id=user.id)
            self.db.session.add_all([task1, task2])
            self.db.session.commit()

            # 关联标签和任务
            task_tag1 = self.TaskTag(task_id=task1.id, tag_id=tag.id)
            task_tag2 = self.TaskTag(task_id=task2.id, tag_id=tag.id)
            self.db.session.add_all([task_tag1, task_tag2])
            self.db.session.commit()

            # 测试有任务关联的标签使用次数
            assert tag.get_usage_count() == 2

    def test_tag_to_dict(self, app):
        """测试标签转换为字典"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建标签
            tag = self.Tag(
                name='学习',
                color='#33FF57',
                user_id=user.id
            )

            tag_dict = tag.to_dict()

            assert 'id' in tag_dict
            assert tag_dict['name'] == '学习'
            assert tag_dict['color'] == '#33FF57'
            assert tag_dict['user_id'] == user.id
            assert 'usage_count' in tag_dict
            assert 'created_at' in tag_dict
            assert 'updated_at' in tag_dict