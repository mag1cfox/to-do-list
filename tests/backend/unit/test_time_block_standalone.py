#!/usr/bin/env python3
"""
独立时间块模型测试 - 不依赖models/__init__.py
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta


class TestTimeBlockStandalone:
    """测试时间块模型独立功能"""

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

        # 定义时间块类型枚举
        class BlockType:
            RESEARCH = 'RESEARCH'
            GROWTH = 'GROWTH'
            REST = 'REST'
            ENTERTAINMENT = 'ENTERTAINMENT'
            REVIEW = 'REVIEW'

        # 定义时间块模型
        class TimeBlock(BaseModel):
            __tablename__ = 'time_blocks'

            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
            date = db.Column(db.DateTime, nullable=False)
            start_time = db.Column(db.DateTime, nullable=False)
            end_time = db.Column(db.DateTime, nullable=False)
            block_type = db.Column(db.String(20), nullable=False)
            color = db.Column(db.String(7), nullable=False)
            is_recurring = db.Column(db.Boolean, default=False)
            recurrence_pattern = db.Column(db.String(100))
            template_id = db.Column(db.String(36))

            def to_dict(self) -> dict:
                """转换为字典"""
                base_dict = super().to_dict()
                base_dict.update({
                    'user_id': self.user_id,
                    'date': self.date.isoformat() if self.date else None,
                    'start_time': self.start_time.isoformat() if self.start_time else None,
                    'end_time': self.end_time.isoformat() if self.end_time else None,
                    'block_type': self.block_type,
                    'color': self.color,
                    'is_recurring': self.is_recurring,
                    'recurrence_pattern': self.recurrence_pattern,
                    'template_id': self.template_id,
                    'duration': self.get_duration(),
                    'is_active': self.is_active()
                })
                return base_dict

            def get_duration(self) -> int:
                """获取时间块持续时间（分钟）"""
                if self.start_time and self.end_time:
                    duration = (self.end_time - self.start_time).total_seconds() / 60
                    return int(duration)
                return 0

            def is_active(self) -> bool:
                """检查时间块是否处于活跃状态"""
                now = datetime.utcnow()
                return self.start_time <= now <= self.end_time if self.start_time and self.end_time else False

            def overlaps_with(self, other: 'TimeBlock') -> bool:
                """检查与另一个时间块是否重叠"""
                if not self.start_time or not self.end_time or not other.start_time or not other.end_time:
                    return False
                return self.start_time < other.end_time and other.start_time < self.end_time

            def can_accommodate_task(self, task_duration: int) -> bool:
                """检查时间块是否能容纳指定时长的任务"""
                block_duration = self.get_duration()
                return block_duration >= task_duration

        # 保存模型引用
        self.User = User
        self.TimeBlock = TimeBlock
        self.BlockType = BlockType
        self.db = db

        with app.app_context():
            db.create_all()
            yield app

    def test_time_block_creation(self, app):
        """测试时间块创建"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建时间块
            now = datetime.utcnow()
            time_block = self.TimeBlock(
                user_id=user.id,
                date=now.date(),
                start_time=now,
                end_time=now + timedelta(hours=1),
                block_type=self.BlockType.RESEARCH,
                color='#FF5733'
            )

            self.db.session.add(time_block)
            self.db.session.commit()

            assert time_block.id is not None
            assert time_block.user_id == user.id
            assert time_block.block_type == self.BlockType.RESEARCH
            assert time_block.color == '#FF5733'

    def test_time_block_duration_calculation(self, app):
        """测试时间块持续时间计算"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建2小时的时间块
            now = datetime.utcnow()
            time_block = self.TimeBlock(
                user_id=user.id,
                date=now.date(),
                start_time=now,
                end_time=now + timedelta(hours=2),
                block_type=self.BlockType.GROWTH,
                color='#33FF57'
            )

            duration = time_block.get_duration()
            assert duration == 120  # 2小时 = 120分钟

    def test_time_block_overlap_detection(self, app):
        """测试时间块重叠检测"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            now = datetime.utcnow()

            # 创建第一个时间块
            block1 = self.TimeBlock(
                user_id=user.id,
                date=now.date(),
                start_time=now,
                end_time=now + timedelta(hours=1),
                block_type=self.BlockType.RESEARCH,
                color='#FF5733'
            )

            # 创建重叠的时间块
            block2 = self.TimeBlock(
                user_id=user.id,
                date=now.date(),
                start_time=now + timedelta(minutes=30),
                end_time=now + timedelta(hours=1, minutes=30),
                block_type=self.BlockType.GROWTH,
                color='#33FF57'
            )

            # 创建不重叠的时间块
            block3 = self.TimeBlock(
                user_id=user.id,
                date=now.date(),
                start_time=now + timedelta(hours=2),
                end_time=now + timedelta(hours=3),
                block_type=self.BlockType.REST,
                color='#3357FF'
            )

            # 测试重叠检测
            assert block1.overlaps_with(block2) == True
            assert block2.overlaps_with(block1) == True
            assert block1.overlaps_with(block3) == False
            assert block3.overlaps_with(block1) == False

    def test_time_block_task_accommodation(self, app):
        """测试时间块任务容纳能力"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            now = datetime.utcnow()

            # 创建1小时的时间块
            time_block = self.TimeBlock(
                user_id=user.id,
                date=now.date(),
                start_time=now,
                end_time=now + timedelta(hours=1),
                block_type=self.BlockType.RESEARCH,
                color='#FF5733'
            )

            # 测试任务容纳能力
            assert time_block.can_accommodate_task(30) == True   # 30分钟任务
            assert time_block.can_accommodate_task(60) == True   # 60分钟任务
            assert time_block.can_accommodate_task(90) == False  # 90分钟任务

    def test_time_block_to_dict(self, app):
        """测试时间块转换为字典"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            now = datetime.utcnow()
            time_block = self.TimeBlock(
                user_id=user.id,
                date=now.date(),
                start_time=now,
                end_time=now + timedelta(hours=1),
                block_type=self.BlockType.REVIEW,
                color='#FF33FF'
            )

            time_block_dict = time_block.to_dict()

            assert 'id' in time_block_dict
            assert time_block_dict['user_id'] == user.id
            assert time_block_dict['block_type'] == self.BlockType.REVIEW
            assert time_block_dict['color'] == '#FF33FF'
            assert 'duration' in time_block_dict
            assert 'is_active' in time_block_dict
            assert 'created_at' in time_block_dict
            assert 'updated_at' in time_block_dict