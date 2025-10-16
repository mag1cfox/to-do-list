#!/usr/bin/env python3
"""
独立番茄钟会话模型测试 - 不依赖models/__init__.py
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 创建独立数据库配置
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 导入模型类并重新定义以使用独立数据库
from backend.models.pomodoro_session import PomodoroSession as OriginalPomodoroSession, SessionStatus, SessionType

class PomodoroSession(OriginalPomodoroSession):
    """使用独立数据库的PomodoroSession类"""
    pass

PomodoroSession.metadata = db.metadata

class TestPomodoroSessionStandalone:
    """PomodoroSession模型独立测试"""

    def test_pomodoro_session_creation(self):
        """测试番茄钟会话创建功能"""
        session = PomodoroSession(
            task_id=1,
            user_id=1,
            planned_duration=30,
            session_type=SessionType.FOCUS
        )

        assert session.task_id == 1
        assert session.user_id == 1
        assert session.planned_duration == 30
        assert session.session_type == SessionType.FOCUS
        assert session.status == SessionStatus.PLANNED
        assert session.start_time is None
        assert session.end_time is None
        assert session.actual_duration is None

    def test_pomodoro_session_start(self):
        """测试番茄钟会话开始功能"""
        session = PomodoroSession(task_id=1, user_id=1)

        session.start()

        assert session.status == SessionStatus.IN_PROGRESS
        assert session.start_time is not None
        assert session.is_active() is True

    def test_pomodoro_session_complete(self):
        """测试番茄钟会话完成功能"""
        session = PomodoroSession(task_id=1, user_id=1)
        session.start()

        # 模拟时间流逝
        session.start_time = datetime.utcnow() - timedelta(minutes=20)

        session.complete("任务完成")

        assert session.status == SessionStatus.COMPLETED
        assert session.end_time is not None
        assert session.completion_summary == "任务完成"
        assert session.actual_duration == 20
        assert session.is_active() is False

    def test_pomodoro_session_interrupt(self):
        """测试番茄钟会话中断功能"""
        session = PomodoroSession(task_id=1, user_id=1)
        session.start()

        # 模拟时间流逝
        session.start_time = datetime.utcnow() - timedelta(minutes=15)

        session.interrupt("紧急情况")

        assert session.status == SessionStatus.INTERRUPTED
        assert session.end_time is not None
        assert session.interruption_reason == "紧急情况"
        assert session.actual_duration == 15
        assert session.is_active() is False

    def test_pomodoro_session_remaining_time(self):
        """测试剩余时间计算功能"""
        session = PomodoroSession(task_id=1, user_id=1, planned_duration=25)

        # 未开始的会话
        assert session.get_remaining_time() == 0

        # 已开始的会话
        session.start()
        session.start_time = datetime.utcnow() - timedelta(minutes=10)

        remaining_time = session.get_remaining_time()
        assert remaining_time > 0
        assert remaining_time <= 15 * 60  # 15分钟转换为秒

    def test_pomodoro_session_to_dict(self):
        """测试字典转换功能"""
        session = PomodoroSession(
            task_id=1,
            user_id=1,
            planned_duration=25,
            session_type=SessionType.FOCUS
        )

        session_dict = session.to_dict()

        assert session_dict['task_id'] == 1
        assert session_dict['user_id'] == 1
        assert session_dict['planned_duration'] == 25
        assert session_dict['status'] == 'PLANNED'
        assert session_dict['session_type'] == 'FOCUS'
        assert session_dict['is_active'] is False
        assert session_dict['remaining_time'] == 0
        assert 'created_at' in session_dict
        assert 'updated_at' in session_dict

    def test_pomodoro_session_status_validation(self):
        """测试状态流转验证"""
        session = PomodoroSession(task_id=1, user_id=1)

        # 不能从未开始状态直接完成
        with pytest.raises(ValueError, match="只能从IN_PROGRESS状态完成会话"):
            session.complete()

        # 不能从未开始状态直接中断
        with pytest.raises(ValueError, match="只能从IN_PROGRESS状态中断会话"):
            session.interrupt()

        # 正常流转
        session.start()
        session.complete()

        # 不能从完成状态重新开始
        with pytest.raises(ValueError, match="只能从PLANNED状态开始会话"):
            session.start()

    def test_pomodoro_session_break_type(self):
        """测试休息类型会话"""
        session = PomodoroSession(
            task_id=1,
            user_id=1,
            planned_duration=5,
            session_type=SessionType.BREAK
        )

        assert session.session_type == SessionType.BREAK
        assert session.planned_duration == 5

        session_dict = session.to_dict()
        assert session_dict['session_type'] == 'BREAK'

    def test_pomodoro_session_duration_calculation(self):
        """测试持续时间计算"""
        session = PomodoroSession(task_id=1, user_id=1, planned_duration=25)
        session.start()

        # 设置开始时间为25分钟前
        session.start_time = datetime.utcnow() - timedelta(minutes=25)
        session.complete()

        assert session.actual_duration == 25

        # 测试部分时间
        session2 = PomodoroSession(task_id=2, user_id=1, planned_duration=25)
        session2.start()
        session2.start_time = datetime.utcnow() - timedelta(minutes=18, seconds=30)
        session2.complete()

        assert session2.actual_duration == 18  # 向下取整