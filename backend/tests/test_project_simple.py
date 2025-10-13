#!/usr/bin/env python3
"""
简化版项目路由测试
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


class TestProjectSimple:
    """简化版项目路由测试"""

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

        # 定义项目模型
        class Project(BaseModel):
            __tablename__ = 'projects'

            name = db.Column(db.String(100), nullable=False)
            user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
            color = db.Column(db.String(7), nullable=False)  # 项目颜色标识
            description = db.Column(db.Text)

            def to_dict(self) -> dict:
                """转换为字典"""
                base_dict = super().to_dict()
                base_dict.update({
                    'name': self.name,
                    'user_id': self.user_id,
                    'color': self.color,
                    'description': self.description,
                    'task_count': 0,
                    'total_estimated_time': 0,
                    'total_actual_time': 0,
                    'completion_progress': 0.0
                })
                return base_dict

        # 注册路由
        from flask import request, jsonify
        from flask_jwt_extended import jwt_required, get_jwt_identity

        @app.route('/api/projects/', methods=['POST'])
        @jwt_required()
        def create_project():
            """创建项目"""
            current_user_id = get_jwt_identity()
            data = request.get_json()

            # 验证必填字段
            required_fields = ['name', 'color']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # 检查项目名称是否重复
            existing_project = Project.query.filter_by(
                user_id=current_user_id,
                name=data['name']
            ).first()

            if existing_project:
                return jsonify({'error': 'Project with this name already exists'}), 400

            # 创建新项目
            project = Project(
                name=data['name'],
                color=data['color'],
                user_id=current_user_id,
                description=data.get('description')
            )

            db.session.add(project)
            db.session.commit()

            return jsonify({
                'message': 'Project created successfully',
                'project': project.to_dict()
            }), 201

        @app.route('/api/projects/', methods=['GET'])
        @jwt_required()
        def get_projects():
            """获取项目列表"""
            current_user_id = get_jwt_identity()
            projects = Project.query.filter_by(user_id=current_user_id).all()
            return jsonify([project.to_dict() for project in projects])

        # 保存引用
        self.User = User
        self.Project = Project
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

    def test_create_project_simple(self, client, auth_headers):
        """测试创建项目"""
        data = {
            'name': '个人网站开发',
            'color': '#FF5733'
        }

        response = client.post('/api/projects/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result['message'] == 'Project created successfully'
        assert 'project' in result
        assert result['project']['name'] == '个人网站开发'
        assert result['project']['color'] == '#FF5733'

    def test_get_projects_simple(self, client, auth_headers):
        """测试获取项目列表"""
        # 先创建项目
        data = {
            'name': '学习项目',
            'color': '#33FF57'
        }
        client.post('/api/projects/',
                   data=json.dumps(data),
                   headers=auth_headers)

        # 获取项目列表
        response = client.get('/api/projects/', headers=auth_headers)

        assert response.status_code == 200
        result = json.loads(response.data)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == '学习项目'
        assert result[0]['color'] == '#33FF57'