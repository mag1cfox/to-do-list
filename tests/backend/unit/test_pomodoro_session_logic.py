#!/usr/bin/env python3
"""
PomodoroSession逻辑测试 - 完全独立，不依赖数据库
"""

import pytest
from datetime import datetime, timedelta

class SessionStatus:
    """会话状态枚举"""
    PLANNED = 'PLANNED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    INTERRUPTED = 'INTERRUPTED'

class SessionType:
    """会话类型枚举"""
    FOCUS = 'FOCUS'
    BREAK = 'BREAK'

class MockPomodoroSession:
    """模拟PomodoroSession类，用于逻辑测试"""

    def __init__(self, task_id, user_id, planned_duration=25, session_type=SessionType.FOCUS):
        self.task_id = task_id
        self.user_id = user_id
        self.planned_duration = planned_duration
        self.session_type = session_type
        self.status = SessionStatus.PLANNED
        self.start_time = None
        self.end_time = None
        self.actual_duration = None
        self.completion_summary = None
        self.interruption_reason = None

    def start(self):
        """开始番茄钟会话"""
        if self.status != SessionStatus.PLANNED:
            raise ValueError("只能从PLANNED状态开始会话")

        self.status = SessionStatus.IN_PROGRESS
        self.start_time = datetime.utcnow()

    def complete(self, summary=None):
        """完成番茄钟会话"""
        if self.status != SessionStatus.IN_PROGRESS:
            raise ValueError("只能从IN_PROGRESS状态完成会话")

        self.status = SessionStatus.COMPLETED
        self.end_time = datetime.utcnow()
        self.completion_summary = summary

        # 计算实际持续时间
        if self.start_time and self.end_time:
            duration_seconds = (self.end_time - self.start_time).total_seconds()
            self.actual_duration = int(duration_seconds / 60)  # 转换为分钟

    def interrupt(self, reason=None):
        """中断番茄钟会话"""
        if self.status != SessionStatus.IN_PROGRESS:
            raise ValueError("只能从IN_PROGRESS状态中断会话")

        self.status = SessionStatus.INTERRUPTED
        self.end_time = datetime.utcnow()
        self.interruption_reason = reason

        # 计算实际持续时间
        if self.start_time and self.end_time:
            duration_seconds = (self.end_time - self.start_time).total_seconds()
            self.actual_duration = int(duration_seconds / 60)  # 转换为分钟

    def get_remaining_time(self):
        """获取剩余时间（秒）"""
        if self.status != SessionStatus.IN_PROGRESS:
            return 0

        if not self.start_time:
            return self.planned_duration * 60

        elapsed_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        remaining_seconds = max(0, self.planned_duration * 60 - elapsed_seconds)
        return int(remaining_seconds)

    def is_active(self):
        """检查会话是否活跃"""
        return self.status == SessionStatus.IN_PROGRESS

    def to_dict(self):
        """转换为字典格式"""
        return {
            'task_id': self.task_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'planned_duration': self.planned_duration,
            'actual_duration': self.actual_duration,
            'status': self.status,
            'session_type': self.session_type,
            'completion_summary': self.completion_summary,
            'interruption_reason': self.interruption_reason,
            'is_active': self.is_active(),
            'remaining_time': self.get_remaining_time()
        }

class TestPomodoroSessionLogic:
    """PomodoroSession逻辑测试"""

    def test_pomodoro_session_creation(self):
        """测试番茄钟会话创建功能"""
        session = MockPomodoroSession(
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
        session = MockPomodoroSession(task_id=1, user_id=1)

        session.start()

        assert session.status == SessionStatus.IN_PROGRESS
        assert session.start_time is not None
        assert session.is_active() is True

    def test_pomodoro_session_complete(self):
        """测试番茄钟会话完成功能"""
        session = MockPomodoroSession(task_id=1, user_id=1)
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
        session = MockPomodoroSession(task_id=1, user_id=1)
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
        session = MockPomodoroSession(task_id=1, user_id=1, planned_duration=25)

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
        session = MockPomodoroSession(
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

    def test_pomodoro_session_status_validation(self):
        """测试状态流转验证"""
        session = MockPomodoroSession(task_id=1, user_id=1)

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
        session = MockPomodoroSession(
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
        session = MockPomodoroSession(task_id=1, user_id=1, planned_duration=25)
        session.start()

        # 设置开始时间为25分钟前
        session.start_time = datetime.utcnow() - timedelta(minutes=25)
        session.complete()

        assert session.actual_duration == 25

        # 测试部分时间
        session2 = MockPomodoroSession(task_id=2, user_id=1, planned_duration=25)
        session2.start()
        session2.start_time = datetime.utcnow() - timedelta(minutes=18, seconds=30)
        session2.complete()

        assert session2.actual_duration == 18  # 向下取整