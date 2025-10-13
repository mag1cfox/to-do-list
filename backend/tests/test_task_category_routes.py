#!/usr/bin/env python3
"""
任务类别路由集成测试
"""

import pytest
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from flask_jwt_extended import create_access_token


class TestTaskCategoryRoutes:
    """测试任务类别路由功能"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'

        with app.test_client() as client:
            with app.app_context():
                from app import db
                db.create_all()
                yield client

    @pytest.fixture
    def auth_headers(self):
        """创建认证头"""
        access_token = create_access_token(identity='test-user-id')
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def test_create_task_category(self, client, auth_headers):
        """测试创建任务类别"""
        data = {
            'name': '工作',
            'color': '#FF5733',
            'icon': 'work',
            'description': '工作相关任务'
        }

        response = client.post('/api/task-categories/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result['message'] == 'Task category created successfully'
        assert 'category' in result
        assert result['category']['name'] == '工作'
        assert result['category']['color'] == '#FF5733'

    def test_create_task_category_missing_fields(self, client, auth_headers):
        """测试缺少必填字段"""
        # 缺少名称
        data = {
            'color': '#FF5733'
        }

        response = client.post('/api/task-categories/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'Missing required field' in result['error']

        # 缺少颜色
        data = {
            'name': '工作'
        }

        response = client.post('/api/task-categories/',
                             data=json.dumps(data),
                             headers=auth_headers)

        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'Missing required field' in result['error']

    def test_get_task_categories(self, client, auth_headers):
        """测试获取任务类别列表"""
        # 先创建一些任务类别
        categories_data = [
            {'name': '工作', 'color': '#FF5733'},
            {'name': '学习', 'color': '#33FF57'},
            {'name': '健身', 'color': '#3357FF'}
        ]

        for category_data in categories_data:
            client.post('/api/task-categories/',
                       data=json.dumps(category_data),
                       headers=auth_headers)

        # 获取任务类别列表
        response = client.get('/api/task-categories/', headers=auth_headers)

        assert response.status_code == 200
        result = json.loads(response.data)
        assert isinstance(result, list)
        assert len(result) == 3

        # 验证返回的数据结构
        for category in result:
            assert 'id' in category
            assert 'name' in category
            assert 'color' in category
            assert 'user_id' in category
            assert 'task_count' in category
            assert 'total_time_spent' in category

    def test_get_single_task_category(self, client, auth_headers):
        """测试获取单个任务类别"""
        # 创建任务类别
        data = {
            'name': '工作',
            'color': '#FF5733'
        }

        create_response = client.post('/api/task-categories/',
                                    data=json.dumps(data),
                                    headers=auth_headers)
        category_id = json.loads(create_response.data)['category']['id']

        # 获取单个任务类别
        response = client.get(f'/api/task-categories/{category_id}', headers=auth_headers)

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['id'] == category_id
        assert result['name'] == '工作'
        assert result['color'] == '#FF5733'

    def test_get_nonexistent_task_category(self, client, auth_headers):
        """测试获取不存在的任务类别"""
        response = client.get('/api/task-categories/nonexistent-id', headers=auth_headers)

        assert response.status_code == 404
        result = json.loads(response.data)
        assert 'error' in result
        assert result['error'] == 'Task category not found'

    def test_update_task_category(self, client, auth_headers):
        """测试更新任务类别"""
        # 创建任务类别
        data = {
            'name': '工作',
            'color': '#FF5733'
        }

        create_response = client.post('/api/task-categories/',
                                    data=json.dumps(data),
                                    headers=auth_headers)
        category_id = json.loads(create_response.data)['category']['id']

        # 更新任务类别
        update_data = {
            'name': '新工作',
            'color': '#33FF57',
            'icon': 'new-work',
            'description': '新的工作类别'
        }

        response = client.put(f'/api/task-categories/{category_id}',
                            data=json.dumps(update_data),
                            headers=auth_headers)

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['message'] == 'Task category updated successfully'
        assert result['category']['name'] == '新工作'
        assert result['category']['color'] == '#33FF57'
        assert result['category']['icon'] == 'new-work'
        assert result['category']['description'] == '新的工作类别'

    def test_update_nonexistent_task_category(self, client, auth_headers):
        """测试更新不存在的任务类别"""
        update_data = {
            'name': '新名称',
            'color': '#FF5733'
        }

        response = client.put('/api/task-categories/nonexistent-id',
                            data=json.dumps(update_data),
                            headers=auth_headers)

        assert response.status_code == 404
        result = json.loads(response.data)
        assert 'error' in result
        assert result['error'] == 'Task category not found'

    def test_delete_task_category(self, client, auth_headers):
        """测试删除任务类别"""
        # 创建任务类别
        data = {
            'name': '工作',
            'color': '#FF5733'
        }

        create_response = client.post('/api/task-categories/',
                                    data=json.dumps(data),
                                    headers=auth_headers)
        category_id = json.loads(create_response.data)['category']['id']

        # 删除任务类别
        response = client.delete(f'/api/task-categories/{category_id}', headers=auth_headers)

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['message'] == 'Task category deleted successfully'

        # 验证已删除
        get_response = client.get(f'/api/task-categories/{category_id}', headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_nonexistent_task_category(self, client, auth_headers):
        """测试删除不存在的任务类别"""
        response = client.delete('/api/task-categories/nonexistent-id', headers=auth_headers)

        assert response.status_code == 404
        result = json.loads(response.data)
        assert 'error' in result
        assert result['error'] == 'Task category not found'