#!/usr/bin/env python3
"""
生产力分析API测试脚本
测试任务、番茄钟会话、时间块等API端点，为生产力分析功能提供数据验证
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from app import create_app, db
from config import TestingConfig
from models.user import User
from models.task import Task, TaskStatus, TaskType, PriorityLevel
from models.task_category import TaskCategory
from models.project import Project
from models.pomodoro_session import PomodoroSession, SessionStatus, SessionType
from models.time_block import TimeBlock, BlockType
from flask_jwt_extended import create_access_token


@pytest.fixture
def app():
    """创建测试应用实例"""
    # 设置测试环境变量
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """创建测试用户"""
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash='hashed_password'
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_headers(test_user):
    """生成认证头"""
    access_token = create_access_token(identity=test_user.id)
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_data(app, test_user):
    """创建示例数据用于生产力分析测试"""
    # 创建任务分类
    category = TaskCategory(
        name='工作',
        description='工作相关任务',
        user_id=test_user.id,
        color='#1890ff'
    )
    db.session.add(category)

    # 创建项目
    project = Project(
        name='生产力分析项目',
        description='用于测试生产力分析功能',
        user_id=test_user.id,
        color='#52c41a'
    )
    db.session.add(project)

    # 先提交category和project以获取ID
    db.session.flush()

    # 创建任务
    tasks = []
    task_data = [
        {
            'title': '完成API文档',
            'description': '编写API接口文档',
            'status': TaskStatus.COMPLETED,
            'priority': PriorityLevel.HIGH,
            'task_type': TaskType.RIGID,
            'estimated_pomodoros': 3
        },
        {
            'title': '代码审查',
            'description': '审查团队代码',
            'status': TaskStatus.IN_PROGRESS,
            'priority': PriorityLevel.MEDIUM,
            'task_type': TaskType.FLEXIBLE,
            'estimated_pomodoros': 2
        },
        {
            'title': '学习新技术',
            'description': '学习React新特性',
            'status': TaskStatus.PENDING,
            'priority': PriorityLevel.LOW,
            'task_type': TaskType.FLEXIBLE,
            'estimated_pomodoros': 1
        }
    ]

    for i, data in enumerate(task_data):
        task = Task(
            title=data['title'],
            description=data['description'],
            status=data['status'],
            priority=data['priority'],
            task_type=data['task_type'],
            estimated_pomodoros=data['estimated_pomodoros'],
            user_id=test_user.id,
            category_id=category.id,
            project_id=project.id,
            planned_start_time=datetime.now() + timedelta(hours=i)
        )
        tasks.append(task)
        db.session.add(task)

    # 创建时间块
    time_blocks = []
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    block_configs = [
        {'type': BlockType.RESEARCH, 'start': 0, 'duration': 2},      # 9:00-11:00
        {'type': BlockType.GROWTH, 'start': 2, 'duration': 1},        # 11:00-12:00
        {'type': BlockType.REST, 'start': 4, 'duration': 1},          # 13:00-14:00
        {'type': BlockType.RESEARCH, 'start': 5, 'duration': 2},      # 14:00-16:00
        {'type': BlockType.REVIEW, 'start': 7, 'duration': 1},        # 16:00-17:00
    ]

    for config in block_configs:
        start_time = base_date + timedelta(hours=config['start'])
        end_time = start_time + timedelta(hours=config['duration'])

        time_block = TimeBlock(
            user_id=test_user.id,
            date=base_date.date(),
            start_time=start_time,
            end_time=end_time,
            block_type=config['type'],
            color='#1890ff'
        )
        time_blocks.append(time_block)
        db.session.add(time_block)

    # 提交任务以获取ID
    db.session.flush()

    # 创建番茄钟会话
    pomodoro_sessions = []
    session_data = [
        {
            'task_id': tasks[0].id,
            'session_type': SessionType.FOCUS,
            'planned_duration': 25,
            'is_completed': True,
            'actual_duration': 23
        },
        {
            'task_id': tasks[0].id,
            'session_type': SessionType.BREAK,
            'planned_duration': 5,
            'is_completed': True,
            'actual_duration': 5
        },
        {
            'task_id': tasks[1].id,
            'session_type': SessionType.FOCUS,
            'planned_duration': 25,
            'is_in_progress': True,
            'actual_duration': 15
        }
    ]

    for data in session_data:
        session = PomodoroSession(
            task_id=data['task_id'],
            user_id=test_user.id,
            planned_duration=data['planned_duration'],
            session_type=data['session_type']
        )

        # 根据测试数据设置状态
        if data.get('is_completed'):
            session.status = SessionStatus.COMPLETED
            session.actual_duration = data['actual_duration']
            session.start_time = datetime.now() - timedelta(hours=2)
            session.end_time = session.start_time + timedelta(minutes=data['actual_duration'])
        elif data.get('is_in_progress'):
            session.status = SessionStatus.IN_PROGRESS
            session.start_time = datetime.now() - timedelta(minutes=data['actual_duration'])
            session.actual_duration = data['actual_duration']
        else:
            session.created_at = datetime.now() - timedelta(hours=2)

        pomodoro_sessions.append(session)
        db.session.add(session)

    db.session.commit()

    return {
        'tasks': tasks,
        'time_blocks': time_blocks,
        'pomodoro_sessions': pomodoro_sessions,
        'category': category,
        'project': project
    }


class TestProductivityDataAPI:
    """生产力分析数据API测试类"""

    def test_get_tasks_for_productivity_analysis(self, client, auth_headers, sample_data):
        """测试获取任务数据用于生产力分析"""
        response = client.get('/api/tasks/', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)

        # 验证返回结构
        assert 'tasks' in data
        assert 'count' in data
        assert len(data['tasks']) == 3

        # 验证任务数据完整性
        tasks = data['tasks']
        completed_tasks = [t for t in tasks if t['status'] == 'COMPLETED']
        in_progress_tasks = [t for t in tasks if t['status'] == 'IN_PROGRESS']
        pending_tasks = [t for t in tasks if t['status'] == 'PENDING']

        assert len(completed_tasks) == 1
        assert len(in_progress_tasks) == 1
        assert len(pending_tasks) == 1

        # 验证生产力分析相关字段
        for task in tasks:
            assert 'title' in task
            assert 'status' in task
            assert 'priority' in task
            assert 'task_type' in task
            assert 'estimated_pomodoros' in task
            assert 'planned_start_time' in task
            assert 'created_at' in task

    def test_get_tasks_with_status_filter(self, client, auth_headers, sample_data):
        """测试按状态过滤任务"""
        # 测试获取已完成的任务
        response = client.get('/api/tasks/?status=COMPLETED', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['status'] == 'COMPLETED'

        # 测试获取进行中的任务
        response = client.get('/api/tasks/?status=IN_PROGRESS', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['status'] == 'IN_PROGRESS'

    def test_get_pomodoro_sessions_for_productivity_analysis(self, client, auth_headers, sample_data):
        """测试获取番茄钟会话数据用于生产力分析"""
        response = client.get('/api/pomodoro-sessions/', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)

        # 验证返回结构
        assert 'pomodoro_sessions' in data
        sessions = data['pomodoro_sessions']
        assert len(sessions) == 3

        # 验证会话数据完整性
        completed_sessions = [s for s in sessions if s['status'] == 'COMPLETED']
        in_progress_sessions = [s for s in sessions if s['status'] == 'IN_PROGRESS']

        assert len(completed_sessions) == 2
        assert len(in_progress_sessions) == 1

        # 验证生产力分析相关字段
        for session in sessions:
            assert 'task_id' in session
            assert 'session_type' in session
            assert 'status' in session
            assert 'planned_duration' in session
            assert 'actual_duration' in session
            assert 'created_at' in session

    def test_get_pomodoro_sessions_with_date_filter(self, client, auth_headers, sample_data):
        """测试按日期过滤番茄钟会话"""
        today = datetime.now().date().isoformat()
        response = client.get(f'/api/pomodoro-sessions/?date={today}', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'pomodoro_sessions' in data
        assert len(data['pomodoro_sessions']) == 3

    def test_get_time_blocks_for_productivity_analysis(self, client, auth_headers, sample_data):
        """测试获取时间块数据用于生产力分析"""
        response = client.get('/api/time-blocks/', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)

        # 验证返回结构
        assert isinstance(data, list)
        assert len(data) == 5

        # 验证时间块数据完整性
        active_blocks = [b for b in data if b['is_active']]
        inactive_blocks = [b for b in data if not b['is_active']]

        assert len(active_blocks) == 4
        assert len(inactive_blocks) == 1

        # 验证生产力分析相关字段
        for block in data:
            assert 'date' in block
            assert 'start_time' in block
            assert 'end_time' in block
            assert 'block_type' in block
            assert 'is_active' in block
            assert 'duration' in block

    def test_get_time_blocks_with_date_filter(self, client, auth_headers, sample_data):
        """测试按日期过滤时间块"""
        today = datetime.now().date().isoformat()
        response = client.get(f'/api/time-blocks/?date={today}', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 5

    def test_get_active_pomodoro_session(self, client, auth_headers, sample_data):
        """测试获取活跃番茄钟会话"""
        response = client.get('/api/pomodoro-sessions/active', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)

        # 验证有活跃会话
        assert 'active_session' in data
        assert data['active_session']['status'] == 'IN_PROGRESS'

    def test_task_creation_for_productivity_tracking(self, client, auth_headers, sample_data):
        """测试创建任务用于生产力跟踪"""
        task_data = {
            'title': '新生产力测试任务',
            'description': '用于测试生产力跟踪的任务',
            'category_id': sample_data['category'].id,
            'project_id': sample_data['project'].id,
            'priority': 'HIGH',
            'task_type': 'RIGID',
            'estimated_pomodoros': 2,
            'planned_start_time': (datetime.now() + timedelta(hours=1)).isoformat()
        }

        response = client.post('/api/tasks/',
                             headers=auth_headers,
                             data=json.dumps(task_data))

        assert response.status_code == 201
        data = json.loads(response.data)

        # 验证任务创建成功且包含生产力分析所需字段
        assert 'task' in data
        task = data['task']
        assert task['title'] == task_data['title']
        assert task['priority'] == 'HIGH'
        assert task['task_type'] == 'RIGID'
        assert task['estimated_pomodoros'] == 2

    def test_pomodoro_session_creation_for_productivity_tracking(self, client, auth_headers, sample_data):
        """测试创建番茄钟会话用于生产力跟踪"""
        session_data = {
            'task_id': sample_data['tasks'][0].id,
            'planned_duration': 30,
            'session_type': 'FOCUS'
        }

        response = client.post('/api/pomodoro-sessions/',
                             headers=auth_headers,
                             data=json.dumps(session_data))

        assert response.status_code == 201
        data = json.loads(response.data)

        # 验证会话创建成功
        assert 'pomodoro_session' in data
        session = data['pomodoro_session']
        assert session['task_id'] == sample_data['tasks'][0].id
        assert session['planned_duration'] == 30
        assert session['session_type'] == 'FOCUS'
        assert session['status'] == 'PENDING'

    def test_time_block_creation_for_productivity_tracking(self, client, auth_headers, sample_data):
        """测试创建时间块用于生产力跟踪"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        start_time = datetime.combine(tomorrow, datetime.min.time()).replace(hour=10)
        end_time = start_time + timedelta(hours=2)

        block_data = {
            'date': tomorrow.isoformat(),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'block_type': 'RESEARCH',
            'color': '#52c41a'
        }

        response = client.post('/api/time-blocks/',
                             headers=auth_headers,
                             data=json.dumps(block_data))

        assert response.status_code == 201
        data = json.loads(response.data)

        # 验证时间块创建成功
        assert 'time_block' in data
        block = data['time_block']
        assert block['block_type'] == 'RESEARCH'
        assert block['duration'] == 120  # 2小时 = 120分钟


class TestProductivityMetricsCalculation:
    """生产力指标计算测试类"""

    def test_task_completion_rate_calculation(self, client, auth_headers, sample_data):
        """测试任务完成率计算"""
        # 获取所有任务
        response = client.get('/api/tasks/', headers=auth_headers)
        data = json.loads(response.data)
        tasks = data['tasks']

        # 计算完成率
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t['status'] == 'COMPLETED'])
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

        # 验证计算结果
        assert completion_rate == 33.33333333333333  # 1/3 * 100
        assert total_tasks == 3
        assert completed_tasks == 1

    def test_pomodoro_efficiency_calculation(self, client, auth_headers, sample_data):
        """测试番茄钟效率计算"""
        # 获取番茄钟会话
        response = client.get('/api/pomodoro-sessions/', headers=auth_headers)
        data = json.loads(response.data)
        sessions = data['pomodoro_sessions']

        # 计算效率指标
        focus_sessions = [s for s in sessions if s['session_type'] == 'FOCUS']
        completed_sessions = [s for s in focus_sessions if s['status'] == 'COMPLETED']

        if completed_sessions:
            total_planned = sum(s['planned_duration'] for s in completed_sessions)
            total_actual = sum(s['actual_duration'] for s in completed_sessions)
            efficiency = (total_actual / total_planned) * 100 if total_planned > 0 else 0

            # 验证效率计算
            assert 0 <= efficiency <= 200  # 效率应该在合理范围内
            assert total_planned == 25  # 只有一个完成的专注会话
            assert total_actual == 23

    def test_time_utilization_calculation(self, client, auth_headers, sample_data):
        """测试时间利用率计算"""
        # 获取时间块
        response = client.get('/api/time-blocks/', headers=auth_headers)
        data = json.loads(response.data)
        time_blocks = data

        # 计算时间利用率
        total_blocks = len(time_blocks)
        active_blocks = len([b for b in time_blocks if b['is_active']])
        utilization = (active_blocks / total_blocks) * 100 if total_blocks > 0 else 0

        # 验证计算结果
        assert utilization == 80.0  # 4/5 * 100
        assert total_blocks == 5
        assert active_blocks == 4

    def test_productivity_data_integration(self, client, auth_headers, sample_data):
        """测试生产力数据集成"""
        # 获取所有相关数据
        tasks_response = client.get('/api/tasks/', headers=auth_headers)
        sessions_response = client.get('/api/pomodoro-sessions/', headers=auth_headers)
        blocks_response = client.get('/api/time-blocks/', headers=auth_headers)

        tasks_data = json.loads(tasks_response.data)
        sessions_data = json.loads(sessions_response.data)
        blocks_data = json.loads(blocks_response.data)

        # 验证数据一致性
        assert len(tasks_data['tasks']) == 3
        assert len(sessions_data['pomodoro_sessions']) == 3
        assert len(blocks_data) == 5

        # 验证时间戳格式一致性
        for task in tasks_data['tasks']:
            assert 'created_at' in task
            assert 'planned_start_time' in task

        for session in sessions_data['pomodoro_sessions']:
            assert 'created_at' in session

        for block in blocks_data:
            assert 'date' in block
            assert 'start_time' in block
            assert 'end_time' in block


if __name__ == '__main__':
    pytest.main([__file__, '-v'])