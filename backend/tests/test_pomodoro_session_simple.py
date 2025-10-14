import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from config import TestingConfig
from models.user import User
from models.task import Task
from models.task_category import TaskCategory

class TestPomodoroSessionSimple:
    """PomodoroSession路由简化测试"""

    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = create_app(TestingConfig)
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()

    @pytest.fixture
    def auth_headers(self, client):
        """创建认证头"""
        # 创建测试用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # 登录获取token
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        token = response.get_json()['access_token']

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    @pytest.fixture
    def test_task(self, auth_headers):
        """创建测试任务"""
        # 创建任务类别
        category = TaskCategory(name='测试类别', user_id=1, color='#FF0000')
        db.session.add(category)
        db.session.commit()

        # 创建任务
        task = Task(
            title='测试任务',
            description='测试任务描述',
            user_id=1,
            category_id=category.id,
            task_type='FLEXIBLE',
            status='PENDING',
            priority='MEDIUM'
        )
        db.session.add(task)
        db.session.commit()

        return task

    def test_create_pomodoro_session_simple(self, client, auth_headers, test_task):
        """测试创建番茄钟会话API"""
        response = client.post('/api/pomodoro-sessions',
            json={'task_id': test_task.id},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == '番茄钟会话创建成功'
        assert 'pomodoro_session' in data

        session_data = data['pomodoro_session']
        assert session_data['task_id'] == test_task.id
        assert session_data['status'] == 'PLANNED'
        assert session_data['session_type'] == 'FOCUS'

    def test_get_pomodoro_sessions_simple(self, client, auth_headers, test_task):
        """测试获取番茄钟会话列表API"""
        # 先创建一个会话
        client.post('/api/pomodoro-sessions',
            json={'task_id': test_task.id},
            headers=auth_headers
        )

        response = client.get('/api/pomodoro-sessions', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'pomodoro_sessions' in data
        assert len(data['pomodoro_sessions']) == 1

    def test_start_pomodoro_session_simple(self, client, auth_headers, test_task):
        """测试开始番茄钟会话API"""
        # 先创建一个会话
        create_response = client.post('/api/pomodoro-sessions',
            json={'task_id': test_task.id},
            headers=auth_headers
        )
        session_id = create_response.get_json()['pomodoro_session']['id']

        # 开始会话
        response = client.post(f'/api/pomodoro-sessions/{session_id}/start',
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == '番茄钟会话已开始'
        assert data['pomodoro_session']['status'] == 'IN_PROGRESS'

    def test_complete_pomodoro_session_simple(self, client, auth_headers, test_task):
        """测试完成番茄钟会话API"""
        # 先创建并开始一个会话
        create_response = client.post('/api/pomodoro-sessions',
            json={'task_id': test_task.id},
            headers=auth_headers
        )
        session_id = create_response.get_json()['pomodoro_session']['id']

        client.post(f'/api/pomodoro-sessions/{session_id}/start', headers=auth_headers)

        # 完成会话
        response = client.post(f'/api/pomodoro-sessions/{session_id}/complete',
            json={'completion_summary': '任务完成'},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == '番茄钟会话已完成'
        assert data['pomodoro_session']['status'] == 'COMPLETED'
        assert data['pomodoro_session']['completion_summary'] == '任务完成'

    def test_get_active_pomodoro_session_simple(self, client, auth_headers, test_task):
        """测试获取活跃番茄钟会话API"""
        # 没有活跃会话
        response = client.get('/api/pomodoro-sessions/active', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == '没有活跃的番茄钟会话'

        # 创建并开始一个会话
        create_response = client.post('/api/pomodoro-sessions',
            json={'task_id': test_task.id},
            headers=auth_headers
        )
        session_id = create_response.get_json()['pomodoro_session']['id']

        client.post(f'/api/pomodoro-sessions/{session_id}/start', headers=auth_headers)

        # 获取活跃会话
        response = client.get('/api/pomodoro-sessions/active', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'active_session' in data
        assert data['active_session']['id'] == session_id
        assert data['active_session']['status'] == 'IN_PROGRESS'

    def test_create_pomodoro_session_validation_error(self, client, auth_headers):
        """测试创建番茄钟会话验证错误"""
        # 缺少task_id
        response = client.post('/api/pomodoro-sessions',
            json={},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert '必须提供task_id' in data['error']

    def test_create_pomodoro_session_task_not_found(self, client, auth_headers):
        """测试任务不存在的情况"""
        response = client.post('/api/pomodoro-sessions',
            json={'task_id': 999},
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert '任务不存在或无权限访问' in data['error']

    def test_pomodoro_session_with_break_type(self, client, auth_headers, test_task):
        """测试创建休息类型会话"""
        response = client.post('/api/pomodoro-sessions',
            json={
                'task_id': test_task.id,
                'session_type': 'BREAK',
                'planned_duration': 5
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        session_data = data['pomodoro_session']
        assert session_data['session_type'] == 'BREAK'
        assert session_data['planned_duration'] == 5

    def test_pomodoro_session_invalid_session_type(self, client, auth_headers, test_task):
        """测试无效的会话类型"""
        response = client.post('/api/pomodoro-sessions',
            json={
                'task_id': test_task.id,
                'session_type': 'INVALID'
            },
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert '无效的会话类型' in data['error']