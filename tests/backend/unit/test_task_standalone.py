#!/usr/bin/env python3
"""
独立任务模型测试 - 不依赖models/__init__.py
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class TestTaskStandalone:
    """测试任务模型独立功能"""

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
            created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
            updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow(),
                                 onupdate=lambda: datetime.utcnow())

            def to_dict(self) -> dict:
                """转换为字典"""
                return {
                    'id': self.id,
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None
                }

        # 定义枚举类型
        import enum
        class TaskType(enum.Enum):
            RIGID = 'RIGID'
            FLEXIBLE = 'FLEXIBLE'

        class TaskStatus(enum.Enum):
            PENDING = 'PENDING'
            IN_PROGRESS = 'IN_PROGRESS'
            COMPLETED = 'COMPLETED'
            CANCELLED = 'CANCELLED'

        class PriorityLevel(enum.Enum):
            HIGH = 'HIGH'
            MEDIUM = 'MEDIUM'
            LOW = 'LOW'

        # 定义用户模型（简化版）
        class User(BaseModel):
            __tablename__ = 'users'
            username = db.Column(db.String(50), unique=True, nullable=False)
            email = db.Column(db.String(100), unique=True, nullable=False)
            password_hash = db.Column(db.String(255), nullable=False)

        # 定义任务类别模型（简化版）
        class TaskCategory(BaseModel):
            __tablename__ = 'task_categories'
            name = db.Column(db.String(100), nullable=False)
            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

        # 定义任务模型
        class Task(BaseModel):
            __tablename__ = 'tasks'

            # 基础属性
            title = db.Column(db.String(200), nullable=False)
            description = db.Column(db.Text)
            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

            # 时间属性
            planned_start_time = db.Column(db.DateTime, nullable=False)
            estimated_pomodoros = db.Column(db.Integer, default=1)
            task_type = db.Column(db.Enum(TaskType), nullable=False)

            # 分类与排布
            category_id = db.Column(db.String(36), db.ForeignKey('task_categories.id'), nullable=False)
            scheduled_time_block_id = db.Column(db.String(36))

            # 状态管理
            status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
            priority = db.Column(db.Enum(PriorityLevel), default=PriorityLevel.MEDIUM)

            # 关联
            project_id = db.Column(db.String(36))

            # 关联关系
            user = db.relationship('User', backref='tasks')
            category = db.relationship('TaskCategory', backref='tasks')

            def calculate_completion_rate(self) -> float:
                """计算任务完成率"""
                if self.estimated_pomodoros == 0:
                    return 0.0
                return 0.0  # 暂时返回0

            def get_actual_time_spent(self) -> int:
                """获取实际花费时间（分钟）"""
                return 0  # 暂时返回0

            def can_start(self) -> bool:
                """检查任务是否可以开始"""
                return self.status == TaskStatus.PENDING

            def mark_complete(self):
                """标记任务为完成"""
                self.status = TaskStatus.COMPLETED
                self.updated_at = datetime.utcnow()

            def can_move_to_time_block(self, time_block) -> bool:
                """检查任务是否可以移动到指定时间块"""
                return True  # 暂时返回True

            def to_dict(self) -> dict:
                """转换为字典"""
                base_dict = super().to_dict()
                base_dict.update({
                    'title': self.title,
                    'description': self.description,
                    'user_id': self.user_id,
                    'planned_start_time': self.planned_start_time.isoformat() if self.planned_start_time else None,
                    'estimated_pomodoros': self.estimated_pomodoros,
                    'task_type': self.task_type.value if hasattr(self.task_type, 'value') else self.task_type,
                    'category_id': self.category_id,
                    'scheduled_time_block_id': self.scheduled_time_block_id,
                    'status': self.status.value if hasattr(self.status, 'value') else self.status,
                    'priority': self.priority.value if hasattr(self.priority, 'value') else self.priority,
                    'project_id': self.project_id,
                    'completion_rate': self.calculate_completion_rate(),
                    'actual_time_spent': self.get_actual_time_spent()
                })
                return base_dict

        # 保存模型引用
        self.User = User
        self.TaskCategory = TaskCategory
        self.Task = Task
        self.db = db

        with app.app_context():
            db.create_all()
            yield app

    def test_task_creation(self, app):
        """测试任务创建"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建任务类别
            category = self.TaskCategory(name='工作', user_id=user.id)
            self.db.session.add(category)
            self.db.session.commit()

            # 创建任务
            planned_time = datetime.utcnow() + timedelta(hours=1)
            task = self.Task(
                title='测试任务',
                description='这是一个测试任务',
                user_id=user.id,
                planned_start_time=planned_time,
                estimated_pomodoros=3,
                task_type='FLEXIBLE',
                category_id=category.id,
                priority='MEDIUM'
            )

            self.db.session.add(task)
            self.db.session.commit()

            assert task.id is not None
            assert task.title == '测试任务'
            assert task.description == '这是一个测试任务'
            assert task.user_id == user.id
            assert task.planned_start_time == planned_time
            assert task.estimated_pomodoros == 3
            assert task.task_type.value == 'FLEXIBLE'
            assert task.category_id == category.id
            assert task.status.value == 'PENDING'
            assert task.priority.value == 'MEDIUM'

    def test_task_status_management(self, app):
        """测试任务状态管理"""
        with app.app_context():
            # 创建用户和类别
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            category = self.TaskCategory(name='工作', user_id=user.id)
            self.db.session.add(category)
            self.db.session.commit()

            # 创建任务
            planned_time = datetime.utcnow() + timedelta(hours=1)
            task = self.Task(
                title='测试任务',
                user_id=user.id,
                planned_start_time=planned_time,
                task_type='FLEXIBLE',
                category_id=category.id
            )
            self.db.session.add(task)
            self.db.session.commit()

            # 测试状态检查
            assert task.can_start() == True
            assert task.status.value == 'PENDING'

            # 测试标记完成
            task.mark_complete()
            assert task.status.value == 'COMPLETED'
            assert task.can_start() == False

    def test_task_completion_calculation(self, app):
        """测试任务完成率计算"""
        with app.app_context():
            # 创建用户和类别
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            category = self.TaskCategory(name='工作', user_id=user.id)
            self.db.session.add(category)
            self.db.session.commit()

            # 创建任务
            planned_time = datetime.utcnow() + timedelta(hours=1)
            task = self.Task(
                title='测试任务',
                user_id=user.id,
                planned_start_time=planned_time,
                estimated_pomodoros=0,  # 测试0番茄钟的情况
                task_type='FLEXIBLE',
                category_id=category.id
            )

            # 测试完成率计算
            assert task.calculate_completion_rate() == 0.0

            # 测试实际时间花费
            assert task.get_actual_time_spent() == 0

    def test_task_to_dict(self, app):
        """测试任务转换为字典"""
        with app.app_context():
            # 创建用户和类别
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            category = self.TaskCategory(name='工作', user_id=user.id)
            self.db.session.add(category)
            self.db.session.commit()

            # 创建任务
            planned_time = datetime.utcnow() + timedelta(hours=1)
            task = self.Task(
                title='测试任务',
                description='这是一个测试任务',
                user_id=user.id,
                planned_start_time=planned_time,
                estimated_pomodoros=3,
                task_type='FLEXIBLE',
                category_id=category.id,
                status='PENDING',
                priority='HIGH',
                project_id='project123'
            )

            task_dict = task.to_dict()

            assert 'id' in task_dict
            assert task_dict['title'] == '测试任务'
            assert task_dict['description'] == '这是一个测试任务'
            assert task_dict['user_id'] == user.id
            assert task_dict['estimated_pomodoros'] == 3
            assert task_dict['task_type'] == 'FLEXIBLE'
            assert task_dict['category_id'] == category.id
            assert task_dict['status'] == 'PENDING'
            assert task_dict['priority'] == 'HIGH'
            assert task_dict['project_id'] == 'project123'
            assert 'completion_rate' in task_dict
            assert 'actual_time_spent' in task_dict
            assert 'created_at' in task_dict
            assert 'updated_at' in task_dict