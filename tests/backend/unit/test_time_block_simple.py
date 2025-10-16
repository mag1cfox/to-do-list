#!/usr/bin/env python3
"""
简化版时间块路由测试
"""

import pytest
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta


class TestTimeBlockSimple:
    """简化版时间块路由测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'

        db = SQLAlchemy(app)
        jwt = JWTManager(app)

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

        # 注册路由
        from flask import request, jsonify
        from flask_jwt_extended import jwt_required, get_jwt_identity

        @app.route('/api/time-blocks/', methods=['POST'])
        @jwt_required()
        def create_time_block():
            """创建时间块"""
            current_user_id = get_jwt_identity()
            data = request.get_json()

            # 验证必填字段
            required_fields = ['date', 'start_time', 'end_time', 'block_type', 'color']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # 验证时间格式
            try:
                date = datetime.fromisoformat(data['date'])
                start_time = datetime.fromisoformat(data['start_time'])
                end_time = datetime.fromisoformat(data['end_time'])
            except ValueError:
                return jsonify({'error': 'Invalid date/time format'}), 400

            # 验证开始时间早于结束时间
            if start_time >= end_time:
                return jsonify({'error': 'Start time must be before end time'}), 400

            # 创建新时间块
            time_block = TimeBlock(
                user_id=current_user_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                block_type=data['block_type'],
                color=data['color'],
                is_recurring=data.get('is_recurring', False),
                recurrence_pattern=data.get('recurrence_pattern'),
                template_id=data.get('template_id')
            )

            db.session.add(time_block)
            db.session.commit()

            return jsonify({
                'message': 'Time block created successfully',
                'time_block': time_block.to_dict()
            }), 201

        @app.route('/api/time-blocks/', methods=['GET'])
        @jwt_required()
        def get_time_blocks():
            """获取时间块列表"""
            current_user_id = get_jwt_identity()
            time_blocks = TimeBlock.query.filter_by(user_id=current_user_id).all()
            return jsonify([time_block.to_dict() for time_block in time_blocks])

        # 保存引用
        self.User = User
        self.TimeBlock = TimeBlock
        self.BlockType = BlockType
        self.db = db

        with app.app_context():
            db.create_all()
            yield app.test_client()

    @pytest.fixture
    def auth_headers(self):
        """创建认证头"""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity='test-user-id')
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def test_create_time_block_simple(self, client, auth_headers):
        """测试创建时间块"""
        now = datetime.utcnow()
        data = {
            'date': now.date().isoformat(),
            'start_time': now.isoformat(),
            'end_time': (now + timedelta(hours=1)).isoformat(),
            'block_type': 'RESEARCH',
            'color': '#FF5733'
        }

        response = client.post('/api/time-blocks/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result['message'] == 'Time block created successfully'
        assert 'time_block' in result
        assert result['time_block']['block_type'] == 'RESEARCH'
        assert result['time_block']['color'] == '#FF5733'
        assert 'duration' in result['time_block']

    def test_get_time_blocks_simple(self, client, auth_headers):
        """测试获取时间块列表"""
        # 先创建时间块
        now = datetime.utcnow()
        data = {
            'date': now.date().isoformat(),
            'start_time': now.isoformat(),
            'end_time': (now + timedelta(hours=2)).isoformat(),
            'block_type': 'GROWTH',
            'color': '#33FF57'
        }
        client.post('/api/time-blocks/',
                   data=json.dumps(data),
                   headers=auth_headers)

        # 获取时间块列表
        response = client.get('/api/time-blocks/', headers=auth_headers)

        assert response.status_code == 200
        result = json.loads(response.data)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['block_type'] == 'GROWTH'
        assert result[0]['color'] == '#33FF57'

    def test_create_time_block_validation_error(self, client, auth_headers):
        """测试创建时间块验证错误"""
        now = datetime.utcnow()

        # 测试缺少必填字段
        data = {
            'date': now.date().isoformat(),
            'start_time': now.isoformat(),
            # 缺少 end_time
            'block_type': 'RESEARCH',
            'color': '#FF5733'
        }

        response = client.post('/api/time-blocks/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'Missing required field' in result['error']

    def test_create_time_block_time_validation(self, client, auth_headers):
        """测试时间验证"""
        now = datetime.utcnow()

        # 测试开始时间晚于结束时间
        data = {
            'date': now.date().isoformat(),
            'start_time': (now + timedelta(hours=1)).isoformat(),
            'end_time': now.isoformat(),  # 开始时间晚于结束时间
            'block_type': 'RESEARCH',
            'color': '#FF5733'
        }

        response = client.post('/api/time-blocks/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'Start time must be before end time' in result['error']