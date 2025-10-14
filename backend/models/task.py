from . import BaseModel, db
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from typing import Dict, Any, Optional
import enum


class TaskType(enum.Enum):
    """任务类型枚举"""
    RIGID = 'RIGID'      # 刚性任务
    FLEXIBLE = 'FLEXIBLE'  # 柔性任务


class TaskStatus(enum.Enum):
    """任务状态枚举"""
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'


class PriorityLevel(enum.Enum):
    """优先级枚举"""
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'


class Task(BaseModel):
    """任务模型"""
    __tablename__ = 'tasks'

    title = db.Column(String(200), nullable=False)
    description = db.Column(Text)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False)

    # 时间属性
    planned_start_time = db.Column(DateTime, nullable=False)
    estimated_pomodoros = db.Column(Integer, default=1)
    task_type = db.Column(Enum(TaskType), nullable=False)

    # 分类与排布
    category_id = db.Column(String(36), ForeignKey('task_categories.id'), nullable=False)
    scheduled_time_block_id = db.Column(String(36), ForeignKey('time_blocks.id'))

    # 状态管理
    status = db.Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = db.Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)

    # 项目关联
    project_id = db.Column(String(36), ForeignKey('projects.id'))

    # 关联关系
    user = relationship('User', back_populates='tasks')
    category = relationship('TaskCategory', back_populates='tasks')
    scheduled_time_block = relationship('TimeBlock', back_populates='scheduled_tasks')
    project = relationship('Project', back_populates='tasks')
    tags = relationship('Tag', secondary='task_tags', back_populates='tasks')
    pomodoro_sessions = relationship('PomodoroSession', back_populates='task', cascade='all, delete-orphan')
    # time_logs = relationship('TimeLog', back_populates='task', cascade='all, delete-orphan')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'planned_start_time': self.planned_start_time.isoformat() if self.planned_start_time else None,
            'estimated_pomodoros': self.estimated_pomodoros,
            'task_type': self.task_type.value,
            'category_id': self.category_id,
            'scheduled_time_block_id': self.scheduled_time_block_id,
            'status': self.status.value,
            'priority': self.priority.value,
            'project_id': self.project_id
        })
        return base_dict