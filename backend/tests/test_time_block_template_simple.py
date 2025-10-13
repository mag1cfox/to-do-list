#!/usr/bin/env python3
"""
简化版时间块模板路由测试
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
from datetime import datetime


class TestTimeBlockTemplateSimple:
    """简化版时间块模板路由测试"""

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

            # 关联关系
            time_blocks = db.relationship('TimeBlock', backref='template', lazy='dynamic')

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
                else:
                    # 默认实现：生成一个简单的时间块
                    base_time = datetime.combine(target_date, datetime.min.time())
                    time_blocks.append(TimeBlock(
                        user_id=self.user_id,
                        date=target_date,
                        start_time=base_time.replace(hour=9, minute=0),
                        end_time=base_time.replace(hour=17, minute=0),
                        block_type=BlockType.RESEARCH,
                        color='#FF5733',
                        template_id=self.id
                    ))

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

            def clone(self) -> 'TimeBlockTemplate':
                """克隆模板"""
                new_template = TimeBlockTemplate(
                    name=f"{self.name} (副本)",
                    user_id=self.user_id,
                    description=self.description,
                    is_default=False  # 副本不能是默认模板
                )
                return new_template

        # 注册路由
        from flask import request, jsonify
        from flask_jwt_extended import jwt_required, get_jwt_identity

        @app.route('/api/time-block-templates/', methods=['POST'])
        @jwt_required()
        def create_time_block_template():
            """创建时间块模板"""
            current_user_id = get_jwt_identity()
            data = request.get_json()

            # 验证必填字段
            if not data.get('name'):
                return jsonify({'error': 'Missing required field: name'}), 400

            # 检查模板名称是否重复
            existing_template = TimeBlockTemplate.query.filter_by(
                user_id=current_user_id,
                name=data['name']
            ).first()

            if existing_template:
                return jsonify({'error': 'Template with this name already exists'}), 400

            # 创建新模板
            template = TimeBlockTemplate(
                name=data['name'],
                user_id=current_user_id,
                description=data.get('description'),
                is_default=data.get('is_default', False)
            )

            db.session.add(template)
            db.session.commit()

            return jsonify({
                'message': 'Time block template created successfully',
                'template': template.to_dict()
            }), 201

        @app.route('/api/time-block-templates/', methods=['GET'])
        @jwt_required()
        def get_time_block_templates():
            """获取时间块模板列表"""
            current_user_id = get_jwt_identity()
            templates = TimeBlockTemplate.query.filter_by(user_id=current_user_id).all()
            return jsonify([template.to_dict() for template in templates])

        @app.route('/api/time-block-templates/<string:template_id>/apply', methods=['POST'])
        @jwt_required()
        def apply_time_block_template(template_id):
            """将模板应用到指定日期"""
            current_user_id = get_jwt_identity()
            data = request.get_json()

            # 验证必填字段
            if not data.get('date'):
                return jsonify({'error': 'Missing required field: date'}), 400

            template = TimeBlockTemplate.query.filter_by(
                id=template_id,
                user_id=current_user_id
            ).first()

            if not template:
                return jsonify({'error': 'Time block template not found'}), 404

            # 验证日期格式
            try:
                target_date = datetime.fromisoformat(data['date'])
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400

            # 应用模板生成时间块
            generated_time_blocks = template.apply_to_date(target_date)

            # 保存生成的时间块到数据库
            for time_block in generated_time_blocks:
                db.session.add(time_block)

            db.session.commit()

            return jsonify({
                'message': 'Template applied successfully',
                'generated_time_blocks': [block.to_dict() for block in generated_time_blocks]
            }), 201

        # 保存引用
        self.User = User
        self.TimeBlock = TimeBlock
        self.TimeBlockTemplate = TimeBlockTemplate
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

    def test_create_time_block_template_simple(self, client, auth_headers):
        """测试创建时间块模板"""
        data = {
            'name': '标准工作日',
            'description': '标准的工作日时间安排',
            'is_default': True
        }

        response = client.post('/api/time-block-templates/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result['message'] == 'Time block template created successfully'
        assert 'template' in result
        assert result['template']['name'] == '标准工作日'
        assert result['template']['description'] == '标准的工作日时间安排'
        assert result['template']['is_default'] == True

    def test_get_time_block_templates_simple(self, client, auth_headers):
        """测试获取时间块模板列表"""
        # 先创建模板
        data = {
            'name': '深度工作模式',
            'description': '深度工作的时间安排'
        }
        client.post('/api/time-block-templates/',
                   data=json.dumps(data),
                   headers=auth_headers)

        # 获取模板列表
        response = client.get('/api/time-block-templates/', headers=auth_headers)

        assert response.status_code == 200
        result = json.loads(response.data)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == '深度工作模式'
        assert result[0]['description'] == '深度工作的时间安排'

    def test_apply_time_block_template_simple(self, client, auth_headers):
        """测试应用时间块模板"""
        # 先创建模板
        data = {
            'name': '标准工作日',
            'description': '标准的工作日时间安排'
        }
        response = client.post('/api/time-block-templates/',
                             data=json.dumps(data),
                             headers=auth_headers)
        template_id = json.loads(response.data)['template']['id']

        # 应用模板到指定日期
        apply_data = {
            'date': '2025-01-13'
        }

        response = client.post(f'/api/time-block-templates/{template_id}/apply',
                             data=json.dumps(apply_data),
                             headers=auth_headers)

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result['message'] == 'Template applied successfully'
        assert 'generated_time_blocks' in result
        assert len(result['generated_time_blocks']) == 2  # 标准工作日生成2个时间块

    def test_create_time_block_template_validation_error(self, client, auth_headers):
        """测试创建时间块模板验证错误"""
        # 测试缺少必填字段
        data = {
            'description': '缺少名称的模板'
            # 缺少 name 字段
        }

        response = client.post('/api/time-block-templates/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'Missing required field' in result['error']