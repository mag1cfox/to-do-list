from . import BaseModel, db
from datetime import datetime
from sqlalchemy import Enum as SQLAlchemyEnum
import enum

class SessionStatus(enum.Enum):
    PLANNED = 'PLANNED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    INTERRUPTED = 'INTERRUPTED'

class SessionType(enum.Enum):
    FOCUS = 'FOCUS'
    BREAK = 'BREAK'

class PomodoroSession(BaseModel):
    __tablename__ = 'pomodoro_sessions'

    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # 时间追踪
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    planned_duration = db.Column(db.Integer, nullable=False, default=25)  # 默认25分钟
    actual_duration = db.Column(db.Integer)  # 实际持续时间（分钟）

    # 状态
    status = db.Column(SQLAlchemyEnum(SessionStatus), nullable=False, default=SessionStatus.PLANNED)
    session_type = db.Column(SQLAlchemyEnum(SessionType), nullable=False, default=SessionType.FOCUS)

    # 复盘数据
    completion_summary = db.Column(db.Text)
    interruption_reason = db.Column(db.Text)

    # 关联
    task = db.relationship('Task', back_populates='pomodoro_sessions')
    user = db.relationship('User', back_populates='pomodoro_sessions')

    def __init__(self, task_id, user_id, planned_duration=25, session_type=SessionType.FOCUS):
        self.task_id = task_id
        self.user_id = user_id
        self.planned_duration = planned_duration
        self.session_type = session_type
        self.status = SessionStatus.PLANNED
        self.start_time = datetime.utcnow()

    def start(self):
        """开始番茄钟会话"""
        if self.status != SessionStatus.PLANNED:
            raise ValueError("只能从PLANNED状态开始会话")

        self.status = SessionStatus.IN_PROGRESS
        self.start_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()

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

        self.updated_at = datetime.utcnow()

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

        self.updated_at = datetime.utcnow()

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
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'planned_duration': self.planned_duration,
            'actual_duration': self.actual_duration,
            'status': self.status.value,
            'session_type': self.session_type.value,
            'completion_summary': self.completion_summary,
            'interruption_reason': self.interruption_reason,
            'is_active': self.is_active(),
            'remaining_time': self.get_remaining_time(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<PomodoroSession {self.id} - {self.status.value} - {self.session_type.value}>'