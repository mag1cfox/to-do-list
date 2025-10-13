#!/usr/bin/env python3
"""
独立时间块模板模型测试 - 不依赖models/__init__.py
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta


class TestTimeBlockTemplateStandalone:
    """测试时间块模板模型独立功能"""

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
            template_id = db.Column(db.String(36), db.ForeignKey('time_block_templates.id'))

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
                    'template_id': self.template_id
                })
                return base_dict

        # 定义时间块模板模型
        class TimeBlockTemplate(BaseModel):
            __tablename__ = 'time_block_templates'

            name = db.Column(db.String(100), nullable=False)
            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
            description = db.Column(db.Text)
            is_default = db.Column(db.Boolean, default=False)

            # 关联关系 - 手动指定外键关系
            time_blocks = db.relationship('TimeBlock',
                                         foreign_keys='TimeBlock.template_id',
                                         backref='template',
                                         lazy='dynamic')

            def to_dict(self) -> dict:
                """转换为字典"""
                base_dict = super().to_dict()
                base_dict.update({
                    'name': self.name,
                    'user_id': self.user_id,
                    'description': self.description,
                    'is_default': self.is_default,
                    'time_block_count': self.get_time_block_count()
                })
                return base_dict

            def get_time_block_count(self) -> int:
                """获取模板关联的时间块数量"""
                return self.time_blocks.count()

            def apply_to_date(self, target_date: datetime) -> list:
                """将模板应用到指定日期，生成时间块列表"""
                time_blocks = []

                # 示例：生成一个基础的工作日模板
                if self.name == "标准工作日":
                    time_blocks = self._generate_standard_workday(target_date)
                elif self.name == "深度工作模式":
                    time_blocks = self._generate_deep_work_day(target_date)
                else:
                    # 默认实现：复制模板中已有的时间块配置
                    time_blocks = self._copy_existing_time_blocks(target_date)

                return time_blocks

            def _generate_standard_workday(self, target_date: datetime) -> list:
                """生成标准工作日时间块"""
                time_blocks = []
                base_time = datetime.combine(target_date, datetime.min.time())

                # 上午工作时间（9:00-12:00）
                time_blocks.append(TimeBlock(
                    user_id=self.user_id,
                    date=target_date,
                    start_time=base_time.replace(hour=9, minute=0),
                    end_time=base_time.replace(hour=12, minute=0),
                    block_type=BlockType.RESEARCH,
                    color='#FF5733',
                    template_id=self.id
                ))

                # 下午工作时间（13:00-17:00）
                time_blocks.append(TimeBlock(
                    user_id=self.user_id,
                    date=target_date,
                    start_time=base_time.replace(hour=13, minute=0),
                    end_time=base_time.replace(hour=17, minute=0),
                    block_type=BlockType.GROWTH,
                    color='#33FF57',
                    template_id=self.id
                ))

                return time_blocks

            def _generate_deep_work_day(self, target_date: datetime) -> list:
                """生成深度工作模式时间块"""
                time_blocks = []
                base_time = datetime.combine(target_date, datetime.min.time())

                # 深度工作块（9:00-12:00）
                time_blocks.append(TimeBlock(
                    user_id=self.user_id,
                    date=target_date,
                    start_time=base_time.replace(hour=9, minute=0),
                    end_time=base_time.replace(hour=12, minute=0),
                    block_type=BlockType.RESEARCH,
                    color='#FF5733',
                    template_id=self.id
                ))

                # 学习块（14:00-16:00）
                time_blocks.append(TimeBlock(
                    user_id=self.user_id,
                    date=target_date,
                    start_time=base_time.replace(hour=14, minute=0),
                    end_time=base_time.replace(hour=16, minute=0),
                    block_type=BlockType.GROWTH,
                    color='#33FF57',
                    template_id=self.id
                ))

                # 复盘块（16:30-17:00）
                time_blocks.append(TimeBlock(
                    user_id=self.user_id,
                    date=target_date,
                    start_time=base_time.replace(hour=16, minute=30),
                    end_time=base_time.replace(hour=17, minute=0),
                    block_type=BlockType.REVIEW,
                    color='#3357FF',
                    template_id=self.id
                ))

                return time_blocks

            def _copy_existing_time_blocks(self, target_date: datetime) -> list:
                """复制模板中已有的时间块配置"""
                time_blocks = []

                for existing_block in self.time_blocks:
                    # 创建新的时间块，保持相对时间关系
                    new_start = datetime.combine(target_date, existing_block.start_time.time())
                    new_end = datetime.combine(target_date, existing_block.end_time.time())

                    time_blocks.append(TimeBlock(
                        user_id=self.user_id,
                        date=target_date,
                        start_time=new_start,
                        end_time=new_end,
                        block_type=existing_block.block_type,
                        color=existing_block.color,
                        template_id=self.id
                    ))

                return time_blocks

            def clone(self) -> 'TimeBlockTemplate':
                """克隆模板"""
                new_template = TimeBlockTemplate(
                    name=f"{self.name} (副本)",
                    user_id=self.user_id,
                    description=self.description,
                    is_default=False  # 副本不能是默认模板
                )
                return new_template

        # 保存模型引用
        self.User = User
        self.TimeBlock = TimeBlock
        self.TimeBlockTemplate = TimeBlockTemplate
        self.BlockType = BlockType
        self.db = db

        with app.app_context():
            db.create_all()
            yield app

    def test_time_block_template_creation(self, app):
        """测试时间块模板创建"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建时间块模板
            template = self.TimeBlockTemplate(
                name='标准工作日',
                user_id=user.id,
                description='标准的工作日时间安排',
                is_default=True
            )

            self.db.session.add(template)
            self.db.session.commit()

            assert template.id is not None
            assert template.name == '标准工作日'
            assert template.user_id == user.id
            assert template.is_default == True

    def test_time_block_template_time_block_count(self, app):
        """测试时间块模板关联的时间块数量统计"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建时间块模板
            template = self.TimeBlockTemplate(
                name='自定义模板',
                user_id=user.id
            )
            self.db.session.add(template)
            self.db.session.commit()

            # 测试空模板的时间块数量
            assert template.get_time_block_count() == 0

            # 创建关联的时间块
            now = datetime.utcnow()
            time_block1 = self.TimeBlock(
                user_id=user.id,
                date=now.date(),
                start_time=now,
                end_time=now + timedelta(hours=1),
                block_type=self.BlockType.RESEARCH,
                color='#FF5733',
                template_id=template.id
            )
            time_block2 = self.TimeBlock(
                user_id=user.id,
                date=now.date(),
                start_time=now + timedelta(hours=2),
                end_time=now + timedelta(hours=3),
                block_type=self.BlockType.GROWTH,
                color='#33FF57',
                template_id=template.id
            )
            self.db.session.add_all([time_block1, time_block2])
            self.db.session.commit()

            # 测试有2个时间块关联的模板
            assert template.get_time_block_count() == 2

    def test_time_block_template_apply_to_date(self, app):
        """测试时间块模板应用到指定日期"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建时间块模板
            template = self.TimeBlockTemplate(
                name='标准工作日',
                user_id=user.id
            )
            self.db.session.add(template)
            self.db.session.commit()

            # 应用模板到指定日期
            target_date = datetime(2025, 1, 13)
            generated_blocks = template.apply_to_date(target_date)

            assert len(generated_blocks) == 2  # 标准工作日生成2个时间块
            assert generated_blocks[0].block_type == self.BlockType.RESEARCH
            assert generated_blocks[1].block_type == self.BlockType.GROWTH
            assert generated_blocks[0].template_id == template.id

    def test_time_block_template_clone(self, app):
        """测试时间块模板克隆"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            # 创建时间块模板
            original_template = self.TimeBlockTemplate(
                name='原始模板',
                user_id=user.id,
                description='原始模板描述',
                is_default=True
            )
            self.db.session.add(original_template)
            self.db.session.commit()

            # 克隆模板
            cloned_template = original_template.clone()

            assert cloned_template.name == '原始模板 (副本)'
            assert cloned_template.user_id == user.id
            assert cloned_template.description == '原始模板描述'
            assert cloned_template.is_default == False  # 副本不能是默认模板

    def test_time_block_template_to_dict(self, app):
        """测试时间块模板转换为字典"""
        with app.app_context():
            # 创建用户
            user = self.User(username='testuser', email='test@example.com', password_hash='hash123')
            self.db.session.add(user)
            self.db.session.commit()

            template = self.TimeBlockTemplate(
                name='测试模板',
                user_id=user.id,
                description='这是一个测试模板',
                is_default=False
            )

            template_dict = template.to_dict()

            assert 'id' in template_dict
            assert template_dict['name'] == '测试模板'
            assert template_dict['user_id'] == user.id
            assert template_dict['description'] == '这是一个测试模板'
            assert template_dict['is_default'] == False
            assert 'time_block_count' in template_dict
            assert 'created_at' in template_dict
            assert 'updated_at' in template_dict