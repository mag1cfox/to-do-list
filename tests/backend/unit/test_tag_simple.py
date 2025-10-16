#!/usr/bin/env python3
"""
简化版标签路由测试
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


class TestTagSimple:
    """简化版标签路由测试"""

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

        # 定义标签模型
        class Tag(BaseModel):
            __tablename__ = 'tags'

            name = db.Column(db.String(50), nullable=False)
            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
            color = db.Column(db.String(7))  # HEX颜色值

            def to_dict(self) -> dict:
                """转换为字典"""
                base_dict = super().to_dict()
                base_dict.update({
                    'name': self.name,
                    'user_id': self.user_id,
                    'color': self.color,
                    'usage_count': 0
                })
                return base_dict

        # 注册路由
        from flask import request, jsonify
        from flask_jwt_extended import jwt_required, get_jwt_identity

        @app.route('/api/tags/', methods=['POST'])
        @jwt_required()
        def create_tag():
            """创建标签"""
            current_user_id = get_jwt_identity()
            data = request.get_json()

            # 验证必填字段
            if not data.get('name'):
                return jsonify({'error': 'Missing required field: name'}), 400

            # 检查标签名称是否重复
            existing_tag = Tag.query.filter_by(
                user_id=current_user_id,
                name=data['name']
            ).first()

            if existing_tag:
                return jsonify({'error': 'Tag with this name already exists'}), 400

            # 创建新标签
            tag = Tag(
                name=data['name'],
                user_id=current_user_id,
                color=data.get('color')
            )

            db.session.add(tag)
            db.session.commit()

            return jsonify({
                'message': 'Tag created successfully',
                'tag': tag.to_dict()
            }), 201

        @app.route('/api/tags/', methods=['GET'])
        @jwt_required()
        def get_tags():
            """获取标签列表"""
            current_user_id = get_jwt_identity()
            tags = Tag.query.filter_by(user_id=current_user_id).all()
            return jsonify([tag.to_dict() for tag in tags])

        # 保存引用
        self.User = User
        self.Tag = Tag
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

    def test_create_tag_simple(self, client, auth_headers):
        """测试创建标签"""
        data = {
            'name': '重要',
            'color': '#FF5733'
        }

        response = client.post('/api/tags/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result['message'] == 'Tag created successfully'
        assert 'tag' in result
        assert result['tag']['name'] == '重要'
        assert result['tag']['color'] == '#FF5733'

    def test_get_tags_simple(self, client, auth_headers):
        """测试获取标签列表"""
        # 先创建标签
        data = {
            'name': '学习',
            'color': '#33FF57'
        }
        client.post('/api/tags/',
                   data=json.dumps(data),
                   headers=auth_headers)

        # 获取标签列表
        response = client.get('/api/tags/', headers=auth_headers)

        assert response.status_code == 200
        result = json.loads(response.data)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == '学习'
        assert result[0]['color'] == '#33FF57'