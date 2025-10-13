#!/usr/bin/env python3
"""
独立项目模型测试 - 不依赖models/__init__.py
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class TestProjectStandalone:
    """测试项目模型独立功能"""

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
            project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=True)
            estimated_pomodoros = db.Column(db.Integer, default=1)
            status = db.Column(db.String(20), default='PENDING')

        # 定义项目模型
        class Project(BaseModel):
            __tablename__ = 'projects'

            name = db.Column(db.String(100), nullable=False)
            description = db.Column(db.Text)
            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
            color = db.Column(db.String(7), nullable=False)  # 项目颜色标识

            # 关联关系
            user = db.relationship('User', backref='projects')
            tasks = db.relationship('Task', backref='project', cascade='all, delete-orphan')

            def to_dict(self) -> dict:
                """转换为字典"""
                base_dict = super().to_dict()
                base_dict.update({
                    'name': self.name,
                    'description': self.description,
                    'user_id': self.user_id,
                    'color': self.color,
                    'task_count': self.get_task_count(),
                    'total_estimated_time': self.get_total_estimated_time(),
                    'total_actual_time': self.get_total_actual_time(),
                    'completion_progress': self.get_completion_progress()
                })
                return base_dict

            def get_task_count(self) -> int:
                """获取项目中的任务数量"""
                return len(self.tasks) if self.tasks else 0

            def get_total_estimated_time(self) -> int:
                """获取项目总预估时间（分钟）"""
                if not self.tasks:
                    return 0

                total_time = 0
                for task in self.tasks:
                    # 假设每个番茄钟25分钟
                    total_time += task.estimated_pomodoros * 25 if task.estimated_pomodoros else 0
                return total_time

            def get_total_actual_time(self) -> int:
                """获取项目总实际花费时间（分钟）"""
                if not self.tasks:
                    return 0

                total_time = 0
                for task in self.tasks:
                    # 这里需要实现获取任务实际时间的方法
                    # 暂时返回0，后续可以集成TimeLog数据
                    total_time += 0
                return total_time

            def get_completion_progress(self) -> float:
                """获取项目完成进度（0-1）"""
                if not self.tasks:
                    return 0.0

                completed_tasks = [task for task in self.tasks if task.status == 'COMPLETED']
                return len(completed_tasks) / len(self.tasks)

        # 保存模型引用
        self.User = User
        self.Task = Task
        self.Project = Project
        self.db = db

        with app.app_context():
            db.create_all()
            yield app

    def test_project_creation(self, app):
        """测试项目创建"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建项目
            project = self.Project(
                name='个人网站开发',
                color='#FF5733',
                user_id=user.id,
                description='开发个人博客网站'
            )

            self.db.session.add(project)
            self.db.session.commit()

            assert project.id is not None
            assert project.name == '个人网站开发'
            assert project.color == '#FF5733'
            assert project.user_id == user.id
            assert project.description == '开发个人博客网站'

    def test_project_task_count(self, app):
        """测试项目中的任务数量统计"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建项目
            project = self.Project(
                name='学习项目',
                color='#33FF57',
                user_id=user.id
            )
            self.db.session.add(project)
            self.db.session.commit()

            # 测试空项目的任务数量
            assert project.get_task_count() == 0

            # 创建任务
            task1 = self.Task(title='学习Python', user_id=user.id, project_id=project.id, estimated_pomodoros=2)
            task2 = self.Task(title='学习数据库', user_id=user.id, project_id=project.id, estimated_pomodoros=3)
            self.db.session.add_all([task1, task2])
            self.db.session.commit()

            # 测试有任务的项目
            assert project.get_task_count() == 2

    def test_project_estimated_time(self, app):
        """测试项目预估时间计算"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建项目
            project = self.Project(
                name='健身计划',
                color='#3357FF',
                user_id=user.id
            )
            self.db.session.add(project)
            self.db.session.commit()

            # 测试空项目的预估时间
            assert project.get_total_estimated_time() == 0

            # 创建任务
            task1 = self.Task(title='跑步', user_id=user.id, project_id=project.id, estimated_pomodoros=1)
            task2 = self.Task(title='力量训练', user_id=user.id, project_id=project.id, estimated_pomodoros=2)
            self.db.session.add_all([task1, task2])
            self.db.session.commit()

            # 测试有任务的项目预估时间（1*25 + 2*25 = 75分钟）
            assert project.get_total_estimated_time() == 75

    def test_project_completion_progress(self, app):
        """测试项目完成进度计算"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建项目
            project = self.Project(
                name='阅读计划',
                color='#F3FF33',
                user_id=user.id
            )
            self.db.session.add(project)
            self.db.session.commit()

            # 测试空项目的完成进度
            assert project.get_completion_progress() == 0.0

            # 创建任务
            task1 = self.Task(title='阅读书籍A', user_id=user.id, project_id=project.id, status='COMPLETED')
            task2 = self.Task(title='阅读书籍B', user_id=user.id, project_id=project.id, status='PENDING')
            task3 = self.Task(title='阅读书籍C', user_id=user.id, project_id=project.id, status='PENDING')
            self.db.session.add_all([task1, task2, task3])
            self.db.session.commit()

            # 测试有任务的项目完成进度（1/3 ≈ 0.333）
            assert abs(project.get_completion_progress() - 0.333) < 0.001

    def test_project_to_dict(self, app):
        """测试项目转换为字典"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建项目
            project = self.Project(
                name='写作项目',
                color='#FF33F3',
                user_id=user.id,
                description='个人写作项目'
            )

            project_dict = project.to_dict()

            assert 'id' in project_dict
            assert project_dict['name'] == '写作项目'
            assert project_dict['color'] == '#FF33F3'
            assert project_dict['user_id'] == user.id
            assert project_dict['description'] == '个人写作项目'
            assert 'task_count' in project_dict
            assert 'total_estimated_time' in project_dict
            assert 'total_actual_time' in project_dict
            assert 'completion_progress' in project_dict
            assert 'created_at' in project_dict
            assert 'updated_at' in project_dict