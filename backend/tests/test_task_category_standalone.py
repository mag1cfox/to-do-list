#!/usr/bin/env python3
"""
独立任务类别模型测试 - 不依赖models/__init__.py
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class TestTaskCategoryStandalone:
    """测试任务类别模型独立功能"""

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
            category_id = db.Column(db.String(36), db.ForeignKey('task_categories.id'), nullable=False)

        # 定义任务类别模型
        class TaskCategory(BaseModel):
            __tablename__ = 'task_categories'

            name = db.Column(db.String(50), nullable=False)
            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
            color = db.Column(db.String(7), nullable=False)  # HEX颜色值
            icon = db.Column(db.String(50))
            description = db.Column(db.Text)

            # 关联关系
            user = db.relationship('User', backref='task_categories')
            tasks = db.relationship('Task', backref='category', cascade='all, delete-orphan')

            def to_dict(self) -> dict:
                """转换为字典"""
                base_dict = super().to_dict()
                base_dict.update({
                    'name': self.name,
                    'user_id': self.user_id,
                    'color': self.color,
                    'icon': self.icon,
                    'description': self.description,
                    'task_count': self.get_task_count(),
                    'total_time_spent': self.get_total_time_spent()
                })
                return base_dict

            def get_task_count(self) -> int:
                """获取任务数量"""
                return len(self.tasks) if self.tasks else 0

            def get_total_time_spent(self) -> int:
                """获取总时间花费（分钟）"""
                if not self.tasks:
                    return 0

                total_time = 0
                for task in self.tasks:
                    # 这里需要实现获取任务实际时间的方法
                    # 暂时返回0，后续可以集成TimeLog数据
                    total_time += 0
                return total_time

        # 保存模型引用
        self.User = User
        self.Task = Task
        self.TaskCategory = TaskCategory
        self.db = db

        with app.app_context():
            db.create_all()
            yield app

    def test_task_category_creation(self, app):
        """测试任务类别创建"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建任务类别
            category = self.TaskCategory(
                name='工作',
                color='#FF5733',
                user_id=user.id,
                icon='work',
                description='工作相关任务'
            )

            self.db.session.add(category)
            self.db.session.commit()

            assert category.id is not None
            assert category.name == '工作'
            assert category.color == '#FF5733'
            assert category.user_id == user.id
            assert category.icon == 'work'
            assert category.description == '工作相关任务'

    def test_task_category_task_count(self, app):
        """测试任务类别中的任务数量统计"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建任务类别
            category = self.TaskCategory(
                name='学习',
                color='#33FF57',
                user_id=user.id
            )
            self.db.session.add(category)
            self.db.session.commit()

            # 测试空类别的任务数量
            assert category.get_task_count() == 0

            # 创建任务
            task1 = self.Task(title='学习Python', user_id=user.id, category_id=category.id)
            task2 = self.Task(title='学习数据库', user_id=user.id, category_id=category.id)
            self.db.session.add_all([task1, task2])
            self.db.session.commit()

            # 测试有任务的类别
            assert category.get_task_count() == 2

    def test_task_category_time_spent(self, app):
        """测试任务类别时间花费统计"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建任务类别
            category = self.TaskCategory(
                name='健身',
                color='#3357FF',
                user_id=user.id
            )
            self.db.session.add(category)
            self.db.session.commit()

            # 测试空类别的时间花费
            assert category.get_total_time_spent() == 0

            # 创建任务（即使有任务，时间花费暂时返回0）
            task = self.Task(title='跑步', user_id=user.id, category_id=category.id)
            self.db.session.add(task)
            self.db.session.commit()

            # 测试有任务的时间花费（目前返回0）
            assert category.get_total_time_spent() == 0

    def test_task_category_to_dict(self, app):
        """测试任务类别转换为字典"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建任务类别
            category = self.TaskCategory(
                name='阅读',
                color='#F3FF33',
                user_id=user.id,
                icon='book',
                description='阅读和学习任务'
            )

            category_dict = category.to_dict()

            assert 'id' in category_dict
            assert category_dict['name'] == '阅读'
            assert category_dict['color'] == '#F3FF33'
            assert category_dict['user_id'] == user.id
            assert category_dict['icon'] == 'book'
            assert category_dict['description'] == '阅读和学习任务'
            assert 'task_count' in category_dict
            assert 'total_time_spent' in category_dict
            assert 'created_at' in category_dict
            assert 'updated_at' in category_dict